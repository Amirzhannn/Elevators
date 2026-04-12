"""
API для системы мониторинга лифтового оборудования
Предоставляет REST API endpoints для интеграции с внешними системами
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import random
import math
import json
import os
from faker import Faker

app = Flask(__name__)
# CORS позволяет обращаться к API с других доменов
CORS(app)

# Глобальное хранилище данных (в реальном проекте это будет база данных)
elevators_data = None
REQUESTS_FILE = os.path.join(os.path.dirname(__file__), 'requests_storage.json')


def load_requests_data() -> list:
    """
    Загружает заявки из JSON-файла.
    """
    if not os.path.exists(REQUESTS_FILE):
        return []

    try:
        with open(REQUESTS_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
    except (OSError, json.JSONDecodeError):
        pass

    return []


def save_requests_data() -> None:
    """
    Сохраняет заявки в JSON-файл.
    """
    with open(REQUESTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(requests_data, file, ensure_ascii=False, indent=2)


def generate_mock_data(num_records: int = 50) -> pd.DataFrame:
    """
    Генерирует тестовые данные о лифтовом оборудовании в Астане.
    """
    fake = Faker('ru_RU')
    
    # Координаты центра Астаны
    center_lat = 51.127
    center_lon = 71.430
    
    # Радиус разброса точек (примерно 10 км)
    lat_spread = 0.09
    lon_spread = 0.15
    
    data = []
    
    for i in range(1, num_records + 1):
        # Генерация статуса с заданным распределением
        status_roll = random.random()
        if status_roll < 0.7:
            status = 'ok'
        elif status_roll < 0.9:
            status = 'warning'
        else:
            status = 'error'
        
        # Генерация координат вокруг центра Астаны
        lat = center_lat + random.uniform(-lat_spread, lat_spread)
        lon = center_lon + random.uniform(-lon_spread, lon_spread)
        
        # Генерация даты последнего ТО (от 1 до 180 дней назад)
        days_ago = random.randint(1, 180)
        last_maintenance = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Статус сети (90% онлайн)
        network_ping = 'Online' if random.random() < 0.9 else 'Offline'
        
        data.append({
            'elevator_id': f'ELEV-{i:03d}',
            'address': f'{fake.street_address()}',
            'lat': lat,
            'lon': lon,
            'status': status,
            'network_ping': network_ping,
            'last_maintenance': last_maintenance
        })
    
    return pd.DataFrame(data)


@app.route('/api/elevators', methods=['GET'])
def get_elevators():
    """
    Получить список всех лифтов
    
    Query параметры:
    - status: фильтр по статусу (ok, warning, error)
    - network: фильтр по сети (Online, Offline)
    
    Пример: /api/elevators?status=error
    """
    global elevators_data
    
    # Инициализация данных при первом запросе
    if elevators_data is None:
        elevators_data = generate_mock_data(50)
    
    df = elevators_data.copy()
    
    # Фильтрация по статусу
    status_filter = request.args.get('status')
    if status_filter:
        df = df[df['status'] == status_filter]
    
    # Фильтрация по сети
    network_filter = request.args.get('network')
    if network_filter:
        df = df[df['network_ping'] == network_filter]
    
    # Конвертация в JSON
    result = df.to_dict('records')
    
    return jsonify({
        'success': True,
        'count': len(result),
        'data': result
    })


@app.route('/api/elevators/<elevator_id>', methods=['GET'])
def get_elevator(elevator_id):
    """
    Получить информацию о конкретном лифте
    
    Пример: /api/elevators/ELEV-001
    """
    global elevators_data
    
    if elevators_data is None:
        elevators_data = generate_mock_data(50)
    
    elevator = elevators_data[elevators_data['elevator_id'] == elevator_id]
    
    if elevator.empty:
        return jsonify({
            'success': False,
            'error': 'Elevator not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': elevator.to_dict('records')[0]
    })


@app.route('/api/elevators/nearby', methods=['GET'])
def get_nearby_elevators():
    """
    Получить лифты рядом с указанными координатами
    
    Query параметры:
    - lat: широта
    - lon: долгота
    - radius: радиус поиска в км (по умолчанию 1)
    
    Пример: /api/elevators/nearby?lat=51.127&lon=71.430&radius=2
    """
    global elevators_data
    
    if elevators_data is None:
        elevators_data = generate_mock_data(50)
    
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius', 1))
    except (TypeError, ValueError):
        return jsonify({
            'success': False,
            'error': 'Invalid parameters. Required: lat, lon (optional: radius)'
        }), 400
    
    if radius <= 0:
        return jsonify({
            'success': False,
            'error': 'Radius must be greater than 0'
        }), 400

    # Простой расчет расстояния (для точности нужна формула Haversine)
    # 1 градус ≈ 111 км
    lat_range = radius / 111
    cos_lat = abs(math.cos(math.radians(lat)))
    if cos_lat < 1e-6:
        cos_lat = 1e-6
    lon_range = radius / (111 * cos_lat)
    
    df = elevators_data[
        (elevators_data['lat'] >= lat - lat_range) &
        (elevators_data['lat'] <= lat + lat_range) &
        (elevators_data['lon'] >= lon - lon_range) &
        (elevators_data['lon'] <= lon + lon_range)
    ]
    
    result = df.to_dict('records')
    
    return jsonify({
        'success': True,
        'count': len(result),
        'data': result
    })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    Получить статистику по всем лифтам
    """
    global elevators_data
    
    if elevators_data is None:
        elevators_data = generate_mock_data(50)
    
    df = elevators_data
    
    stats = {
        'total': len(df),
        'by_status': {
            'ok': int(len(df[df['status'] == 'ok'])),
            'warning': int(len(df[df['status'] == 'warning'])),
            'error': int(len(df[df['status'] == 'error']))
        },
        'by_network': {
            'online': int(len(df[df['network_ping'] == 'Online'])),
            'offline': int(len(df[df['network_ping'] == 'Offline']))
        }
    }
    
    return jsonify({
        'success': True,
        'data': stats
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Проверка работоспособности API
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def root():
    """
    Корневой endpoint с подсказкой по API.
    """
    return jsonify({
        'success': True,
        'message': 'Elevator Monitor API is running',
        'api_base': '/api',
        'endpoints': [
            '/api/health',
            '/api/elevators',
            '/api/elevators/<id>',
            '/api/elevators/nearby?lat=..&lon=..&radius=..',
            '/api/statistics',
            '/api/requests',
            '/api/requests/<id>'
        ]
    })


# Глобальное хранилище заявок (в реальном проекте это будет база данных)
requests_data = load_requests_data()


@app.route('/api/requests', methods=['POST'])
def create_request():
    """
    Создать новую заявку
    
    Body (JSON):
    {
        "address": "ул. Пушкина, д. 10",
        "latitude": 51.127,
        "longitude": 71.430,
        "elevator-id": "ELEV-001",
        "priority": "high",
        "description": "Описание проблемы",
        "contact": "Иванов Иван, +7 777 123 4567"
    }
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid JSON body'
            }), 400
        
        # Валидация обязательных полей
        required_fields = ['address', 'priority', 'description', 'contact']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Поле "{field}" обязательно для заполнения'
                }), 400
        
        # Генерация ID заявки
        request_id = f'REQ-{len(requests_data) + 1:03d}'

        # Координаты (могут прийти как строки)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        try:
            latitude = float(latitude) if latitude not in (None, '') else None
            longitude = float(longitude) if longitude not in (None, '') else None
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'error': 'latitude/longitude must be numeric values'
            }), 400
        
        # Создание заявки
        new_request = {
            'request_id': request_id,
            'address': data['address'],
            'latitude': latitude,
            'longitude': longitude,
            'elevator_id': data.get('elevator_id') or data.get('elevator-id'),
            'priority': data['priority'],
            'description': data['description'],
            'contact': data['contact'],
            'status': 'new',
            'created_at': datetime.now().isoformat()
        }
        
        # Сохранение заявки
        requests_data.append(new_request)
        save_requests_data()
        
        return jsonify({
            'success': True,
            'data': new_request
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/requests', methods=['GET'])
def get_requests():
    """
    Получить список всех заявок
    
    Query параметры:
    - status: фильтр по статусу (new, in-progress, completed)
    - priority: фильтр по приоритету (low, medium, high, critical)
    
    Пример: /api/requests?status=new
    """
    filtered_requests = requests_data.copy()
    
    # Фильтрация по статусу
    status_filter = request.args.get('status')
    if status_filter:
        filtered_requests = [r for r in filtered_requests if r['status'] == status_filter]
    
    # Фильтрация по приоритету
    priority_filter = request.args.get('priority')
    if priority_filter:
        filtered_requests = [r for r in filtered_requests if r['priority'] == priority_filter]
    
    return jsonify({
        'success': True,
        'count': len(filtered_requests),
        'data': filtered_requests
    })


@app.route('/api/requests/<request_id>', methods=['GET'])
def get_request(request_id):
    """
    Получить информацию о конкретной заявке
    
    Пример: /api/requests/REQ-001
    """
    for req in requests_data:
        if req['request_id'] == request_id:
            return jsonify({
                'success': True,
                'data': req
            })
    
    return jsonify({
        'success': False,
        'error': 'Request not found'
    }), 404


if __name__ == '__main__':
    print("="*60)
    print("ELEVATOR MONITOR API")
    print("="*60)
    print("API запущен на: http://localhost:5000")
    print("\nДоступные endpoints:")
    print("  GET  /                        - Информация об API")
    print("  GET  /api/elevators          - Список всех лифтов")
    print("  GET  /api/elevators/<id>     - Информация о лифте")
    print("  GET  /api/elevators/nearby   - Лифты рядом с координатами")
    print("  GET  /api/statistics         - Статистика")
    print("  GET  /api/health             - Проверка работоспособности")
    print("  POST /api/requests           - Создать новую заявку")
    print("  GET  /api/requests           - Список всех заявок")
    print("  GET  /api/requests/<id>      - Информация о заявке")
    print("="*60)
    print("\nДля остановки нажмите Ctrl+C")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
