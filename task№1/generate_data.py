import random
from datetime import datetime, timedelta
from faker import Faker
import csv

fake = Faker()

# Параметры генерации
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 31)
days = (end_date - start_date).days + 1
action_types = [
    'first_visit', 'registration', 'login', 'logout',
    'create_topic', 'view_topic', 'delete_topic', 'create_message'
]

# Генерация данных
users = []
logs = []
user_id_counter = 1

for day in range(days):
    current_date = start_date + timedelta(days=day)
    date_str = current_date.strftime('%Y-%m-%d')

    # Генерация 5 регистраций в день
    for _ in range(5):
        user = {
            'user_id': user_id_counter,
            'username': fake.user_name(),
            'created_at': current_date
        }
        users.append(user)
        logs.append({
            'user_id': user_id_counter,
            'action_type': 'registration',
            'server_response': 'success',
            'timestamp': current_date,
            'action_id': None
        })
        user_id_counter += 1

    # Генерация минимум 5 действий каждого типа
    for action in action_types:
        min_actions = 5
        if action == 'create_topic':
            min_actions += 2  # 2 ошибки
        for _ in range(min_actions):
            user_id = None
            if action in ['registration', 'login', 'logout', 'create_topic', 'delete_topic']:
                user = random.choice(users) if users and action != 'registration' else None
                user_id = user['user_id'] if user else None
            elif action == 'create_message':
                user_id = random.choice(users)['user_id'] if random.choice([True, False]) and users else None

            # Обработка ошибок для create_topic
            if action == 'create_topic':
                if random.choice([True, False]) and len(logs) >= 2:
                    # Генерируем ошибку для незалогиненного
                    user_id = None
                    response = 'error'
                else:
                    response = 'success' if user_id else 'error'
            else:
                response = 'success'

            logs.append({
                'user_id': user_id,
                'action_type': action,
                'server_response': response,
                'timestamp': current_date,
                'action_id': random.randint(1000, 9999) if action in ['create_topic', 'create_message'] else None
            })

# Функция для корректного форматирования данных перед записью в CSV
def format_for_csv(value):
    if value is None:
        return ''
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return value

# Сохранение users.csv
with open('users.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['user_id', 'username', 'created_at'])
    writer.writeheader()
    for user in users:
        writer.writerow({
            'user_id': user['user_id'],
            'username': user['username'],
            'created_at': format_for_csv(user['created_at'])
        })

# Сохранение logs.csv с гарантированно правильным форматом
with open('logs.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'action_type', 'action_id', 'server_response', 'timestamp'])
    for log in logs:
        writer.writerow([
            log['user_id'] if log['user_id'] is not None else '',
            log['action_type'],
            log['action_id'] if log['action_id'] is not None else '',
            log['server_response'],
            log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        ])

# print("Файлы успешно сгенерированы: users.csv и logs.csv")