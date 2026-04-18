# 🌍 Wanderly — Tourism Platform

A full-featured Django MVT tourism platform: hotels, restaurants, cafés, agencies, real-time chat, bookings, flight search, weather, and notifications.

---

## ⚡ Quick Start
python -m venv venv
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
Open **http://127.0.0.1:8000**


the search nav does not work 
top hotels debateble 

---
python manage.py createsuperuser

## 🗂 Project Structure

```
wanderly/               ← Django project config (settings, urls, asgi)
accounts/               ← User & partner registration, login, profile
partners/               ← Partner profiles (Hotel, Restaurant, Coffee, Agency)
locations/              ← Cities & famous places (admin-managed)
posts/                  ← Posts, images, likes, comments
booking/                ← Hotel bookings & agency requests
flights/                ← Flight search & booking (mock + API-ready)
chat/                   ← Real-time WebSocket chat (Django Channels)
notifications/          ← Real-time notifications via WebSocket
reviews/                ← Star ratings & reviews
core/                   ← Home, search, about pages
templates/              ← All HTML templates
static/css/style.css    ← Complete design system
static/js/main.js       ← WebSocket chat/notifications, like toggle
```

---

## 👥 Roles

| Role    | Capabilities |
|---------|-------------|
| **User** | Browse, search, book hotels, chat with partners, rate, manage flights |
| **Partner** | Create posts (max 5, unlimited for agencies), manage bookings, chat with users |
| **Admin** | Approve partners, manage cities & places, full Django admin |

---

## 🔧 Configuration

### Database (MySQL — production)
In `wanderly/settings.py`, uncomment and configure:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wanderly_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
Install: `pip install mysqlclient`

### Weather API
Set your OpenWeatherMap API key in `settings.py`:
```python
WEATHER_API_KEY = 'your_key_here'
```

### Real-time (Production)
For production WebSockets, replace `InMemoryChannelLayer` with Redis:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {"hosts": [("127.0.0.1", 6379)]},
    },
}
```
Install: `pip install channels-redis`

---

## 📋 Key Business Rules

- Partners must be **approved by admin** before accessing features
- Partners can create **max 5 posts** (oldest auto-replaced on overflow); agencies are unlimited
- **One comment** per user per post; **one rating** per user per partner
- Hotels belong to a city; agencies do not
- **Max 20 famous places** per city (enforced in admin)
- Chat messages are stored for **180 days** then expire
- Hotel booking with **card** = instant confirmation (simulated)
- **Real-time** events: new messages, booking updates, partner approval

---

## 🔌 Admin Panel

Visit `/admin/` and login with your superuser.

Key admin tasks:
- **Approve partners**: Partners → Partner → select → "Approve selected partners"
- **Add cities**: Locations → Cities → Add
- **Add places**: Locations → Places → Add (with up to 5 images)

---

## 🧩 Apps Summary

| App | Models |
|-----|--------|
| `accounts` | User (custom AbstractUser) |
| `partners` | Partner, Hotel, Restaurant, Coffee, Agency |
| `locations` | City, Place, PlaceImage |
| `posts` | Post, PostImage, Comment, Like |
| `booking` | Booking, BookingRequest |
| `flights` | Flight |
| `chat` | Conversation, Message |
| `notifications` | Notification |
| `reviews` | Rating |

---

## 🚀 Tech Stack

- **Backend**: Django 5 (MVT, no DRF)
- **Real-time**: Django Channels + WebSockets
- **Database**: SQLite (dev) / MySQL (prod)
- **Frontend**: Django Templates + vanilla CSS/JS
- **Auth**: Django built-in auth with custom User model
