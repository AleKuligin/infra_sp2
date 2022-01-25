# api_yamdb

### Описание:
API сервиса YaMDB .
Документация API доступна по [ссылке](http://127.0.0.1:8000/redoc/)

### Как запустить проект:

##### 1. Клонировать репозиторий

```
git clone <адрес репозитория>
```

##### 2. При необходимости установить Docker

Инструкция для Linux

```
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

sudo apt update

sudo apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y 

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt update

sudo apt install docker-ce docker-compose -y
```

##### 3. Создать .env файл

env-файл необходимо создать по шаблону ниже и разместить в папку проекта api_yamdb (где лежит Dockerfile)

Имя пользователя, пароль и секретный ключ django нужно указать свои! 

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY= # секретный ключ django
```

##### 4. Запустить приложения в контейнерах
Запускается из места расположения файла docker-compose.yaml: /infra/
```
sudo docker-compose up -d --build
```

##### 5. Создать суперюзера и заполнить базу данными.

```
sudo docker-compose exec web python manage.py migrate

sudo docker-compose exec web python manage.py createsuperuser

sudo docker-compose exec web python manage.py collectstatic --no-input
```

##### 6. Использование приложения

После выполнения указаных шагов проект будет запущен в контейнере, раздел администрирования будет доступен в браузере по адресу http://127.0.0.1/admin/. 

При необходимости контейнеры можно остановить и заново запустить без потери данных следующими командами:

```
sudo docker-compose stop

sudo docker-compose start
```

Удалить контейнеры можно командой:

```
sudo docker-compose down -v 
```
