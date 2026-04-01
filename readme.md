# Поиск тикетов Usedesk

Веб-приложение для поиска тикетов в системе Usedesk. Позволяет находить тикеты по номеру, теме, почте или телефону без прямого доступа к Usedesk.

## Возможности

- Поиск по номеру, теме, почте клиента или телефону
- Отображение исполнителя тикета
- Статусы тикетов с цветовой индикацией
- Пагинация результатов
- Адаптивный дизайн
- Логирование всех операций

## Установка

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Создайте файл `.env`** в корне проекта:
   ```env
   USEDESK_API_TOKEN=ваш_api_токен
   USEDESK_BASE_URL=https://api.usedesk.ru
   TICKETS_PER_PAGE=10
   API_TIMEOUT=60
   LOG_FILE=logs/app.log
   LOG_LEVEL=INFO
   SECRET_KEY=ваш_секретный_ключ
   DEBUG=True
   HOST=0.0.0.0
   PORT=5000
   ```

3. **Запустите приложение:**
   ```bash
   python app.py
   ```

4. **Откройте в браузере:** `http://localhost:5000`

## Структура проекта

```
usedesk-search/
├── app.py              # Основное Flask-приложение
├── api_client.py       # Клиент для Usedesk API
├── utils.py            # Вспомогательные функции
├── config.py           # Конфигурация
├── requirements.txt    # Зависимости
├── templates/
│   └── index.html      # HTML-шаблон
├── static/
│   ├── style.css       # Стили
│   └── script.js       # Клиентская логика
└── logs/               # Логи приложения
```

## Архитектура

```
Браузер → Flask (app.py) → api_client.py → Usedesk API
                ↓
           utils.py (форматирование, пагинация)
```