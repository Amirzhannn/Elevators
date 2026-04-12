# 🏢 Elevator Monitor - Система мониторинга лифтового оборудования

## 📋 Описание проекта

Это система для мониторинга лифтового оборудования с интерактивной картой, которая может быть интегрирована в существующую систему управления заявками.

## 📘 Актуальная документация по интеграции

- Подробная интеграция (RU): `INTEGRATION_RU.md`
- Деплой API на Render: `DEPLOY_RENDER.md`

> Важно: `api.py` поднимает API. Файл `map.html` обычно размещается как фронтенд-страница (статический хостинг или ваш веб-сервер), а не как endpoint Flask.

## 🎯 Основные возможности

1. **Интерактивная карта** - отображение всех лифтов на карте Астаны
2. **Статистика в реальном времени** - количество исправных, требующих внимания и аварийных лифтов
3. **Фильтрация** - по статусу лифтов
4. **Выбор адреса на карте** - для создания новых заявок
5. **REST API** - для интеграции с другими системами

## 📁 Структура проекта

```
elevator_monitor/
├── api.py                              # Backend API (Flask)
├── map.html                            # Интерактивная карта (Frontend)
├── elevator_monitor_dashboard.py      # Генератор статической карты (старая версия)
├── elevator_monitor_dashboard.html    # Статическая карта (старая версия)
├── requirements.txt                    # Зависимости Python
└── README.md                          # Документация
```

## 🚀 Установка и запуск

### Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

**Что устанавливается:**
- `flask` - веб-фреймворк для создания API
- `flask-cors` - для разрешения запросов с других доменов
- `pandas` - для работы с данными
- `faker` - для генерации тестовых данных

### Шаг 2: Запуск API сервера

```bash
python api.py
```

API будет доступен по адресу: `http://localhost:5000`

**Вы увидите:**
```
============================================================
ELEVATOR MONITOR API
============================================================
API запущен на: http://localhost:5000

Доступные endpoints:
  GET  /api/elevators          - Список всех лифтов
  GET  /api/elevators/<id>     - Информация о лифте
  GET  /api/elevators/nearby   - Лифты рядом с координатами
  GET  /api/statistics         - Статистика
  GET  /api/health             - Проверка работоспособности
============================================================
```

### Шаг 3: Открытие карты

Откройте файл `map.html` в браузере:
- Просто дважды кликните на файл `map.html`
- Или откройте через браузер: `Файл → Открыть файл → map.html`

## 🔌 API Endpoints

### 1. Получить все лифты
```
GET /api/elevators
```

**Параметры (опционально):**
- `status` - фильтр по статусу (ok, warning, error)
- `network` - фильтр по сети (Online, Offline)

**Пример запроса:**
```bash
curl http://localhost:5000/api/elevators?status=error
```

**Пример ответа:**
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "elevator_id": "ELEV-001",
      "address": "ул. Пушкина, д. 10",
      "lat": 51.127,
      "lon": 71.430,
      "status": "ok",
      "network_ping": "Online",
      "last_maintenance": "2026-03-15"
    }
  ]
}
```

### 2. Получить информацию о конкретном лифте
```
GET /api/elevators/<elevator_id>
```

**Пример:**
```bash
curl http://localhost:5000/api/elevators/ELEV-001
```

### 3. Найти лифты рядом с координатами
```
GET /api/elevators/nearby?lat=51.127&lon=71.430&radius=2
```

**Параметры:**
- `lat` - широта (обязательно)
- `lon` - долгота (обязательно)
- `radius` - радиус поиска в км (по умолчанию 1)

### 4. Получить статистику
```
GET /api/statistics
```

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "total": 50,
    "by_status": {
      "ok": 35,
      "warning": 10,
      "error": 5
    },
    "by_network": {
      "online": 45,
      "offline": 5
    }
  }
}
```

### 5. Проверка работоспособности
```
GET /api/health
```

## 🔗 Интеграция в существующую систему

### Вариант 1: Встраивание через iframe

В HTML-коде их системы заявок добавьте:

```html
<iframe 
    src="http://localhost:5000/map.html" 
    width="100%" 
    height="600px" 
    frameborder="0">
</iframe>
```

### Вариант 2: Получение данных через API

В их JavaScript коде:

```javascript
// Получить все лифты
fetch('http://localhost:5000/api/elevators')
  .then(response => response.json())
  .then(data => {
    console.log('Лифты:', data.data);
    // Обработка данных
  });

// Получить статистику
fetch('http://localhost:5000/api/statistics')
  .then(response => response.json())
  .then(data => {
    console.log('Статистика:', data.data);
  });
```

### Вариант 3: Получение выбранного адреса

Когда пользователь выбирает адрес на карте, данные отправляются через `postMessage`:

```javascript
// В их системе заявок (родительское окно)
window.addEventListener('message', (event) => {
  if (event.data.type === 'ADDRESS_SELECTED') {
    const { lat, lon, address } = event.data.data;
    console.log('Выбран адрес:', address);
    console.log('Координаты:', lat, lon);
    
    // Заполнить форму заявки
    document.getElementById('address-field').value = address;
    document.getElementById('lat-field').value = lat;
    document.getElementById('lon-field').value = lon;
  }
});
```

