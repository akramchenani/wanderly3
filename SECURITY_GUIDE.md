# Guide de Sécurité Wanderly — Fichiers d'Implémentation
# ========================================================
# Ce fichier explique chaque mesure de sécurité livrée et comment l'appliquer.

## Structure des fichiers fournis

```
wanderly_security/
├── wanderly/
│   └── settings_production.py    ← Remplace settings.py en production
├── security/
│   └── views_and_decorators.py   ← Helpers RBAC + fichier privé + webhook
├── chat/management/commands/
│   └── purge_old_messages.py     ← Commande de purge RGPD
├── nginx/
│   └── wanderly.conf             ← Config Nginx production
└── SECURITY_GUIDE.md             ← Ce fichier
```

---

## Section 1 — Configuration Django (settings_production.py)

### 1.1 – Désactiver DEBUG
```python
DEBUG = False
```
En production DEBUG=True expose les tracebacks complets (chemins de fichiers,
variables locales, etc.) à n'importe quel visiteur.  DEBUG doit toujours être
False en production.

### 1.2 – SECRET_KEY via variable d'environnement
```python
SECRET_KEY = config('SECRET_KEY')   # jamais en dur dans le code
```
Installation :
```bash
pip install python-decouple
echo "SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" >> /srv/wanderly/.env
```

### 1.3 – HTTPS et cookies sécurisés
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 1800        # déconnexion après 30 min d'inactivité
```
Ces paramètres empêchent que les cookies de session et CSRF soient envoyés
en clair sur HTTP (vol de session via sniffing réseau).

---

## Section 2 — Protection contre XSS et injections SQL

### 2.1 – ORM Django et injections SQL
L'ORM Django utilise des requêtes paramétrées.  Toute valeur utilisateur
passée via `.filter()`, `.get()`, `.exclude()` est automatiquement échappée :

```python
# SÛRE — l'ORM paramétrise la valeur
User.objects.filter(username=request.POST['username'])

# DANGEREUSE — appel SQL brut avec interpolation de chaîne
User.objects.raw(f"SELECT * FROM auth_user WHERE username = '{username}'")

