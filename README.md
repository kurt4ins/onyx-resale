# Onyx
**Onyx** — это веб-приложение, платформа для продажи и покупки товаров. Пользователи могут регистрироваться как клиенты или продавцы, просматривать каталог товаров, добавлять товары в корзину и избранное, оформлять заказы, а продавцы могут управлять своими товарами и отслеживать статистику.

Сервер построен на Django с использованием современного админ-интерфейса Django Unfold, обеспечивающего удобное управление контентом и данными.

## Функции

### Для клиентов:
- Регистрация и авторизация с выбором роли (клиент/продавец) и загрузкой аватара
- Просмотр каталога товаров с фильтрацией по категориям, брендам и условию
- Поиск товаров по названию, описанию и бренду
- Добавление товаров в избранное
- Корзина покупок с возможностью изменения количества товаров
- Оформление заказов с выбором способа оплаты
- История заказов с детальной информацией
- Просмотр публичных страниц продавцов

### Для продавцов:
- Личный кабинет продавца с дашбордом и статистикой
- Управление товарами (создание, редактирование, удаление)
- Загрузка нескольких изображений для каждого товара
- Автокомплит при выборе категорий и брендов
- Создание и управление справочниками (бренды, категории, размеры)
- Статистика продаж по категориям, брендам и месяцам
- Публичная страница продавца с товарами и отзывами

### Общие функции:
- Нормализация телефонных номеров в формат +7XXXXXXXXXX
- Вход по email или телефону
- Аналитика просмотров товаров и поисковых запросов
- Система уведомлений
- Современный админ-интерфейс с Django Unfold

## Стек технологий
- **Backend:** Python 3.14+, Django 6.0+
- **Database:** SQLite
- **Admin:** Django Unfold 0.74.1+
- **Frontend:** HTML, CSS, JavaScript
- **Image Processing:** Pillow 12.0+

## Установка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/kurt4ins/onyx-resale
   cd onyx
   ```

2. **Установите зависимости с помощью uv**
   ```bash
   uv sync
   ```

3. **Создание .env файла**
   > Создайте файл `.env` в корне проекта с необходимыми переменными:
   ```
   SECRET_KEY=<ваш-секретный-ключ>
   DEBUG=True
   ```

4. **Примените миграции**
   ```bash
   python manage.py migrate
   ```

5. **Создайте суперпользователя (для доступа к админке)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Соберите статические файлы (опционально)**
   ```bash
    python manage.py collectstatic --noinput
   ```

7. **Запустите сервер разработки**
   ```bash
   python manage.py runserver
   ```

8. **Откройте приложение**
   - Перейдите в браузере по адресу `http://127.0.0.1:8000/`
   - Админ-панель доступна по адресу `http://127.0.0.1:8000/admin/`
   - Создайте новый аккаунт или войдите под суперпользователем

## Скриншоты

- Главная страница (Каталог товаров)
![Главная страница](./docs/img/Home.png)

- Регистрация
![Регистрация](./docs/img/Register.png)

- Профиль продавца
![Профиль продавца](./docs/img/SellerDashboard.png)

- Корзина
![Корзина](./docs/img/Cart.png)

- Админ-панель
![Админ-панель](./docs/img/Admin.png)

## Схема базы данных
```mermaid
erDiagram
    User ||--o| Customer : "has"
    User ||--o| Seller : "has"
    User ||--o{ Notification : "receives"
    
    Customer ||--o{ Wishlist : "has"
    Customer ||--o{ Cart : "has"
    Customer ||--o{ Order : "places"
    Customer ||--o{ Review : "writes"
    
    Seller ||--o{ Product : "sells"
    Seller ||--o{ Review : "receives"
    
    Category ||--o{ Product : "contains"
    Category ||--o| Category : "parent"
    
    Brand ||--o{ Product : "has"
    Size ||--o{ Product : "fits"
    
    Product ||--o{ ProductImage : "has"
    Product ||--o{ Wishlist : "in"
    Product ||--o{ CartItem : "in"
    Product ||--o{ OrderItem : "in"
    Product ||--o{ Review : "reviewed"
    Product ||--|| ProductAnalytics : "has"
    
    Cart ||--o{ CartItem : "contains"
    Order ||--o{ OrderItem : "contains"
    Order ||--o{ Payment : "has"
    
    User {
        int id PK
        string username
        string email
        string password
    }
    
    Customer {
        int id PK
        int user_id FK
        string name
        string email
        string phone
        string image
    }
    
    Seller {
        int id PK
        int user_id FK
        string name
        string email
        string phone
        boolean is_active
        boolean is_verified
    }
    
    Product {
        int id PK
        int seller_id FK
        string title
        text description
        int category_id FK
        int brand_id FK
        int size_id FK
        decimal price
        int quantity
        string condition
        boolean is_active
        boolean is_sold
    }
    
    Category {
        int id PK
        string name
        string slug
        int parent_id FK
    }
    
    Brand {
        int id PK
        string name
        string slug
    }
    
    Cart {
        int id PK
        int customer_id FK
    }
    
    CartItem {
        int id PK
        int cart_id FK
        int product_id FK
        int quantity
        decimal price
    }
    
    Order {
        int id PK
        int customer_id FK
        string status
    }
    
    OrderItem {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
    
    Payment {
        int id PK
        int order_id FK
        string status
        string method
        decimal amount
    }
```

## Архитектурная схема
```mermaid
graph TB
    A[Браузер<br>HTML/CSS/JS] -- HTTP --> B[Django Views<br/>Class-Based Views]
    B -- ORM --> C[(SQLite<br/>База данных)]
    B -- Templates --> D[Django Templates]
    B -- Forms --> E[Forms Layer<br/>Validation]
    B -- Admin --> F[Django Unfold<br/>Admin Interface]
    E --> C
    F --> C
    B -- Static/Media --> G[File Storage]
```

## Структура проекта

```
onyx/
├── apps/
│   ├── accounts/          # Управление пользователями (клиенты и продавцы)
│   ├── catalog/           # Каталог товаров, категории, бренды
│   ├── orders/            # Корзина, заказы, платежи
│   ├── analytics/         # Аналитика просмотров и поисков
│   └── core/              # Базовые функции (уведомления)
├── templates/             # HTML шаблоны
├── docs/                  # Документация 
├── staticfiles/           # Статические файлы
├── media/                 # Загруженные пользователями файлы
└── onyx/                  # Настройки проекта Django
```
