# This is now old

See https://github.com/M0r13n/Smartphoniker-shop

# price_picker
This project aims to provide a simple yet good-looking price overview for repairshops that offer various kinds of services around Smartphones and Tablets.

# Credit
All 'pictures' of smartphones are 100% pure CSS and taken from 
[this repo.](https://github.com/marvelapp/devices.css) All credit goes to them.

### Run this application with Docker
Build the docker image and start the containers.

```sh
$ docker-compose up -d --build
```

After that create the database.

Create the database:
-
```sh
$ docker-compose run web python manage.py create-db
$ docker-compose run web python manage.py db init
$ docker-compose run web python manage.py db migrate
$ docker-compose run web python manage.py create-admin
$ docker-compose run web python manage.py create-data
```

The App is now accessible at the address [http://localhost:5000/](http://localhost:5000/)

### Testing

Test without coverage:

```sh
$ docker-compose run web python manage.py test
```
