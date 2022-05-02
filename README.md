# foodgram
![Foodgram workflow](
https://github.com/ilart/foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg?branch=master
)

Проект Foodgram создан для любителей вкусно поесть. Здесь вы сможете делиться своими рецептами,
просматривать рецепты других пользователей и подписываться на любимых авторов. 
Данный проект включает в себя:
1. backend - api foodgram. Включает в себя весь функционал. 
Подробности можно узнать в [документации](http://51.250.81.3/api/docs/ "How to use API Foodgram")".
2. frontend - контейнер с готовым UI на базе React.
3. infra - Web сервер на базе Nginx.

### Как запустить проект
**Внимание, большинство операций требуют аутентификацию пользователя.**

1. Сделайте форк данного репозитория. В папке .github вы найдете готовый workflow
Создайте секреты в github actions. 
- DB_ENGINE
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DB_HOST
- DB_PORT
- SSH_HOST
- SSH_KEY
- SSH_USER 
2. Установите docker на сервер на котором планируется деплой.

```bash
sudo apt install docker.io 
```

4. Установите docker-compose, в этом вам поможет [официальная документация](https://docs.docker.com/compose/install/).

5. Скопируйте файлы ```docker-compose.yaml``` и ```nginx.conf``` из вашего 
проекта на сервер в ```/home/<ваш_username>/docker-compose.yaml``` и ```/home/<ваш_username>/nginx.conf``` соответственно.

6. Выполните git push на свой репозиторий. И убедитесь, что workflow завершился успешно.

7. Перейдите по адресу вашего сервера в браузере и убедитесь, что все работает.

8. Теперь проект готов.

9. Некоторые данные уже подгружены. Если захотите их удалить, просто выполните
```bash
docker-compose exec backend python3 ./manage.py flush
```

## Используемые технологии

| Technology     | Description                  | Link ↘️                        |
|----------------|------------------------------|--------------------------------|
| Django         | Фреймворк для веб-приложений | https://www.djangoproject.com/ |
| Python3        | Интерпретатор языка Python3  | https://www.python.org/        |
| Nginx          | HTTP сервер                  | https://www.nginx.com/         |
| Docker         | Платформа для контейнеризации | https://docker.com/            |
| GitHub Actions | CI/CD платформа              | https://github.com/            |
| React          | Фронтенд                     | https://reactjs.org            |


## Автор
- github: ilart
- email: arteevilya@gmail.com 

## Ссылка на развернутый сервер
Здесь вы можете ознакомится и проверить как работает мой тестовый сервер:
- [Admin page](http://51.250.81.3/admin/)
- [Foodgram](http://51.250.81.3/signin/)
\
email: admin@example.com
\
пароль: AdminPassword777