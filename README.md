# PrintStudio3D — сервис 3D-печати и 3D-сканирования

Production-ready Django-монолит для сервиса 3D-печати: каталог готовых
изделий, заявки на печать собственных 3D-моделей, заявки на
3D-сканирование объектов и система заявок вместо классического
интернет-магазина с оплатой.

**Ключевой принцип:** у клиентов нет аккаунтов, паролей и личного
кабинета. Клиент оставляет заявку (имя + телефон обязательны), заявка
сохраняется в PostgreSQL и обрабатывается администратором через
собственную (не Django Admin) панель управления `/manage/`.
Авторизация нужна только для персонала.

---

## 1. Архитектура

```
3dprint_service/
├── config/                  # настройки, urls, wsgi/asgi
│   └── settings/
│       ├── base.py          # общие настройки
│       ├── dev.py           # локальная разработка (console email backend)
│       └── prod.py          # production (SSL, HSTS, SMTP)
├── apps/
│   ├── core/                 # главная, о нас, контакты, email, валидаторы, номера заявок
│   ├── products/              # каталог: Category, Product, ProductImage
│   ├── orders/                 # корзина (сессия) + заявка на товары
│   ├── print_requests/         # заявка на печать своей 3D-модели
│   ├── scanning/                # заявка на 3D-сканирование
│   └── dashboard/               # собственная панель управления /manage/ (не Django Admin)
├── templates/                 # Django templates (base + components + страницы)
├── static/                    # CSS / JS (vanilla, без React)
├── media/                     # загруженные файлы клиентов (не в БД)
├── requirements/               # base / dev / prod
├── nginx/nginx.conf            # reverse proxy для production
├── Dockerfile
├── docker-compose.yml           # локальная разработка
├── docker-compose.prod.yml      # production (web + db + nginx)
├── .github/workflows/ci.yml     # lint + tests + docker build
├── .github/workflows/deploy.yml # build → push → deploy по SSH
└── manage.py
```

**Технологии:** Django 5, PostgreSQL, Django Templates + vanilla JS,
Gunicorn, Nginx, Docker / docker-compose, GitHub Actions, pytest.

**Ключевой поток данных:**

```
Гость → каталог → корзина (сессия) → форма заявки
      → PostgreSQL (OrderRequest + OrderRequestItem)
      → REQ-000123 → страница "Заявка отправлена"
      → администратор видит заявку в панели управления `/manage/`
```

То же самое для печати модели (`PRINT-000123`) и 3D-сканирования
(`SCAN-000123`).

---

## 2. Реализованный функционал

- Каталог товаров: категории, поиск, фильтрация по категории,
  сортировка (новизна/цена/название), пагинация, карточки, страница товара.
- Корзина на Django-сессиях (без аккаунта): добавление, изменение
  количества, удаление, очистка после отправки заявки.
- Заявка на товары (`OrderRequest` + `OrderRequestItem`) со снэпшотом
  названия и цены товара на момент заказа.
- Заявка на печать собственной модели (`CustomPrintRequest`): файл
  (STL/OBJ/3MF/STEP/STP) и/или ссылка на модель, материал, цвет, срок,
  до 5 дополнительных фото.
- Заявка на 3D-сканирование (`ScanningRequest`): обязательная загрузка
  1–10 фотографий объекта, требования к постобработке и формату результата.
- Уникальные, сгенерированные сервером номера заявок: `REQ-000001`,
  `PRINT-000001`, `SCAN-000001` (через транзакционный счетчик, без гонок).
- **Собственная (не Django Admin) панель управления `/manage/`**:
  отдельный брендированный логин для персонала, дашборд со сводкой
  по всем очередям заявок, управление товарами (поиск/фильтр по
  наличию, инлайн-переключение активности, форма с превью главного
  изображения и редактируемой галереей фото), категории в виде
  карточек, три очереди заявок с фильтрами по статусу и раздельные
  двухколоночные страницы деталей (контакты/файлы слева, смена
  статуса + ориентировочная цена + комментарий администратора справа).
  Django Admin (`/admin/`) при этом остаётся доступен как технический
  резерв, но основной ежедневной панелью является `/manage/`.
- Email-уведомления клиенту (если указан email) и администратору
  после каждой заявки; консольный backend в dev, SMTP в prod;
  ошибки отправки логируются и не прерывают сохранение заявки.
- Безопасная загрузка файлов: allow-list расширений, запрет
  исполняемых/скриптовых файлов, проверка magic-bytes для изображений,
  ограничение размера и количества файлов, случайные имена файлов на диске.
- SEO: title/description на каждую страницу, Open Graph, canonical,
  `sitemap.xml`, `robots.txt`.
- Security: CSRF, стандартная защита Django от XSS/SQL-инъекций,
  HTTPS-редирект и secure-cookies в prod, `X-Frame-Options`, HSTS,
  логирование ошибок без секретов.