## 🎨 Использование карты

### Просмотр лифтов
1. Откройте `map.html` в браузере
2. На карте отображаются все лифты с цветовой индикацией:
   - 🟢 Зеленый - исправен
   - 🟠 Оранжевый - требует внимания
   - 🔴 Красный - авария
3. Кликните на маркер, чтобы увидеть детальную информацию

### Фильтрация
В правой панели выберите фильтр по статусу:
- Все
- Исправны
- Требуют внимания
- Авария

### Выбор адреса для заявки
1. Нажмите кнопку **"📍 Выбрать адрес на карте"** внизу экрана
2. Кликните на карту в нужном месте
3. Система автоматически определит адрес по координатам
4. Подтвердите выбор адреса
5. Данные будут отправлены в систему заявок

## 🔧 Настройка для продакшена

### 1. Изменить URL API

В файле `map.html` найдите строку:
```javascript
const API_URL = 'http://localhost:5000/api';
```

Замените на URL вашего сервера:
```javascript
const API_URL = 'https://your-domain.com/api';
```

### 2. Настроить CORS

В файле `api.py` настройте разрешенные домены:
```python
from flask_cors import CORS

# Разрешить запросы только с определенных доменов
CORS(app, origins=['https://your-company-domain.com'])
```

### 3. Использовать реальную базу данных

Замените функцию `generate_mock_data()` на подключение к вашей базе данных:

```python
import psycopg2  # или другой драйвер БД

def get_elevators_from_db():
    conn = psycopg2.connect("dbname=elevators user=postgres")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM elevators")
    # ... обработка данных
    return df
```

## 📊 Пример интеграции в их систему

### Сценарий 1: Вкладка "Интерактивная карта"

В их системе заявок добавьте новую вкладку:

```html
<div class="tabs">
  <button onclick="showTab('requests')">Заявки</button>
  <button onclick="showTab('map')">Интерактивная карта</button>
</div>

<div id="map-tab" style="display: none;">
  <iframe 
    src="http://localhost:5000/map.html" 
    width="100%" 
    height="800px" 
    frameborder="0">
  </iframe>
</div>
```

### Сценарий 2: Форма создания заявки с выбором адреса

```html
<form id="request-form">
  <label>Адрес:</label>
  <input type="text" id="address" required>
  <button type="button" onclick="openMapSelector()">
    📍 Выбрать на карте
  </button>
  
  <input type="hidden" id="latitude">
  <input type="hidden" id="longitude">
  
  <button type="submit">Создать заявку</button>
</form>

<script>
function openMapSelector() {
  // Открыть карту в модальном окне или новой вкладке
  window.open('map.html', 'MapSelector', 'width=1200,height=800');
}

// Получить выбранный адрес
window.addEventListener('message', (event) => {
  if (event.data.type === 'ADDRESS_SELECTED') {
    document.getElementById('address').value = event.data.data.address;
    document.getElementById('latitude').value = event.data.data.lat;
    document.getElementById('longitude').value = event.data.data.lon;
  }
});
</script>
```

## 🐛 Решение проблем

### Проблема: API не запускается

**Ошибка:** `ModuleNotFoundError: No module named 'flask'`

**Решение:**
```bash
pip install -r requirements.txt
```

### Проблема: Карта не загружает данные

**Ошибка в консоли браузера:** `Failed to fetch`

**Решение:**
1. Убедитесь, что API запущен (`python api.py`)
2. Проверьте, что API доступен: откройте `http://localhost:5000/api/health` в браузере
3. Проверьте консоль браузера (F12) на наличие ошибок CORS

### Проблема: CORS ошибка

**Ошибка:** `Access to fetch has been blocked by CORS policy`

**Решение:**
Убедитесь, что в `api.py` установлен `flask-cors`:
```python
from flask_cors import CORS
CORS(app)
```

## 📝 Следующие шаги для интеграции

1. **Обсудите с командой** их систему заявок:
   - На каком языке/фреймворке написана? (PHP, Node.js, Python, etc.)
   - Какая база данных используется?
   - Где хранятся данные о лифтах?

2. **Подключите реальные данные:**
   - Замените `generate_mock_data()` на запросы к их БД
   - Синхронизируйте структуру данных

3. **Разверните на сервере:**
   - Установите API на их сервер
   - Настройте домен и HTTPS
   - Обновите URL в `map.html`

4. **Интегрируйте в их интерфейс:**
   - Добавьте вкладку "Интерактивная карта"
   - Добавьте кнопку выбора адреса в форму создания заявки

## 💡 Полезные советы

- **Тестирование:** Используйте `http://localhost:5000/api/health` для проверки работы API
- **Отладка:** Откройте консоль браузера (F12) для просмотра ошибок JavaScript
- **Производительность:** При большом количестве лифтов (>1000) рассмотрите пагинацию API
- **Безопасность:** В продакшене используйте HTTPS и аутентификацию для API

## 📞 Вопросы?

Если что-то непонятно или нужна помощь с интеграцией, обратитесь к своему наставнику на практике!

---

**Удачи с практикой! 🚀**
#   E l e v a t o r s  
 