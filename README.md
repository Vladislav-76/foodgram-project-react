## Проект: Foodgram - Продуктовый помошник

![Status of workflow runs triggered by the push event](https://github.com/Vladislav-76/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)

## Адрес
http://158.160.24.226

Вход в админку:
username: 'admin@test.com'
password: '123'

## Описание
В этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов, необходимых для приготовления выбранных блюд.

![Main Web-Page View]()

![Recipe View]()


***
## Workflow
Запускается при пуше в `master`

Задачи:

`tests`: устанавливает зависимости, запускает flake8

`build_and_push_foodgram_backend_to_docker_hub`: создает образ foodgram_backend и отправляет на DockerHub

`build_and_push_foodgram_frontend_to_docker_hub`: создает образ foodgram_frontend и отправляет на DockerHub

`deploy`: деплой проекта на удаленный сервер

***
### Подготовка и запуск проекта

***
Клонируйте репозиторий:

```
git clone https://github.com/Vladislav-76/foodgram-project-react/
```

***
Создайте файл переменных окружения .env и заполните его.
Разместите .env файл на сервере.
***
Пример .env

```
SECRET_KEY = #=5s%lu*7d8ht%vo_s&+s2
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=12345
DB_HOST=127.0.0.1
DB_PORT=5432
```

***
### Установка на удаленный сервер (Ubuntu):
1\. Подключитесь к серверу:

```
ssh <your_login>@<ip_address>
```

2\. Установите Docker на сервер:

```
sudo apt install docker.io
```

3\. Установите docker-compose на сервер:
 - Следующая команда скачает версию 2.12.2 и сохранит файлы в `/usr/local/bin/docker-compose`, что позволит глобально обращаться к `docker-compose`:

```
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

- Установите права для docker-compose:

```
sudo chmod +x /usr/local/bin/docker-compose
```

- Прверьте установку:

```
docker-compose --version
```

Docker Compose version v2.12.2
```

4\. Скопируйте файлы `infra/docker-compose.yaml` и `infra/nginx.conf` на удаленный сервер в `home/<your_username>/.env`, `home/<your_username>/docker-compose.yaml` и `home/<your_username>/nginx.conf`

```
scp infra/docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp -r infra/nginx.conf <username>@<host>:/home/<username>/nginx.conf
```

5\. Добавьте переменные окружения в Secrets на GitHub:

```
DOCKER_USERNAME=<<<<<<username DockerHub>>>
DOCKER_PASSWORD=<<<password DockerHub>>>
USER=<<<username remote server>>>
HOST=<<<IP-address of remote server>>>
SSH_KEY=<<<SSH private key можно получить: cat ~/.ssh/id_rsa>>>
```

***
### После деплоя

На удаленном сервере делаем миграции, содаем superuser, собираем статику:

```
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

***
```
Проект будет доступен по адресу: `http://<IP-address of remote server>/`
Админка: `http://<IP-address of remote server>/admin/`
Документация: `http://<IP-address of remote server>/api/docs/`
```
