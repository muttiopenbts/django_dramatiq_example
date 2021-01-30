# django_dramatiq_example

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

An example app demonstrating [django_dramatiq][django_dramatiq].

This example app is designed to accept OS commands from the http service and execute them on an agent.
The user submitting the os command must digitally sign the request with a private key, which the corresponding public key in the app will verify the message.

## Setup
### Services & Misc
* rabbitmq  
    Linux  
    ```
    sudo apt install rabbitmq-server
    rabbitmq-server -detached
    ```
    Macos  
    ```
    brew install rabbitmq
    brew services start rabbitmq
    ```
* pipenv  
```
python -m pip install pipenv
```
* postgresql   
```
brew install postgresql (macos)
```
* openssl  
    Might need to include openssl lib. 
    e.g.  
    ```
    export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"
    ```
### Code
* Clone the repo, then run  
```
git clone <REPO>
cd <REPO>
pipenv install
```
### Create Django user  
```
pipenv shell
export SECRET_KEY=“<SECRET_KEY>“
python manage.py migrate
python manage.py createsuperuser
<WEB_USERNAME>
<WEB_PASSWORD>
```

### Web
* Run the web server:  
```
pipenv shell
export SECRET_KEY=“<SECRET_KEY>“
export RABBIT_USER=“<NAME>" #guest
export RABBIT_PASS=“<PASSWORD>" #guest
python manage.py runserver
```
* Bower  
```
npm install -g bower
pipenv shell
export SECRET_KEY=“<SECRET_KEY>“
export RABBIT_USER=“<NAME>" #guest
export RABBIT_PASS=“<PASSWORD>" #guest
python manage.py bower install
python manage.py collectstatic
```
* Run the workers(agents):  
```
pipenv shell
export SECRET_KEY=“<SECRET_KEY>“
export RABBIT_USER=“<NAME>" #guest
export RABBIT_PASS=“<PASSWORD>" #guest
python manage.py rundramatiq
```

## Test
* Generate rsa key pairs  
```
% openssl genrsa -out ~/cascade_2048_rsa.private 2048
% openssl rsa -in ~/cascade_2048_rsa.private -out ~/cascade_2048_rsa.pub -pubout -outform PEM
```
* Sign the OS command  
```
% echo -n "uname" | openssl dgst -sha256 -sign ~/cascade_2048_rsa.private -out sha256_uname.sign
```
or  
```
echo -n "uname" | openssl dgst -sha256 -sign ~/cascade_2048_rsa.private| base64
```
* Verify the signature 
```
% echo -n "uname"|openssl dgst -sha256 -verify ~/cascade_2048_rsa.pub -signature sha256_uname.sign
```
* Prepare signature to submit to web app  
```
% base64 sha256_uname.sign
```
* API   
http://127.0.0.1:8000/schema/
* UI
http://127.0.0.1:8000/jobs/schema/?format=api

## License

django_dramatiq_example is licensed under Apache 2.0.  Please see
[LICENSE][license] for licensing details.


[django_dramatiq]: https://github.com/Bogdanp/django_dramatiq
[redis]: https://redis.io
[license]: https://github.com/Bogdanp/django_dramatiq_example/blob/master/LICENSE
