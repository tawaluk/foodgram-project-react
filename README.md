
# Дипломный проект Foodgram

    Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты,
    добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
    Пользователям сайта также доступен сервис «Список покупок».
    Он позволяет создавать список продуктов,
    которые нужно купить для приготовления выбранных блюд.


## Skills

    Python 3.11, Django 4.2, DRF 3.14, Docker,
    GitHub Actions, Postman (API-tests), bash


## Исходные данные

    Готовый frontend, и коллекция тестов Postman, файлы спецификации API, ТЗ



## Описание выполненной работы

Проект состоит из следующих страниц: 

    главная,
    страница рецепта,
    страница пользователя,
    страница подписок,
    избранное,
    список покупок,
    создание и редактирование рецепта.

Главная 

    Содержимое главной — список первых шести рецептов,
    отсортированных по дате  публикации «от новых к старым».
    На этой странице нужно реализована постраничная пагинация.
    Остальные рецепты доступны на следующих страницах.

Страница рецепта

    Здесь — полное описание рецепта.
    У авторизованных пользователей есть возможность добавить рецепт
    в избранное и список покупок, а также подписаться на автора рецепта.

Страница пользователя

    На странице — имя пользователя, все рецепты, опубликованные пользователем
    и возможность подписаться на пользователя.

Страница подписок

    Только у владельца аккаунта есть возможность просмотреть свою страницу
    подписок.
    Подписаться на публикации могут только авторизованные пользователи.

Избранное

    Добавлять рецепты в избранное может только авторизованный пользователь.
    Сам список избранного может просмотреть только его владелец.

Список покупок

    Работа со списком покупок доступна только авторизованным пользователям.
    Доступ к своему списку покупок есть только у владельца аккаунта.
    Есть возможность скачать список покупок в формате .txt





## Основы работы с проектом

    Для работы с проектом необходимо иметь на вашем ПК:

    доступ в Сеть и развернутый Docker.

Склонируем репозиторий:

    git clone git@github.com:tawaluk/foodgram-project-react.git

Теперь у Вас есть актуальная версия репозитория и вы можете при желании 
запускать как отдельные контейнеры с помощью докер-файлов в соответсвующих директориях, так и многоступенчатые сборки, при желании изменяя сами докер-образы.



## Особенности

шлюз

    Обратите особое внимание на конфигурацию nginx в зависимости от локации 
    развертывания проекта.
    В проекте имеются 2 nginx файла с конфигурациями,
    в которых учтены особенности развертывания как локально так и удаленно.

backend

    Обратите внимание на взаимную поддержку пакетов и библиотек,
    корнем проекта является взаимосвязь django 4.2 / Python 3.11

frontend

    Локально у меня получилось запустить фронтенд, только через docker.

База данных

    Локально для тестов рекомендую использовать SQLite3.
    Так Вам будет гораздо удобнее рефакторить код исходя
    из удобства видимости результата Ваших дейсвтий в БД.
    Для полноценного проекта лучше использовать PostgreSQL.
    В примере работы реализован PostgreSQL из контейнера DockerHub
    image: postgres:13.0-alpine.
    ВАЖНО! Учтите поддержку версии ОС версии PostgreSQL


## FAQ

### Судя по терминальному ответу docker, проект развернут, но ничего не работает:

В первую очередь включите режим DEBUG в Django.
Дальнейшие действия зависят от ответа Django (см. в веб-браузере)

### Не прогружается статика:

Проверьте, выполнили ли Вы сбор статики?  

    python3 ma[manage.py](backend%2Fmanage.py)nage.py collectstatic

Далее проверте, где статик файлы ожидает увидеть nginx и Djangо

###  После изменений, связанных с API-запросами или связанных с моделями, не запускается Django:

Возможно необходимо проверить поля связанной модели БД и удалить volumes БД

## Support

При необходимости пишите мне на электронную почту

    tawaluk@yandex.ru

## Reviews

Host:

    workexampletavalyuk.ru

Админ:

    почта/логин - admin@admin.ru
    пароль - 1admintest



