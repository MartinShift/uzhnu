# Arch Kanban — Канбан-дошка для архітектурного бюро

Канбан-таск-менеджер для невеликої архітектурної студії. Кожен проєкт (наприклад, «Вілла в Ужгороді») — це картка, яка рухається колонками: **Ескіз → Погодження замовником → Розробка креслень → Готово**. Можна призначати членів команди (архітектор, дизайнер, конструктор) та прикріплювати посилання на креслення.

## Стек

- **Backend:** ASP.NET Core 10 Web API + Entity Framework Core
- **База даних:** SQL Server LocalDB (за замовчуванням) або SQLite (для локальної розробки без LocalDB)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS v4
- **Drag & Drop:** `@hello-pangea/dnd`
- **i18n:** `react-i18next` — перемикач UK/EN у навбарі, мова зберігається в `localStorage`

## Передумови

- .NET 10 SDK
- Node.js 20+ та npm
- (Опційно) SQL Server LocalDB — лише якщо хочете запустити в режимі `Production` зі справжнім SQL Server. У `Development` за замовчуванням використовується SQLite-файл `archkanban.db`, тож нічого додатково встановлювати не треба.

## Запуск

### 1. Бекенд

```powershell
cd server
dotnet run
```

API запуститься на `http://localhost:5080`. При першому старті:

- автоматично створиться база даних (SQLite-файл `server/archkanban.db` у dev-режимі або БД `ArchKanban` у LocalDB у prod-режимі);
- додасться демо-сидинг: 5 членів команди + 4 проєкти у різних колонках.

Swagger UI: `http://localhost:5080/swagger`.

### 2. Фронтенд

В іншому терміналі:

```powershell
cd client
npm install
npm run dev
```

UI: `http://localhost:5173`.

## Переключення на SQL Server LocalDB

Якщо ви хочете використовувати SQL Server LocalDB (а не SQLite, який ввімкнений у dev-режимі), є два варіанти:

1. **Запустити в Production-режимі** (тоді читається лише `appsettings.json`, де налаштований LocalDB):
   ```powershell
   $env:ASPNETCORE_ENVIRONMENT="Production"
   dotnet run
   ```
2. **Або** відредагувати `server/appsettings.Development.json`, виставивши:
   ```json
   {
     "Database": { "Provider": "SqlServer" },
     "ConnectionStrings": {
       "DefaultConnection": "Server=(localdb)\\MSSQLLocalDB;Database=ArchKanban;Trusted_Connection=True;TrustServerCertificate=True"
     }
   }
   ```

Якщо при запуску ви побачите помилку `Cannot create an automatic instance` — це означає що ваш екземпляр LocalDB зламаний. Виправити можна через:
```powershell
SqlLocalDB.exe delete MSSQLLocalDB
SqlLocalDB.exe create MSSQLLocalDB
```
Якщо й це не допомагає (часто буває на свіжих інсталяціях SQL Server 2025 LocalDB), залиште SQLite — для демо результат буде той самий.

## Структура проєкту

```
uzhnu/
├── server/                       # ASP.NET Core Web API
│   ├── Controllers/              # ProjectsController, MembersController, AttachmentsController
│   ├── Data/                     # AppDbContext + DbSeeder
│   ├── Dtos/                     # request/response типи
│   ├── Models/                   # Project, Member, ProjectMember, Attachment, enums
│   └── Program.cs                # bootstrap, CORS, провайдер БД, EnsureCreated + Seed
└── client/                       # React + TS + Vite
    └── src/
        ├── api/                  # axios клієнт (projects, members)
        ├── components/           # Navbar, Column, ProjectCard, ProjectModal
        ├── i18n/                 # react-i18next + uk.json/en.json
        ├── pages/                # BoardPage, MembersPage
        ├── App.tsx, main.tsx
        └── types.ts
```

## Деплой на Render (безкоштовний один контейнер)

Репозиторій містить:

