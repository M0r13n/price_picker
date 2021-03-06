import os
import sentry_sdk
import datetime as dt
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from price_picker.common.next_page import next_page
from price_picker.common.url_for_other_page import url_for_other_page
from config import configs
from flask_bootstrap import Bootstrap
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from price_picker.analytics import Analytics
from celery import Celery
from redis import Redis
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# instantiate the extensions
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
csrf = CSRFProtect()
celery = Celery()
talisman = Talisman()
analytics = Analytics()
r = Redis()


def create_app(config=None, script_info=None):
    # instantiate the app
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="../assets/static",
        instance_relative_config=True
    )
    conf = os.getenv("APP_CONFIG", "DEFAULT")
    config = config or configs[conf]
    app.config.from_object(config)

    init_talisman(app)
    init_extensions(app)
    register_blueprints(app)
    init_flask_login(app)
    register_error_handlers(app)
    add_jinja_vars(app)
    init_celery(app)
    init_sentry(app)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        from price_picker.models import User, Device, Repair, Manufacturer
        return {"app": app, "db": db, 'User': User, 'Repair': Repair, 'Manufacturer': Manufacturer, 'Device': Device}

    return app


def register_error_handlers(app):
    """ Register custom Error Handlers here """

    @app.errorhandler(401)
    def unauthorized_page(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500


def init_flask_login(app):
    """ Flask Login Setup """

    from price_picker.models import User
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "danger"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()


def init_talisman(app):
    csp = {
        'default-src': [
            '\'self\''
        ],
        'style-src': [
            '\'self\'',
            'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
        ],
        'script-src': [
            '\'self\'',
            'https://d3js.org/d3.v3.min.js',
            'https://code.jquery.com/jquery-3.4.1.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js',
            'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js'
        ]
    }
    talisman.init_app(app,
                      content_security_policy=csp,
                      content_security_policy_nonce_in=['script-src'])


def register_blueprints(app):
    """ Register all Blueprints here """
    from price_picker.views.main.views import main_blueprint
    from price_picker.views.admin.views import admin_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)


def init_extensions(app):
    """ Register all Extensions here """

    login_manager.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    analytics.init_app(app, blueprints=['main', ], redis_url=app.config['REDIS_URL'])
    r = Redis.from_url(app.config['REDIS_URL'])


def add_jinja_vars(app):
    def unix2date(value, format='%H:%M / %d-%m-%Y'):
        """
        convert a unix timestamp to datetime
        """
        try:
            return dt.datetime.utcfromtimestamp(value).strftime(format)
        except Exception:
            pass

    app.jinja_env.filters['unix2date'] = unix2date
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page


def init_sentry(app):
    if 'DSN' in app.config.keys():
        sentry_sdk.init(
            dsn=app.config['DSN'],
            integrations=[FlaskIntegration(), CeleryIntegration()]
        )


def init_celery(app=None):
    app = app or create_app()
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
