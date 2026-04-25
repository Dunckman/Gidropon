## Требования к ПО

На компьютере должны быть установлены:

- Docker 24+
- Ollama 0.21.0+

В Ollama должны быть установлены следующие модели:

- qwen3:14b - `ollama pull qwen3:14b`
- nomic-embed-text:latest - `ollama pull nomic-embed-text:latest`\

## Добавление домена(-ов)

#### Если программа будет установлена на сервере

В файле `config/settings.py` надо указать Ваш домен(-ы):

```python
ALLOWED_HOSTS = [
    'example.com',       # точное совпадение домена
    'www.example.com',   # второй домен
    '192.168.1.100',     # IP-адрес сервера
    '.example.com',      # example.com + все поддомены (api.example.com, blog.example.com)
    'myapp.internal',    # внутренние домены (без TLD тоже работает)
]
```

#### Если программа установлена на Вашем личном ПК

Достаточно будет указать следующее:

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]
```

## Запуск

```bash
docker compose build                                               # сборка контейнеров
docker compose up -d                                               # запуск контейнеров
docker compose exec web python manage.py migrate                   # создание таблиц в БД
docker compose exec web python manage.py collectstatic --noinput   # сборка статических файлов
docker compose exec web python manage.py createsuperuser           # создание админа
```