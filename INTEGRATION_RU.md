# Интеграция в систему заявок (RU)

Этот документ описывает рабочую схему интеграции проекта в чужой сайт заявок: загрузка карты, выбор адреса, создание заявки и отображение заявки на карте.

## 1) Что интегрируется

- `api.py` — backend API (Flask)
- `map.html` — карта лифтов (встраивается в `iframe`)
- `integration_example.html` — пример страницы заявок (для локальной проверки)

## 2) Базовая архитектура

1. Фронтенд системы заявок открывает карту в `iframe`.
2. Карта читает лифты через `GET /api/elevators`.
3. При выборе точки карта отправляет в родителя событие `ADDRESS_SELECTED`.
4. Родитель подставляет адрес в форму заявки.
5. При отправке формы родитель делает `POST /api/requests`.
6. После успеха родитель шлет в карту событие `NEW_REQUEST`, и карта добавляет синий маркер заявки.

## 3) Локальный запуск

```bash
pip install -r requirements.txt
python api.py
```

Проверка:

- `http://localhost:5000/`
- `http://localhost:5000/api/health`
- `http://localhost:5000/api/elevators`

## 4) API для интеграции

### Лифты

- `GET /api/elevators`
- `GET /api/elevators/<elevator_id>`
- `GET /api/elevators/nearby?lat=...&lon=...&radius=...`
- `GET /api/statistics`

### Заявки

- `POST /api/requests`
- `GET /api/requests`
- `GET /api/requests/<request_id>`

Пример `POST /api/requests`:

```json
{
  "address": "ул. Пушкина, д. 10",
  "latitude": 51.127,
  "longitude": 71.43,
  "elevator_id": "ELEV-001",
  "priority": "high",
  "description": "Лифт не работает",
  "contact": "Иванов Иван, +7 777 123 45 67"
}
```

Обязательные поля: `address`, `priority`, `description`, `contact`.

## 5) Встраивание карты во внешний сайт

```html
<iframe
  id="elevator-map"
  src="https://<URL-КАРТЫ>/map.html?apiUrl=https%3A%2F%2F<URL-API>%2Fapi&parentOrigins=https%3A%2F%2F<URL-ВАШЕГО-ФРОНТА>"
  width="100%"
  height="700"
  style="border:0"
></iframe>
```

Важно: `map.html` должен быть доступен по URL (не только локальным файлом).

Параметры `map.html`:

- `apiUrl` — URL backend API карты (например `https://api.example.com/api`)
- `parentOrigins` — разрешенный origin родительского окна для `postMessage`.
  Можно передать несколько через запятую: `https://app1.example.com,https://app2.example.com`

## 6) Обмен сообщениями между формой и картой

### Получение адреса из карты

```javascript
window.addEventListener('message', (event) => {
  // Разрешайте только доверенный origin вашей карты
  if (event.origin !== 'https://<URL-КАРТЫ>') return;

  if (event.data?.type === 'ADDRESS_SELECTED') {
    const { address, lat, lon } = event.data.data;
    document.getElementById('address').value = address;
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lon;
  }
});
```

### Отправка новой заявки в карту

```javascript
const iframe = document.getElementById('elevator-map');

iframe.contentWindow.postMessage(
  {
    type: 'NEW_REQUEST',
    data: {
      address: 'ул. Пушкина, д. 10',
      latitude: 51.127,
      longitude: 71.43,
      priority: 'high',
      description: 'Лифт не работает',
      contact: 'Иванов Иван'
    }
  },
  'https://<URL-КАРТЫ>'
);
```

## 7) Автодополнение адреса

В `integration_example.html` реализовано автодополнение через Nominatim (OpenStreetMap):

- пользователь вводит адрес,
- появляются подсказки,
- при выборе адреса заполняются `latitude/longitude`.

Если у вас корпоративный геокодер, замените вызовы Nominatim на ваш API.

## 8) Прод-схема без белого IP

Да, белый IP не нужен.

Рекомендуемая бесплатная схема:

1. API (`api.py`) -> Render (free)
2. Фронтенд (`map.html`) -> Netlify/GitHub Pages/Vercel

После деплоя:

- в `map.html` укажите `API_URL = 'https://<URL-API>/api'`
- в внешней системе в `iframe` укажите `https://<URL-КАРТЫ>/map.html`

Подробный деплой API: `DEPLOY_RENDER.md`.

## 9) CORS и безопасность

Для продакшена ограничьте CORS только нужными доменами:

```python
from flask_cors import CORS

CORS(app, origins=[
    'https://<домен-фронтенда-карты>',
    'https://<домен-системы-заявок>'
])
```

Рекомендации:

- не используйте `postMessage(..., '*')` в проде,
- проверяйте `event.origin`,
- сохраняйте заявки в БД (сейчас используется JSON-файл).

## 10) Чеклист перед сдачей

- [ ] `GET /api/health` отвечает 200
- [ ] карта загружает лифты
- [ ] выбор адреса на карте возвращает данные в форму
- [ ] ручной ввод адреса дает подсказки
- [ ] `POST /api/requests` создает заявку
- [ ] после создания на карте появляется синий маркер
- [ ] CORS ограничен доменами проекта
