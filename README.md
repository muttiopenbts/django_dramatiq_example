# django_dramatiq_example

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

An example app demonstrating [django_dramatiq][django_dramatiq].


## Setup

* Clone the repo, then run 
```pipenv install```.
* Run [Redis][redis].
* Run the web server: ```python manage.py runserver```
* Run the workers: ```python manage.py rundramatiq```


## License

django_dramatiq_example is licensed under Apache 2.0.  Please see
[LICENSE][license] for licensing details.


[django_dramatiq]: https://github.com/Bogdanp/django_dramatiq
[redis]: https://redis.io
[license]: https://github.com/Bogdanp/django_dramatiq_example/blob/master/LICENSE
