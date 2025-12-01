online-teaching-platform/
├── services/
│   ├── user-service/
│   ├── homework-service/
│   ├── gradebook-service/
│   ├── profile-service/
│   ├── notifications-service/
│   ├── tests-service/
│   ├── schedule-service/
│   └── reports-service/
│
├── common/                 # Общие вещи (по желанию, можно ввести позже)
│   ├── libs/               # Общие питоновские модули
│   └── proto/              # Если когда-нибудь появится gRPC или общие схемы
│
├── infra/
│   ├── db/                 # SQL скрипты, init-скрипты для БД
│   └── nginx/              # Конфиги для API-gateway/Reverse proxy (если будет)
│
├── docker-compose.yml
├── .env                    # Общие env-переменные (НЕ для продакшена)
├── .gitignore
└── .github/
    └── workflows/
        ├── ci.yml          # линтеры, тесты
        └── cd.yml          # деплой (если будешь делать)