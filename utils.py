"""
Вспомогательные функции для обработки данных
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def format_ticket_status(status):
    """
    Преобразует числовой статус тикета в читаемый текст и CSS класс.
    
    Аргументы:
        status (int): Числовой статус
    
    Возвращает:
        tuple: (текстовый статус, css класс)
    """
    status_map = {
        1: ('Открыт', 'open'),
        2: ('Выполнен', 'completed'),
        3: ('Закрыт', 'closed'),
        4: ('Удален', 'deleted'),
        5: ('На удержании', 'on-hold'),
        6: ('В ожидании', 'pending'),
        7: ('Спам', 'spam'),
        8: ('Новый', 'new'),
        9: ('Рассылка', 'mailing'),
        10: ('Объединен', 'merged')
    }
    
    default = ('Неизвестный статус', 'unknown')
    return status_map.get(status, default)


def format_datetime(date_string):
    """
    Форматирует дату из формата API в читаемый вид.
    
    Аргументы:
        date_string (str): Дата в формате 'YYYY-MM-DD HH:MM:SS'
    
    Возвращает:
        str: Дата в формате 'DD.MM.YYYY HH:MM' или исходная строка при ошибке
    """
    if not date_string:
        return 'Неизвестно'
    
    try:
        dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d.%m.%Y %H:%M')
    except ValueError:
        return date_string


def get_client_info(ticket):
    """
    Извлекает информацию о клиенте из тикета.
    
    Аргументы:
        ticket (dict): Данные тикета
    
    Возвращает:
        str: Почта клиента, имя или 'Неизвестно'
    """
    client_email = ticket.get('channel_email')
    client_name = ticket.get('client_name')
    
    if client_email:
        return client_email
    elif client_name:
        return client_name
    else:
        return 'Неизвестно'


def sort_tickets_by_date(tickets):
    """
    Сортирует тикеты по дате создания (от новых к старым).
    
    Аргументы:
        tickets (list): Список тикетов
    
    Возвращает:
        list: Отсортированный список тикетов
    """
    return sorted(tickets, key=lambda x: x.get('created_at', ''), reverse=True)


def paginate_tickets(tickets, page, per_page):
    """
    Разбивает список тикетов на страницы.
    
    Аргументы:
        tickets (list): Список тикетов
        page (int): Номер страницы (начинается с 1)
        per_page (int): Количество тикетов на странице
    
    Возвращает:
        tuple: (список тикетов для страницы, общее количество, общее количество страниц)
    """
    total_tickets = len(tickets)
    total_pages = (total_tickets + per_page - 1) // per_page
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_tickets = tickets[start_idx:end_idx]
    
    return paginated_tickets, total_tickets, total_pages