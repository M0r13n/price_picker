from price_picker import create_app
import os

app = create_app()

# WSGI ENTRY POINT
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