- Тесты: каталог, корзина, оформление заявки (включая снэпшот
  цены/названия), генерация и уникальность номеров заявок, валидация
  файлов (в т.ч. отклонение `.exe`), обязательность фото для
  сканирования, права доступа в `/manage/` (аноним → редирект на
  логин, не-staff → 403, staff → доступ), CRUD товаров/категорий и
  смена статуса заявок через панель.

**Явно НЕ реализовано** (по требованиям ТЗ): регистрация клиентов,
логин клиентов, личный кабинет, онлайн-оплата, чат, React,
микросервисы.

---

## 3. Быстрый старт (Docker, рекомендуется)

```bash
cp .env.example .env
# отредактируйте .env при необходимости (SECRET_KEY, пароли и т.д.)

docker compose up --build
```

Compose сам выполнит `migrate`, `collectstatic` и поднимет сервер на
`http://localhost:8000/`.

Создать администратора:

```bash
docker compose exec web python manage.py createsuperuser
```

(Опционально) наполнить каталог демо-товарами:

```bash
docker compose exec web python manage.py seed_demo_data
```

Админка (Django Admin, резерв): `http://localhost:8000/admin/`
Панель управления (основная): `http://localhost:8000/manage/`

---

## 4. Локальный запуск без Docker

Требуется Python 3.12 и локально установленный/доступный PostgreSQL 16.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements/dev.txt

cp .env.example .env
export $(grep -v '^#' .env | xargs)   # или используйте python-decouple/direnv

createdb printshop                    # либо создайте БД через psql

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 5. .env — переменные окружения

| Переменная | Назначение |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` или `config.settings.prod` |
| `SECRET_KEY` | секретный ключ Django (обязателен, длинный случайный в prod) |
| `DEBUG` | `True`/`False` |
| `ALLOWED_HOSTS` | список хостов через запятую |
| `TIME_ZONE` | часовой пояс, по умолчанию `Europe/Moscow` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_HOST` / `POSTGRES_PORT` | подключение к PostgreSQL |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` | SMTP (используется только в prod) |
| `DEFAULT_FROM_EMAIL` | адрес отправителя писем |
| `ADMIN_EMAIL` | куда слать уведомления о новых заявках |
| `MAX_IMAGE_UPLOAD_MB` / `MAX_MODEL_UPLOAD_MB` | лимиты размеров файлов |
| `SECURE_SSL_REDIRECT` / `SECURE_HSTS_SECONDS` / `CSRF_TRUSTED_ORIGINS` | безопасность production |
| `IMAGE_NAME` / `IMAGE_TAG` | имя/тег Docker-образа для `docker-compose.prod.yml` |

Полный пример — в `.env.example`. Секреты никогда не коммитятся в Git.

---

## 6. PostgreSQL

Проект **не использует SQLite**. Все заявки хранятся в PostgreSQL
через стандартные Django-миграции (`python manage.py migrate`).

### Backup

```bash
docker compose exec db pg_dump -U printshop -Fc printshop > backup_$(date +%Y%m%d).dump
```

### Restore

```bash
cat backup_20260101.dump | docker compose exec -T db pg_restore -U printshop -d printshop --clean --if-exists
```

Для «plain SQL» дампа вместо `-Fc`/`pg_restore` можно использовать
`pg_dump ... > backup.sql` и `psql -U printshop -d printshop -f backup.sql`.

---

## 7. Тесты и линт

```bash
# внутри контейнера
docker compose exec web pytest --cov=apps --cov-report=term-missing
docker compose exec web ruff check .
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run

