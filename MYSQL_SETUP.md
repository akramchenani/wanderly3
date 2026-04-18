# Wanderly — Switch to MySQL & Seed Database

## Step 1 — Install MySQL driver

```bash
pip install mysqlclient requests Pillow
```

> On Windows if `mysqlclient` fails:
> ```bash
> pip install PyMySQL
> ```
> Then add to `wanderly/__init__.py`:
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

---

## Step 2 — Create the MySQL database

Open MySQL Workbench or the MySQL command line and run:

```sql
CREATE DATABASE wanderly_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

---

## Step 3 — Update settings.py

Copy `wanderly/settings.py` from this package into your project, then edit:

```python
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'wanderly_db',
        'USER':     'root',        # ← your MySQL username
        'PASSWORD': 'yourpassword',# ← your MySQL password
        'HOST':     'localhost',
        'PORT':     '3306',
    }
}
```

---

## Step 4 — Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 5 — Seed the database

```bash
python manage_seed.py
```

This will:
- Create **8 cities**: Paris, Dubai, Istanbul, Rome, Barcelona, London, New York, Tokyo
- Create **5 places** per city (with images downloaded from Unsplash)
- Create **5 hotels**, **5 cafés**, and **5 agencies** per city
- Create **posts** for each hotel
- Download and save all images into `media/`
- Create demo accounts (admin / traveler)

> The seed takes ~3-5 minutes due to image downloads.
> Re-running is safe — it skips existing records.

---

## Accounts created

| Role     | Username   | Password     |
|----------|------------|--------------|
| Admin    | admin      | admin123     |
| Customer | traveler   | traveler123  |
| Partners | (username) | partner123   |

Admin panel: http://127.0.0.1:8000/admin/
