# Деплой API на Render (бесплатно)

1. Залей проект в GitHub (репозиторий).
2. Открой https://render.com и войди через GitHub.
3. Нажми **New +** -> **Blueprint**.
4. Выбери репозиторий с этим проектом.
5. Render прочитает `render.yaml` и создаст сервис автоматически.
6. Дождись статуса **Live**.

После деплоя API будет доступен по URL вида:

`https://elevator-monitor-api.onrender.com`

Проверка:

- `https://elevator-monitor-api.onrender.com/`
- `https://elevator-monitor-api.onrender.com/api/health`
- `https://elevator-monitor-api.onrender.com/api/elevators`

Важно:

- На бесплатном плане Render сервис "засыпает" при простое.
- Первый запрос после сна может отвечать 20-60 секунд.
