# FastAPI riot stat service приложение

## Описание

`in progress`

## Архитектура приложения

- `main.py` - запуск приложения, создание таблиц и инициализация данных
- `app/database.py` - конфигурация PostgreSQL и SQLAlchemy
- `app/models.py` - модели БД:
  - `Player` - данные аккаунта игрока (puuid, summoner lvl и т.д.)
  - `RankedEntry` - `in progress`
- `app/schemas.py` - Pydantic модели
- `app/security.py` - `in progress`, либо не понадобится и удалю
- `app/dependency.py` - зависимости FastAPI: получение сессии для работы с БД
- `app/api/v1/`
  - `player.py` - эндпоинты для получения данных аккаунта игрока
- `app/repository/` - операции с базой данных
- `app/service/` - бизнес-логика
- `app/client/riot_client.py` - инфраструктура для обращения к RiotAPI по httpx
- `app/config.py` - вытягивание данных из .env и хранение: url БД, словари для регионов, riot api key

## Запуск

Необходимо в корне репозитория создать `.env` с переменными `RIOT_API_KEY`, `USER_DB`, `PASSWORD_DB` и соответствующе присвоить им необходимые значения.<br></br>
Создать PostgreSQL БД можно с установленным Docker и командой в CMD:  
`docker run --name postgres-db docker run --name riot-db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=RiotStats -p 5432:5432 -d postgres:16`<br></br>
 В репозитории с проектом запустить сервер uvicorn  
 CMD `uvicorn main:app --reload`