# или локально в venv
pytest
ruff check .
```

Тесты специально проверяют:

- анонимный пользователь **может** смотреть каталог, создавать заявки,
  загружать файлы;
- анонимный пользователь **не может** открыть `/admin/` или `/manage/`,
  изменить товары или увидеть административные данные (для `/manage/`
  дополнительно проверяется, что аутентифицированный, но не-staff
  пользователь получает 403);
- отсутствие `/login/`, `/register/`, `/profile/` для клиентов;
- отклонение исполняемых файлов (`.exe` и т.п.) при загрузке;
- обязательность фотографий для заявки на сканирование;
- уникальность и корректный префикс номеров заявок (`REQ-` / `PRINT-` / `SCAN-`);
- сохранение снэпшота цены/названия товара в `OrderRequestItem`
  даже после изменения самого товара.

---

## 8. Static / media

- В development статика раздаётся Django (`DEBUG=True`), медиа — тоже.
- В production статика собирается `collectstatic` в `staticfiles/` и
  раздаётся через **Whitenoise** (внутри Gunicorn) и/или напрямую Nginx
  (см. `nginx/nginx.conf`, location `/static/` и `/media/`).
- Медиафайлы клиентов физически лежат в `media/` (`product_images/`,
  `print_requests/models/`, `print_requests/photos/`,
  `scanning_requests/`) и **не хранятся в базе данных** — в БД лежат
  только пути (`FileField`/`ImageField`).

---

## 9. Production deployment

```bash
cp .env.example .env         # заполнить боевыми значениями
docker compose -f docker-compose.prod.yml up --build -d
```

Сервисы: `web` (Gunicorn) + `db` (PostgreSQL) + `nginx` (reverse proxy,
раздача `/static/` и `/media/`). Для HTTPS положите сертификаты в
`nginx/certs/` и раскомментируйте HTTPS-блок в `nginx/nginx.conf`.

Production settings (`config/settings/prod.py`) требуют явного
`SECRET_KEY` и `ALLOWED_HOSTS`, включают `SECURE_SSL_REDIRECT`,
`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`,
`SECURE_CONTENT_TYPE_NOSNIFF`, HSTS и `X_FRAME_OPTIONS=DENY`.

---

## 10. CI/CD

**CI** (`.github/workflows/ci.yml`) на каждый push/PR: checkout →
установка зависимостей → `ruff check` → `manage.py check` → проверка
отсутствия несозданных миграций → `migrate` → `pytest` → `docker build`.

**CD** (`.github/workflows/deploy.yml`) на push в `main`: собирает и
пушит Docker-образ в реестр, затем по SSH на VPS выполняет
`docker compose -f docker-compose.prod.yml pull && up -d`.

Архитектура:

```
GitHub → GitHub Actions → Tests → Docker Build → Docker Registry
       → VPS (SSH) → docker compose → Nginx → Django (Gunicorn) → PostgreSQL
```

### GitHub Secrets, используемые в deploy.yml

| Secret | Назначение |
|---|---|
| `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` | логин в Docker-реестр |
| `REGISTRY_IMAGE` | полное имя образа, напр. `ghcr.io/org/3dprint-web` |
| `SSH_HOST` / `SSH_USER` / `SSH_PRIVATE_KEY` / `SSH_PORT` | доступ к VPS |
| `DEPLOY_PATH` | путь к проекту (с `docker-compose.prod.yml` и `.env`) на VPS |

Секреты задаются в **Settings → Secrets and variables → Actions** и
никогда не попадают в репозиторий.

---

## 11. Nginx

`nginx/nginx.conf`: `/static/` и `/media/` отдаются напрямую из
volume, всё остальное проксируется на `web:8000` (Gunicorn). Закомментированный
блок для HTTPS/443 включается после размещения сертификатов в
`nginx/certs/`.

---

## 12. Создание товаров и работа с заявками

**Товары:** панель управления → *Товары* → *Добавить товар* (название,
категория, цена, артикул, остаток, главное изображение и галерея
дополнительных фото прямо в форме). Категории — раздел *Категории*
(карточки с изображением и счетчиком товаров). Либо
`python manage.py seed_demo_data` для быстрого наполнения для тестов.

**Заявки:** панель управления → соответствующий раздел (*Товары* /
*Печать моделей* / *3D-сканирование* в блоке «Заявки»). Список можно
фильтровать по статусу и искать по номеру/телефону/email.
Администратор открывает заявку, видит контактные данные, состав
заказа или файлы/фото, меняет статус (`NEW → ... → COMPLETED`), при
необходимости указывает `admin_comment` и `estimated_price`. Быстрый
обзор по всем очередям — на главной странице панели `/manage/`.

---

## 13. Команды — шпаргалка

```bash
# Docker
docker compose up --build                 # dev
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo_data
docker compose -f docker-compose.prod.yml up --build -d   # prod

# Django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py collectstatic --noinput

# Тесты / линт
pytest --cov=apps
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run

# Backup / restore PostgreSQL
docker compose exec db pg_dump -U printshop -Fc printshop > backup.dump
cat backup.dump | docker compose exec -T db pg_restore -U printshop -d printshop --clean --if-exists
```

---

## 14. Известные ограничения среды сборки

Этот проект был сгенерирован в песочнице без доступа к сети и без
предустановленного Django/PostgreSQL, поэтому `pip install`,
`manage.py migrate`, `pytest` и `docker build` не были выполнены
автоматически в процессе генерации. Файлы миграций (`apps/*/migrations/0001_initial.py`)
написаны вручную по моделям и включены в репозиторий — `migrate`
не полагается на `makemigrations` во время запуска контейнера.
Код прошёл ручную проверку на согласованность (компиляция всех `.py`
файлов, соответствие имён URL между `urls.py`/`reverse()`/`{% url %}`,
соответствие полей моделей и миграций), но перед продакшен-
использованием обязательно выполните шаги из раздела «Быстрый старт»
и раздела «Тесты и линт» у себя, чтобы подтвердить успешный `migrate`,
прохождение `pytest` (включая `makemigrations --check --dry-run`,
который должен пройти без изменений, если миграции и модели
согласованы) и сборку `docker build`.