- `Dockerfile` — багатоетапна збірка: `node:22-alpine` будує React → `dotnet/sdk:10.0` публікує API → у фіналі `dotnet/aspnet:10.0` віддає і API, і статичний фронтенд з `wwwroot/`.
- `.dockerignore` — щоб у контекст збірки не потрапили `node_modules`, `bin`, `obj`, `.git` тощо.
- `render.yaml` — Render Blueprint: один web-сервіс на безкоштовному тарифі, регіон Frankfurt, провайдер БД — SQLite, healthcheck на `/health`.
- `client/.env.production` — порожній `VITE_API_URL`, тому в продакшені axios звертається до бекенду по relative-URL (той самий origin) і CORS не потрібен.

### Як це працює

- ASP.NET читає змінну середовища `PORT` (Render її задає сам) і слухає `http://0.0.0.0:$PORT`.
- `app.UseStaticFiles()` віддає React-білд з `wwwroot/`.
- `app.MapFallbackToFile("index.html")` повертає `index.html` на будь-який маршрут, який не зматчили API чи статичні файли — це робить React Router-deep-links (`/projects/42`, `/members`, `/login`) робочими після перезавантаження сторінки.
- SQLite-файл `archkanban.db` лежить у файловій системі контейнера. Render free має ефемерний диск — при холодному перезапуску БД зникне і `DbSeeder` створить її заново з тими самими демо-даними. Для шкільної демо цього достатньо.

### Покроковий деплой

1. **Запушити репозиторій на GitHub** (якщо ще не запушений):

    ```powershell
    cd C:\Users\MartinSaprykin\Desktop\uzhnu
    git init
    git add .
    git commit -m "Arch Kanban: initial deploy-ready version"
    git branch -M main
    # створи приватний/публічний репо на github.com, потім:
    git remote add origin https://github.com/<your-user>/arch-kanban.git
    git push -u origin main
    ```

2. **Зареєструватися на Render**: відкрий [render.com](https://render.com), натисни *Get Started for Free* і залогінься через GitHub. Підтверди дозвіл доступу до твого нового репо.

3. **Створити сервіс через Blueprint**:
    - У Render-дашборді натисни **New + → Blueprint**.
    - Обери репозиторій `arch-kanban`.
    - Render прочитає `render.yaml`, покаже preview: один web-сервіс `arch-kanban`, runtime *docker*, plan *free*, регіон *frankfurt*. Натисни **Apply**.

4. **Дочекатися першої збірки** (~5–10 хв): Render клонує репо, виконає `docker build` за нашим `Dockerfile` і запустить контейнер. У вкладці **Logs** ти побачиш ті самі повідомлення EF Core про створення таблиць та `Now listening on: http://0.0.0.0:10000`, як локально.

5. **Перевірити деплой**:
    - Відкрий URL виду `https://arch-kanban.onrender.com` — повинна завантажитись сторінка логіну.
    - Залогінься як `admin` / `admin` (або `olena` / `pass` як менеджер, `taras` / `pass` як звичайний користувач).
    - Перевір drag-and-drop, відкриття детальної сторінки задачі, додавання коментаря.
    - Перевір `https://arch-kanban.onrender.com/health` → JSON `{"status":"ok",...}`.

6. **Подальші релізи**: будь-який `git push` у `main` тригерить новий деплой автоматично — нічого вручну робити не треба.

### Локально перевірити Docker-збірку (опційно)

```powershell
docker build -t arch-kanban .
docker run --rm -p 8080:8080 -e PORT=8080 arch-kanban
# відкрий http://localhost:8080
```

### Особливості Render free tier

- Перший запит після ~15 хв простою холодний — контейнер засинає, відповідь може йти 20–40 с. Далі — миттєво.
- 750 безкоштовних годин на місяць (вистачає на один цілодобовий сервіс).
- Файлова система ефемерна → SQLite-БД скидається при кожному перезапуску контейнера. Якщо для демо це важливо — для продакшену потрібен Render Postgres (теж є free tier) або платний persistent disk.
- JWT-секрет у `server/Auth/TokenService.cs` зашитий у коді — для шкільної демо ОК, у справжньому продакшені треба винести в env-змінну.

## Що НЕ реалізовано (свідомо, щоб не ускладнювати)

- Завантаження файлів — лише посилання (URL)
- Юніт-тести, AutoMapper, MediatR, Clean Architecture
- Database міграції (використовується `EnsureCreated` + seed)
- Persistent storage у продакшені (Render free SQLite — ефемерна)
