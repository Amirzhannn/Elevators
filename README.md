🏢 Elevator Monitor — система мониторинга лифтов.

Система для отслеживания состояния лифтов с интерактивной картой. Можно интегрировать в систему заявок.

📘 Документация
INTEGRATION_RU.md — интеграция
DEPLOY_RENDER.md — деплой API

api.py — запускает API
map.html — фронтенд (открывается отдельно)

🎯 Возможности
Карта лифтов по Астане
Статистика в реальном времени
Фильтр по статусу
Выбор адреса на карте
REST API для интеграции
📁 Структура
elevator_monitor/
├── api.py
├── map.html
├── requirements.txt
└── README.md
🚀 Запуск

Установка:

pip install -r requirements.txt

Запуск API:

python api.py

Адрес:

http://localhost:5000

Открытие карты:

открыть map.html в браузере
🔌 API

Основные запросы:

GET /api/elevators        — список лифтов
GET /api/elevators/<id>   — один лифт
GET /api/elevators/nearby — рядом с координатами
GET /api/statistics       — статистика
GET /api/health           — проверка API

Пример:

curl http://localhost:5000/api/elevators
🔗 Интеграция
iframe
<iframe src="http://localhost:5000/map.html"></iframe>
через API
fetch('http://localhost:5000/api/elevators')
  .then(res => res.json())
  .then(data => console.log(data));
выбор адреса
window.addEventListener('message', (event) => {
  if (event.data.type === 'ADDRESS_SELECTED') {
    console.log(event.data.data);
  }
});
🎨 Работа с картой
Цвета:
🟢 исправен
🟠 проблема
🔴 авария
Можно:
смотреть лифты
фильтровать
выбирать адрес
🔧 Продакшен

Изменить API:

const API_URL = 'https://your-domain.com/api';

Настроить CORS:

CORS(app)

Подключить БД вместо тестовых данных.

🐛 Ошибки

Нет Flask:

pip install -r requirements.txt

API не отвечает:

проверить запуск
открыть /api/health

CORS ошибка:

включить flask-cors
📝 Что дальше
подключить реальную БД
развернуть на сервере
встроить в систему заявок
