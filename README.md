# Cinema Management API

RESTful API для управления кинотеатром с системой рекомендаций фильмов.

## Технологии
- Python 3.8.5
- FastAPI 0.68.1
- SQLite 3
- JWT аутентификация
- Алгоритм рекомендаций на основе TF-IDF

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/timoonnovi/cinema-api.git
cd cinema-api
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```


## Запуск
```bash
uvicorn cinema_api.main:app --reload
```

API будет доступно по адресу: `http://localhost:8000`

## Документация API
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Основные эндпоинты

### Аутентификация
- `POST /register` - Регистрация нового пользователя
- `POST /token` - Получение JWT токена
- `POST /delete` - Удаление пользователя (нужна аутентификация)

### Фильмы
- `POST /movies` - Добавить фильм (требует админских прав)
- `GET /movies/{id}` - Получить информацию о фильме
- `GET /movies/{id}/recommendations` - Получить рекомендации по фильму
- `POST /movies/{id}/rate` - Оценить фильм (требует аутентификации)

### Пользовательские рекомендации
- `GET /users/me/recommendations` - Персонализированные рекомендации (требует аутентификации)

## Тестирование
```bash
pytest --cov=cinema_api --cov-report=term-missing
```

## Алгоритм рекомендаций
Система использует:
1. TF-IDF для векторного представления фильмов
2. Косинусную схожесть для поиска похожих фильмов
3. История оценок пользователя для персонализации

## Структура БД
docs/schema.jpg

## Pylint-анализ
docs/pylint.txt

## Таблицы:
- `users` - Пользователи системы
- `movies` - Каталог фильмов
- `movie_ratings` - Оценки фильмов

## Лицензия
MIT