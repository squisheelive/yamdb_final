# YaMDb API Docker infrastructure

#### В этом учебном проекте реализована инфраструктура [docker](https://www.docker.com/) контейнеризации API для небольшой социальной сети YaMDb.

В YaMDb пользователи могут писать рецензии к различным произведениям (книги, музыка, фильмы и т.д.), а также оставлять к рецензиям комментарии. Сами произведения в YaMDb не хранятся. 

### Документация к API.
Подробную документацию к API вы можете найти после запуска проекта по адресу http://localhost/redoc/

### Подготовка и запуск проекта:

- Клонировать репозиторий и перейти директорию `/infra`.

- Создать там файл `.env` со следующим содержимым:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

- Следует придумать свои имя пользователя и пароль для базы данных и заменить соответствующие значения `POSTGRES_USER` и `POSTGRES_PASSWORD`.

- Запустить контейнеризацию docker `docker-compose up`

- Выполнить миграции и собрать статику:

```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```

### Тестовые данные.

В проекте подготовленны тестовые данные, загрузить их в базу данных можно командой:

```
docker-compose exec web python manage.py loaddata fixtures.json
```

После чего можно будет попасть в админку проекта http://localhost/admin/
###### логин: `admin`
###### пароль: `admin`
