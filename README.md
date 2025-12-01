# Система онлайн-преподавания

Микросервисная платформа для онлайн-обучения, построенная на Python и FastAPI.

## Архитектура

Проект использует микросервисную архитектуру со следующими компонентами:

### Микросервисы

- **user-service** ✅ - Управление пользователями и аутентификация
- **homework-service** ✅ - Управление домашними заданиями
- **gradebook-service** 🔜 - Электронный журнал и оценки
- **profile-service** 🔜 - Профили и достижения пользователей
- **notifications-service** 🔜 - Отправка уведомлений (email, SMS)
- **tests-service** 🔜 - Тесты и экзамены
- **schedule-service** 🔜 - Расписание занятий
- **reports-service** 🔜 - Отчеты и аналитика

### Инфраструктура

- **PostgreSQL** - Основная база данных
- **Nginx** (опционально) - API Gateway / Reverse Proxy
- **Docker** - Контейнеризация
- **GitHub Actions** - CI/CD

## Структура проекта

```
online-teaching-platform/
├── services/
│   ├── user-service/          ✅ Реализован
│   ├── homework-service/      ✅ Реализован
│   ├── gradebook-service/     🔜 Планируется
│   ├── profile-service/       🔜 Планируется
│   ├── notifications-service/ 🔜 Планируется
│   ├── tests-service/         🔜 Планируется
│   ├── schedule-service/      🔜 Планируется
│   └── reports-service/       🔜 Планируется
├── common/                    # Общие библиотеки
│   ├── libs/
│   └── proto/
├── infra/
│   ├── db/                    # Скрипты инициализации БД
│   └── nginx/                 # Конфигурация Nginx
├── docker-compose.yml
├── .env
└── .gitignore
```

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- PostgreSQL (автоматически устанавливается в Docker)

### Запуск через Docker Compose

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd online-teaching-platform
```

2. Создайте файл `.env` (или скопируйте из примера):
```bash
cp .env.example .env
```

3. Запустите все сервисы:
```bash
docker-compose up -d
```

4. Проверьте статус сервисов:
```bash
docker-compose ps
```

### Доступ к сервисам

- **User Service API**: http://localhost:8001
- **User Service Docs**: http://localhost:8001/docs
- **Homework Service API**: http://localhost:8002
- **Homework Service Docs**: http://localhost:8002/docs
- **PostgreSQL**: localhost:5432

## User Service - Микросервис пользователей

### Основные возможности

✅ Регистрация пользователей (студенты, преподаватели, админы)  
✅ Аутентификация с JWT токенами  
✅ Управление профилем  
✅ Подтверждение email и телефона  
✅ Восстановление пароля  
✅ Административные функции  

### API Endpoints

#### Аутентификация
- `POST /api/auth/login` - Вход в систему
- `POST /api/auth/logout` - Выход

#### Пользователи
- `POST /api/users` - Регистрация
- `GET /api/users/me` - Получить профиль
- `PATCH /api/users/me` - Обновить профиль
- `POST /api/users/confirm-email` - Подтвердить email
- `POST /api/users/confirm-phone` - Подтвердить телефон
- `POST /api/users:request-password-reset` - Запросить сброс пароля
- `POST /api/users:reset-password` - Сбросить пароль
- `GET /api/users` - Список пользователей (админ)

Подробная документация: [services/user-service/README.md](services/user-service/README.md)

## Homework Service - Микросервис домашних заданий

### Основные возможности

✅ Создание домашних заданий преподавателями  
✅ Управление статусами ДЗ (draft/assigned/closed)  
✅ Отправка решений студентами  
✅ Просмотр решений с контролем доступа  
✅ Выставление оценок преподавателями  
✅ Интеграция с Gradebook Service  

### API Endpoints

#### Преподаватели
- `POST /api/courses/{course_id}/homeworks` - Создать ДЗ
- `GET /api/courses/{course_id}/homeworks` - Список ДЗ по курсу
- `POST /api/homeworks/{homework_id}/submissions/{submission_id}:grade` - Выставить оценку

#### Студенты
- `GET /api/students/me/homeworks` - Мои домашние задания
- `POST /api/homeworks/{homework_id}/submissions` - Отправить решение
- `GET /api/homeworks/{homework_id}/submissions/{submission_id}` - Просмотр решения

Подробная документация: [services/homework-service/README.md](services/homework-service/README.md)

## Разработка

### Локальный запуск сервиса

```bash
cd services/user-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Запуск тестов

```bash
cd services/user-service
pytest
```

### Линтеры

```bash
# Форматирование кода
black app/

# Сортировка импортов
isort app/

# Проверка стиля
flake8 app/
```

## CI/CD

Проект использует GitHub Actions для:

- **CI** (.github/workflows/ci.yml):
  - Линтинг кода (flake8, black, isort)
  - Запуск тестов
  - Проверка на каждый push и pull request

- **CD** (.github/workflows/cd.yml):
  - Автоматический деплой на продакшен
  - Запускается только для ветки main

## Переменные окружения

Основные переменные в `.env`:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=online_teaching

# User Service
USER_SERVICE_DB_USER=user_service
USER_SERVICE_DB_PASSWORD=user_service_pass123
USER_SERVICE_DB_NAME=user_service_db

# JWT
JWT_SECRET=your-secret-key-here
ACCESS_TOKEN_EXPIRES_MIN=60

# Environment
ENV=local  # local, dev, prod
```

## Технологический стек

### Backend
- **Python 3.11+**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **PostgreSQL** - Database
- **JWT** - Authentication
- **bcrypt** - Password hashing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy
- **GitHub Actions** - CI/CD

### Testing
- **pytest** - Testing framework
- **httpx** - HTTP client for testing

## Roadmap

- [x] Микросервис пользователей
- [x] Микросервис домашних заданий
- [ ] Микросервис журнала оценок
- [ ] Микросервис профилей
- [ ] Микросервис уведомлений
- [ ] Микросервис тестов
- [ ] Микросервис расписания
- [ ] Микросервис отчетов
- [ ] API Gateway (Nginx или Kong)
- [ ] Service mesh (опционально)
- [ ] Мониторинг (Prometheus + Grafana)
- [ ] Централизованное логирование (ELK Stack)

## Лицензия

MIT

## Контакты

Для вопросов и предложений создавайте Issues в GitHub.