# SÛRE — appel SQL brut avec paramètres
User.objects.raw("SELECT * FROM auth_user WHERE username = %s", [username])
```

### 2.2 – Protection XSS dans les templates Django
Le moteur de template Django échappe automatiquement les variables :
`{{ user.bio }}` → `&lt;script&gt;` si le bio contient `<script>`.

**Danger : le filtre `|safe` désactive l'échappement automatique.**
```django
{# DANGEREUX si `content` vient d'un utilisateur #}
{{ post.content|safe }}

{# SÛRE — laissez Django échapper #}
{{ post.content }}
```
Ne jamais utiliser `|safe` sur des données issues de la base de données.

### 2.3 – CSRF Token
Tous les formulaires POST doivent inclure le token CSRF :
```django
<form method="post">
    {% csrf_token %}
    ...
</form>
```
Le middleware `django.middleware.csrf.CsrfViewMiddleware` vérifie ce token
sur chaque requête POST et rejette les soumissions sans token valide.

---

## Section 3 — RBAC (Contrôle d'accès basé sur les rôles)

Depuis `security/views_and_decorators.py` :

### Vues basées sur fonctions
```python
from security.views_and_decorators import approved_partner_required, admin_required

@approved_partner_required          # login + partner.is_approved == True
def partner_dashboard(request):
    ...

@admin_required                     # login + role == 'admin' ou is_superuser
def admin_panel(request):
    ...
```

### Vues basées sur classes
```python
from security.views_and_decorators import OwnerRequiredMixin

class PostUpdateView(OwnerRequiredMixin, UpdateView):
    model = Post
    owner_field = 'author'   # champ sur le modèle Post
    fields = ['title', 'content']
```

---

## Section 4 — Documents légaux (fichiers privés)

### 4.1 – Stockage hors de MEDIA_ROOT
```python
# settings_production.py
PRIVATE_MEDIA_ROOT = '/srv/wanderly/private_media'
```
Créer le répertoire :
```bash
sudo mkdir -p /srv/wanderly/private_media
sudo chown www-data:www-data /srv/wanderly/private_media
sudo chmod 750 /srv/wanderly/private_media
```
Modifier le modèle Partner pour pointer vers ce répertoire :
```python
# partners/models.py
from django.conf import settings
import os

def private_upload_path(instance, filename):
    return os.path.join(settings.PRIVATE_MEDIA_ROOT, 'verifications', filename)

class Partner(models.Model):
    verification_document = models.FileField(
        upload_to=private_upload_path,
        blank=True, null=True
    )
```

### 4.2 – URL protégée par X-Accel-Redirect
```python
# partners/urls.py
from django.urls import path
from security.views_and_decorators import serve_verification_document

urlpatterns = [
    path('document/<int:partner_pk>/', serve_verification_document, name='partner_document'),
]
```
La vue vérifie que l'utilisateur est connecté ET est propriétaire du document
(ou admin) avant de laisser Nginx servir le fichier.

---

## Section 5 — Double authentification (MFA) pour Admins/Partenaires

### Installation
```bash
pip install django-two-factor-auth[phonenumbers]
pip install django-otp qrcode
```

### settings_production.py (ajouts)
```python
INSTALLED_APPS += [
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
]

MIDDLEWARE += [
    'django_otp.middleware.OTPMiddleware',
]

LOGIN_URL = 'two_factor:login'

TWO_FACTOR_FORCE_OTP_ADMIN = True       # force MFA dans l'admin Django
TWO_FACTOR_PATCH_ADMIN = True
```

### urls.py (ajout)
```python
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('', include(tf_urls)),
    ...
]
```

### Forcer MFA pour les partenaires (decorator personnalisé)
```python
from django_otp import user_has_device

def mfa_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not user_has_device(request.user) or not request.user.is_verified():
            messages.warning(request, 'Veuillez activer la double authentification.')
            return redirect('two_factor:setup')
        return view_func(request, *args, **kwargs)
    return _wrapped
```

---

## Section 6 — Paiements (PCI-DSS)

**Règle fondamentale : ne jamais stocker les numéros de carte bancaire.**

### Pourquoi utiliser Stripe/Braintree ?
Ces services sont certifiés PCI-DSS niveau 1 et gèrent la tokenisation :
le navigateur du client envoie les données de carte directement à Stripe
(via stripe.js), qui retourne un token.  Wanderly ne voit jamais le numéro
de carte — seulement le token.

### Étapes clés d'une intégration Stripe
1. Le frontend charge `stripe.js` depuis Stripe (jamais depuis votre serveur).
2. L'utilisateur saisit ses données de carte dans un iframe Stripe (Stripe Elements).
3. Stripe retourne un `PaymentIntent client_secret` à votre frontend.
4. Le frontend confirme le paiement auprès de Stripe.
5. Stripe envoie un webhook POST à `/payments/webhook/` pour confirmer.
6. Votre vue `stripe_webhook()` valide la signature et met à jour la réservation.

Le webhook (`security/views_and_decorators.py`) utilise
`stripe.Webhook.construct_event()` pour vérifier que l'événement provient
bien de Stripe via HMAC-SHA256.

---

## Section 7 — Purge des messages (RGPD)

```bash
# Créer les répertoires nécessaires
mkdir -p wander/chat/management/commands
touch wander/chat/management/__init__.py
touch wander/chat/management/commands/__init__.py

# Copier le fichier fourni
cp purge_old_messages.py wander/chat/management/commands/

# Test à blanc
python manage.py purge_old_messages --dry-run

# Exécution réelle
python manage.py purge_old_messages

# Cron (tous les jours à 3h du matin)
(crontab -l; echo "0 3 * * * /srv/wanderly/venv/bin/python /srv/wanderly/manage.py purge_old_messages >> /var/log/wanderly/purge.log 2>&1") | crontab -
```

---

## Section 8 — Déploiement Nginx

```bash
# Copier la configuration
sudo cp nginx/wanderly.conf /etc/nginx/sites-available/wanderly
sudo ln -s /etc/nginx/sites-available/wanderly /etc/nginx/sites-enabled/

# Obtenir un certificat Let's Encrypt
sudo certbot --nginx -d wanderly.com -d www.wanderly.com

# Tester et recharger Nginx
sudo nginx -t && sudo systemctl reload nginx
```

---

## Section 9 — Audit de dépendances (CI/CD)

```bash
# Vérification manuelle des vulnérabilités connues
pip install pip-audit
pip-audit

# Intégration GitHub Actions (.github/workflows/security.yml)
```

```yaml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt
```

---

## Section 10 — Monitoring (Sentry)

```bash
pip install sentry-sdk
```

```python
# settings_production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,   # IMPORTANT: n'envoie pas d'IP ou d'emails à Sentry
)
```

Les erreurs 500, les requêtes SQL lentes et les exceptions non gérées seront
remontées dans votre tableau de bord Sentry en temps réel.
