# FastAPI riot stat service приложение

## Описание

Backend сервис для агрегации и анализа игровой статистики по игре League of Legends. Получение данных идет через Riot API, сохранение данных в PostgreSQL, миграции через Alembic.

## Архитектура приложения

- `main.py` - запуск приложения и инициализация данных
- `alembic/` - alembic миграции
- `app/database.py` - конфигурация PostgreSQL и SQLAlchemy
- `app/models.py` - модели БД:
  - `Player` - данные аккаунта игрока (puuid, summoner lvl и т.д.)
  - `RankedEntry` - данные о ранге игрока (tier, division и т.д.)
  - `Match` - данные о матче (тип матча, дата матча, длительность и т.д.)
  - `MatchParticipant` - данные участника матча (puuid участника, kda, позиция и т.д.)
- `app/schemas.py` - Pydantic модели
- `app/dependency.py` - зависимости FastAPI: получение сессии для работы с БД
- `app/api/v1/`
  - `player.py` - эндпоинты для получения данных профиля игрока, его ранга, матчей, статистики по чемпионам
  - `admin.py` - эндпоинты для запуска синхронизации определенного игрока и его матчей
- `app/constants.py` - QUEUE_MAPPING_HELPER константа для удобства формирования response схемы
- `app/repository/` - операции с базой данных
- `app/service/` - бизнес-логика
  - `app/service/sync.py` - функции для синхронизации данных игрока и матчей
- `app/client/riot_client.py` - инфраструктура для обращения к RiotAPI по httpx
- `app/config.py` - вытягивание данных из .env и хранение: url БД, словари для регионов, riot api key

## Пользовательские эндпоинты

Ни один пользовательский эндпоинт не обращается к Riot API, обращения идут только через админские эндпоинты, здесь только чтение имеющихся данных из БД

- `GET /api/v1/player/by-riot-id/{game_name}/{tag_line}` - получение профиля игрока по его Riot id
- `GET /api/v1/player/{puuid}` - получение профиля игрока по его puuid
- `GET /api/v1/player/{puuid}/ranked` - получение ранга/рангов игрока по puuid (SoloQ + Flex ранги выводятся с соответствующими подписями)
- `GET /api/v1/player/{puuid}/matches` - получение статистики всех матчей игрока по puuid (список на вывод отсортирован от более свежего матча к более старому)
- `GET /api/v1/player/{puuid}/champions/` - получение статистики чемпиона игрока по puuid и имени чемпиона (если оставить поле с именем чемпиона пустым, то выведет статистику по всем его чемпионам)
- `GET /api/v1/matches/{match_id}` - получение статистики матча по match_id и статистики участников

## Админские эндпоинты

- `GET /api/v1/admin/sync/by-riot-id/{game_name}/{tag_line}` - получение данных профиля игрока (summoner lvl, tier, division и т.д.) по riot id из Riot API и занесение/обновление в БД
- `GET /api/v1/admin/sync/by-puuid/{puuid}` - получение данных профиля игрока по puuid из Riot API и занесение/обновление в БД
- `GET /api/v1/admin/sync/matches/by-puuid/{puuid}` - получение последних count матчей игрока по puuid из Riot API и занесение новых в БД (число последних вытягиваемых матчей можно указать в поле count, если match_id уже есть в БД, делает запросы в Match-V5 только на новые матчи)

## Запуск

Необходимо в корне репозитория создать `.env` с переменными `RIOT_API_KEY`, `USER_DB`, `PASSWORD_DB` и соответствующе присвоить им необходимые значения.<br></br>
В репозитории с проектом запустить docker-compose  
CMD `docker-compose up --build`