# django_dramatiq_example

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

An example app demonstrating [django_dramatiq][django_dramatiq].

This example app is designed to accept OS commands from the http service and execute them on an agent.
The user submitting the os command must digitally sign the request with a private key, which the corresponding public key in the app will verify the message.

## Setup
### Services
* rabbitmq  
```
sudo apt install rabbitmq-server
rabbitmq-server -detached
```
### Code
* Clone the repo, then run   
```pipenv install```
* Run [Redis][redis].
### Web
* Run the web server:  
```python manage.py runserver```
* Run the workers(agents):  
```python manage.py rundramatiq```

## Test
* Generate rsa key pairs  
```
% openssl genrsa -out ~/cascade_2048_rsa.private 2048
% openssl rsa -in ~/cascade_2048_rsa.private -out ~/cascade_2048_rsa.pub -pubout -outform PEM

```

## License

django_dramatiq_example is licensed under Apache 2.0.  Please see
[LICENSE][license] for licensing details.


[django_dramatiq]: https://github.com/Bogdanp/django_dramatiq
[redis]: https://redis.io
[license]: https://github.com/Bogdanp/django_dramatiq_example/blob/master/LICENSE
