# aygarden.az — Backend (Django REST Framework)

## Quraşdırma

```bash
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver     # http://127.0.0.1:8000
```

Arxivdə `db.sqlite3` və `media/` artıq nümunə məlumatlarla gəlir.
Sıfırdan başlamaq üçün:

```bash
python manage.py seed_data            # nümunə məlumatlar + meyvə şəkilləri
python manage.py seed_data --flush    # hər şeyi silib yenidən yaratmaq
python manage.py createsuperuser
```

**Admin panel:** http://127.0.0.1:8000/admin/
Hazır istifadəçi: `admin` / `Aygarden2026!` (**dərhal dəyişin**)

## Admin paneldən idarə olunanlar

| Bölmə | Nə var |
|---|---|
| **Parametrlər** | loqo, footer loqosu, favicon, telefonlar, WhatsApp, e-poçt, ünvan, iş saatları, xəritə, sosial şəbəkələr, SEO |
| Bannerlər | ana səhifə slayderi ("Müraciət et" düyməsi) |
| Statistika | Komanda üzvü, Məhsul çeşidi və s. |
| Haqqımızda səhifəsi | mətn, şəkillər, Vizyonumuz, Missiyamız |
| Dəyərlərimiz / Üstünlüklərimiz / Beynəlxalq tərəfdaşlıqlar | |
| Kateqoriyalar / Məhsullar (+ qalereya) | |
| Xəbərlər | |
| Müraciətlər | sayt formalarından gələn mesajlar |

## API

| Metod | Endpoint | Təsvir |
|---|---|---|
| GET | `/api/settings/` | sayt parametrləri |
| GET | `/api/slides/` | bannerlər |
| GET | `/api/statistics/` | statistika |
| GET | `/api/about/` | haqqımızda + dəyərlər + üstünlüklər + tərəfdaşlar |
| GET | `/api/partners/` | tərəfdaşlar |
| GET | `/api/categories/`, `/api/categories/<slug>/` | kateqoriyalar |
| GET | `/api/products/?category=&search=&featured=true&page=&page_size=` | məhsullar |
| GET | `/api/products/<slug>/` | məhsul (+ qalereya, oxşar məhsullar) |
| GET | `/api/news/?page=`, `/api/news/<slug>/` | xəbərlər |
| GET | `/api/search/?q=` | ümumi axtarış |
| POST | `/api/contact/` | müraciət (`full_name`, `phone`/`email`, `subject`, `message`, `source`) |

## Production

`.env.example` faylını `.env` kimi kopyalayın, `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS` və `CORS_ALLOWED_ORIGINS` dəyərlərini təyin edin. `python manage.py collectstatic`,
gunicorn + nginx (`/media/` və `/static/` nginx-dən verilməlidir).
