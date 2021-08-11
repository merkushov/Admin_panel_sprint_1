# Каталог фильмов

## Как работать с Проектом

```shell
# Скачать код
$ git clone git@github.com:merkushov/Admin_panel_sprint_1.git
$ cd Admin_panel_sprint_1

# (devel) Развернуть код в контейнерах Докер
$ cp movies_admin/.env.example movies_admin/.env
$ docker-compose up -d --build

# (production) Развернуть код в контейнерах Докер
$ cp movies_admin/.env.example movies_admin/.env
$ docker-compose -f docker-compose.prod.yaml up -d --build
```