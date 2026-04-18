"""
Wanderly — Full SQLite Seeder
=================================
Run:  python manage_seed.py

pip install requests Pillow
"""
import os, sys, django, requests, decimal
from datetime import date, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanderly.settings')
django.setup()

from django.core.files.base import ContentFile
from accounts.models import User
from locations.models import City, Place, PlaceImage
from partners.models import Partner, Hotel, Restaurant, Coffee, Agency
from posts.models import Post, PostImage
from flights.models import Flight
from reviews.models import Rating

# ─── image helper ────────────────────────────────────────────────────────────
def fetch(url, w=800, h=600):
    try:
        r = requests.get(f"{url}?w={w}&h={h}&fit=crop&q=80", timeout=15)
        if r.status_code == 200:
            return ContentFile(r.content)
    except Exception as e:
        print(f"    [img error] {e}")
    return None

def city_img(city, url):
    d = fetch(url, 1200, 800)
    if d: city.cover_image.save(f"city_{city.pk}.jpg", d, save=True)

def partner_img(p, url):
    d = fetch(url, 400, 400)
    if d: p.profile_photo.save(f"partner_{p.pk}.jpg", d, save=True)

def place_img(place, url):
    d = fetch(url, 800, 600)
    if d:
        pi = PlaceImage(place=place)
        pi.image.save(f"place_{place.pk}.jpg", d, save=True)

def post_img(post, url):
    d = fetch(url, 800, 600)
    if d:
        pi = PostImage(post=post)
        pi.image.save(f"post_{post.pk}.jpg", d, save=True)

# ─── user/partner helpers ─────────────────────────────────────────────────────
def get_or_create_user(username, full_name, pw="partner123"):
    if User.objects.filter(username=username).exists():
        return User.objects.get(username=username)
    parts = full_name.split(" ", 1)
    return User.objects.create_user(username=username, password=pw, role='partner',
        first_name=parts[0], last_name=parts[1] if len(parts)>1 else "")

def get_or_create_partner(username, full_name, ptype, desc, phone):
    u = get_or_create_user(username, full_name)
    if hasattr(u, 'partner'):
        return u.partner, False
    p = Partner.objects.create(user=u, partner_type=ptype, phone=phone,
        description=desc, is_approved=True,
        verification_document="verifications/sample.pdf")
    return p, True

# ═════════════════════════════════════════════════════════════════════════════
# SEED DATA — 8 cities
# ═════════════════════════════════════════════════════════════════════════════
CITIES = [
  {
    "name": "Paris",
    "desc": "Capital of France, known for art, romance, and iconic landmarks.",
    "cover": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
    "places": [
      ("Eiffel Tower","The iconic iron lattice tower on the Champ de Mars, symbol of Paris.","https://images.unsplash.com/photo-1543340713-8a2a0d94b5c4"),
      ("Louvre Museum","World's largest art museum, home to the Mona Lisa and Venus de Milo.","https://images.unsplash.com/photo-1549887534-3ec93abae2f2"),
      ("Notre-Dame Cathedral","Medieval Gothic masterpiece on the Ile de la Cite.","https://images.unsplash.com/photo-1522093007474-d86e9bf7ba6f"),
      ("Montmartre","Bohemian hilltop district with the Sacré-Coeur basilica and artists.","https://images.unsplash.com/photo-1508057198894-247b23fe5ade"),
      ("Seine River","The river that winds through Paris, lined with bookstalls and bridges.","https://images.unsplash.com/photo-1431274172761-fca41d930114"),
    ],
    "hotels": [
      ("le_meurice_paris","Le Meurice","Opulent palace hotel on Rue de Rivoli facing the Tuileries Garden.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.9,"+33 1 44 58 10 10",450),
      ("shangri_la_paris","Shangri-La Paris","Former Bonaparte mansion with Eiffel Tower views.","https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",4.8,"+33 1 53 67 19 98",520),
      ("hotel_lutetia","Hotel Lutetia","Art Deco landmark on the Left Bank beloved by artists.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.7,"+33 1 49 54 46 00",380),
      ("hotel_regina_louvre","Hotel Regina Louvre","Belle Epoque elegance steps from the Louvre.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.6,"+33 1 42 60 31 10",290),
      ("pullman_tour_eiffel","Pullman Tour Eiffel","Contemporary hotel with breathtaking Eiffel Tower panoramas.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.5,"+33 1 44 38 56 00",260),
    ],
    "restaurants": [
      ("le_grand_vefour","Le Grand Vefour","Legendary 18th-century restaurant under the arches of Palais-Royal.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",4.9,"+33 1 42 96 56 27"),
      ("septime_paris","Septime","Innovative neo-bistrot in Bastille with seasonal produce.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.8,"+33 1 43 67 38 29"),
      ("chez_jeannette","Chez Jeannette","Classic Parisian brasserie in the 10th arrondissement.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.5,"+33 1 47 70 30 89"),
    ],
    "cafes": [
      ("cafe_de_flore","Cafe de Flore","Legendary Saint-Germain café frequented by Sartre and de Beauvoir.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+33 1 45 48 55 26"),
      ("les_deux_magots","Les Deux Magots","Historic literary café on Place Saint-Germain-des-Prés.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+33 1 45 48 55 25"),
      ("coutume_cafe","Coutume Cafe","Specialty coffee pioneer, known for single-origin brews.","https://images.unsplash.com/photo-1521017432531-fbd92d768814","+33 1 45 51 50 47"),
      ("kb_cafeshop","KB CafeShop","Australian-style café in the 9th, beloved for flat whites.","https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb","+33 1 56 92 12 41"),
      ("holybelly","Holybelly Cafe","Canal Saint-Martin spot famous for pancakes and artisan coffee.","https://images.unsplash.com/photo-1554118811-1e0d58224f24","+33 9 73 60 13 64"),
    ],
    "agencies": [
      ("paris_city_vision","Paris City Vision","Full-day tours and skip-the-line tickets across Paris.","https://images.unsplash.com/photo-1521791136064-7986c2920216","+33 1 44 55 61 00"),
      ("getyourguide_paris","GetYourGuide Paris","Book guided tours and activities across the city.","https://images.unsplash.com/photo-1502920917128-1aa500764ce7","+33 1 80 96 51 00"),
      ("viator_france","Viator France","Trusted platform for Paris tours and day trips.","https://images.unsplash.com/photo-1488646953014-85cb44e25828","+33 1 42 71 30 00"),
      ("localers_paris","Localers Paris","Local expert guides for authentic neighbourhood walking tours.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+33 6 12 34 56 78"),
    ],
  },
  {
    "name": "Dubai",
    "desc": "A dazzling city of skyscrapers, luxury malls, and golden desert adventures.",
    "cover": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c",
    "places": [
      ("Burj Khalifa","World's tallest building at 828 m with a 148-floor observation deck.","https://images.unsplash.com/photo-1547623641-d2c56c03e2a7"),
      ("Palm Jumeirah","Palm-shaped artificial island with luxury resorts and residences.","https://images.unsplash.com/photo-1580674684081-7617fbf3d745"),
      ("Dubai Marina","Glamorous waterfront district of skyscrapers, yachts and dining.","https://images.unsplash.com/photo-1579208575657-c595a05383b7"),
      ("Desert Safari","Thrilling dune bashing followed by a traditional Bedouin camp dinner.","https://images.unsplash.com/photo-1547234935-80c7145ec969"),
      ("Dubai Mall","World's largest mall with over 1,200 stores and an indoor aquarium.","https://images.unsplash.com/photo-1526495124232-a04e1849168c"),
    ],
    "hotels": [
      ("burj_al_arab","Burj Al Arab","The world's most luxurious hotel, shaped like a sail on its own island.","https://images.unsplash.com/photo-1582719508461-905c673771fd",5.0,"+971 4 301 7777",900),
      ("atlantis_palm","Atlantis The Palm","Iconic resort on Palm Jumeirah with waterpark and marine habitat.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.8,"+971 4 426 2000",550),
      ("address_downtown","Address Downtown Dubai","Ultra-modern tower steps from Burj Khalifa and Dubai Mall.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.7,"+971 4 436 8888",420),
      ("jumeirah_beach_hotel","Jumeirah Beach Hotel","Wave-shaped beachfront hotel with direct Jumeirah Beach access.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.6,"+971 4 348 0000",380),
      ("one_only_royal_mirage","One&Only Royal Mirage","Arabian-inspired luxury resort on a private stretch of beach.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.9,"+971 4 399 9999",700),
    ],
    "restaurants": [
      ("nobu_dubai","Nobu Dubai","Celebrity chef Nobu Matsuhisa's iconic Japanese-Peruvian fusion restaurant.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",4.8,"+971 4 426 2626"),
      ("zuma_dubai","Zuma Dubai","Award-winning contemporary Japanese izakaya dining in DIFC.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.9,"+971 4 425 5660"),
      ("coya_dubai","Coya Dubai","Vibrant Peruvian restaurant with bold flavours in Four Seasons.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.7,"+971 4 316 9600"),
    ],
    "cafes": [
      ("dubai_brew","Dubai Brew","Specialty coffee roaster in Alserkal Avenue with curated single-origins.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+971 4 333 2299"),
      ("the_sum_of_us","The Sum of Us","Industrial-chic bakery-café famous for sourdough and cold brew.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+971 4 323 5222"),
      ("nightjar_coffee","Nightjar Coffee","Award-winning café known for meticulously crafted espresso drinks.","https://images.unsplash.com/photo-1521017432531-fbd92d768814","+971 4 244 6180"),
      ("cafe_rider","Cafe Rider","Motorcycle-themed café in Al Quoz beloved by creatives.","https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb","+971 4 379 5398"),
    ],
    "agencies": [
      ("arabia_horizons","Arabia Horizons","Award-winning DMC specialising in desert safaris and luxury experiences.","https://images.unsplash.com/photo-1521791136064-7986c2920216","+971 4 343 9800"),
      ("dnata_travel","dnata Travel","One of the world's largest travel management companies.","https://images.unsplash.com/photo-1488646953014-85cb44e25828","+971 4 316 6666"),
      ("big_bus_dubai","Big Bus Dubai","Hop-on hop-off open-top bus covering all major Dubai attractions.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+971 4 340 7709"),
    ],
  },
  {
    "name": "Istanbul",
    "desc": "A timeless city where East meets West, spanning two continents across the Bosphorus.",
    "cover": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200",
    "places": [
      ("Hagia Sophia","Iconic 6th-century masterpiece — cathedral, mosque, and now museum.","https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b"),
      ("Blue Mosque","Sultan Ahmed Mosque with six minarets and exquisite blue Iznik tiles.","https://images.unsplash.com/photo-1527838832700-5059252407fa"),
      ("Topkapi Palace","Opulent palace that served as the heart of the Ottoman Empire.","https://images.unsplash.com/photo-1570939274717-7eda259b50ed"),
      ("Grand Bazaar","One of the world's oldest covered markets with over 4,000 shops.","https://images.unsplash.com/photo-1547223989-1d8672c0adc0"),
      ("Bosphorus","The strait dividing Europe and Asia, best explored by sunset cruise.","https://images.unsplash.com/photo-1584518398598-e90e60a0c9c6"),
    ],
    "hotels": [
      ("pera_palace","Pera Palace Hotel","Legendary 1892 grand hotel where Agatha Christie wrote Orient Express.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.9,"+90 212 377 4000",350),
      ("four_seasons_bosphorus","Four Seasons Bosphorus","Restored 19th-century Ottoman palace on the Bosphorus shores.","https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",4.8,"+90 212 381 4000",480),
      ("ciragan_palace","Ciragan Palace Kempinski","Spectacular palace with private terrace pools over the Bosphorus.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.8,"+90 212 326 4646",520),
      ("soho_house_istanbul","Soho House Istanbul","Members club and boutique hotel in vibrant Beyoglu district.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.6,"+90 212 377 1010",280),
      ("swissotel_istanbul","Swissotel The Bosphorus","Contemporary hotel with panoramic city and sea views.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.5,"+90 212 326 1100",240),
    ],
    "restaurants": [
      ("mikla_istanbul","Mikla","Rooftop fine dining showcasing Anatolian ingredients with modern flair.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",4.9,"+90 212 293 5656"),
      ("ciya_sofrasi","Ciya Sofrasi","Legendary restaurant in Kadikoy serving rare regional Turkish dishes.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.8,"+90 216 330 3190"),
      ("karakoy_lokantasi","Karakoy Lokantasi","Chic neighbourhood restaurant with elevated traditional Turkish fare.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.7,"+90 212 292 4455"),
    ],
    "cafes": [
      ("mandabatmaz","Mandabatmaz","Tiny legendary spot on Istiklal serving the thickest Turkish coffee.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+90 212 293 2800"),
      ("kronotrop","Kronotrop","Istanbul's best specialty coffee with a focus on craft brewing.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+90 212 245 0692"),
      ("walter_coffee","Walter's Coffee","Breaking Bad themed café with chemistry-set pour-overs.","https://images.unsplash.com/photo-1554118811-1e0d58224f24","+90 212 292 1234"),
      ("urban_coffee_ist","Urban Coffee Istanbul","Light-filled café in Nisantasi with great brunch and artisan roasts.","https://images.unsplash.com/photo-1521017432531-fbd92d768814","+90 212 219 9988"),
    ],
    "agencies": [
      ("istanbul_walks","Istanbul Walks","Expert-led walking tours revealing hidden history of the old city.","https://images.unsplash.com/photo-1521791136064-7986c2920216","+90 212 516 6300"),
      ("bosphorus_tours","Bosphorus Tours","Scenic boat tours, sunset cruises and private yacht charters.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+90 212 528 0990"),
      ("turk_tour","Turk Tour","Full-service DMC offering customised private Turkey itineraries.","https://images.unsplash.com/photo-1488646953014-85cb44e25828","+90 212 232 7272"),
    ],
  },
  {
    "name": "Rome",
    "desc": "The Eternal City — 3,000 years of art, ruins, cuisine and la dolce vita.",
    "cover": "https://images.unsplash.com/photo-1552832230-c0197dd311b5",
    "places": [
      ("Colosseum","The greatest Roman amphitheatre, built in 70–80 AD for gladiatorial combat.","https://images.unsplash.com/photo-1555992336-03a23c7b20ee"),
      ("Vatican Museums","Vast complex housing the Sistine Chapel and Raphael's masterful Rooms.","https://images.unsplash.com/photo-1531572753322-ad063cecc140"),
      ("Trevi Fountain","World's most famous fountain — toss a coin to ensure your return to Rome.","https://images.unsplash.com/photo-1552832230-c0197dd617c9"),
      ("Pantheon","Best-preserved Roman temple, built around 125 AD with its perfect dome.","https://images.unsplash.com/photo-1529260830199-42c24126f198"),
      ("Roman Forum","Ancient heart of Rome, where citizens gathered in the shadow of temples.","https://images.unsplash.com/photo-1555992643-a9f25acdd29e"),
    ],
    "hotels": [
      ("hotel_de_russie","Hotel de Russie","Elegant 5-star retreat near Piazza del Popolo with a secret garden.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.9,"+39 06 328881",420),
      ("rome_cavalieri","Rome Cavalieri","Hilltop luxury hotel with a priceless art collection and city panoramas.","https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",4.8,"+39 06 35091",390),
      ("hotel_eden_rome","Hotel Eden Rome","Timeless luxury overlooking the Spanish Steps and Trinita dei Monti.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.8,"+39 06 478121",460),
      ("palazzo_manfredi","Palazzo Manfredi","Boutique hotel with direct Colosseum views and a Michelin rooftop.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.7,"+39 06 77591380",350),
      ("villa_borghese_hotel","Villa Borghese Hotel","Charming boutique steps from the Borghese Gallery and gardens.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.7,"+39 06 8558553",280),
    ],
    "restaurants": [
      ("la_pergola_rome","La Pergola","Rome's only three-Michelin-star restaurant with panoramic city views.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",5.0,"+39 06 3509 2152"),
      ("roscioli_rome","Roscioli","Iconic Roman deli-restaurant celebrated for cacio e pepe and cured meats.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.8,"+39 06 687 5287"),
      ("da_enzo_al_29","Da Enzo al 29","Classic trattoria in Trastevere serving authentic Roman cucina povera.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.7,"+39 06 581 2260"),
    ],
    "cafes": [
      ("sant_eustachio","Sant Eustachio il Caffe","Iconic Roman roastery near the Pantheon, famous for its Gran Caffe.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+39 06 6880 2048"),
      ("tazza_d_oro","Tazza d'Oro","Historic coffee house serving Rome's finest granita di caffe.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+39 06 678 9792"),
      ("roscioli_caffe","Roscioli Caffe","Beloved neighbourhood bar known for perfect cornetto and cappuccino.","https://images.unsplash.com/photo-1554118811-1e0d58224f24","+39 06 8916 5330"),
      ("caffe_peru","Caffe Peru","Bohemian haunt in Testaccio frequented by Roman intellectuals.","https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb","+39 06 574 2415"),
    ],
    "agencies": [
      ("through_eternity","Through Eternity","Award-winning guided tours of the Vatican, Colosseum and hidden Rome.","https://images.unsplash.com/photo-1502920917128-1aa500764ce7","+39 06 7009 3636"),
      ("rome_walking_tours","Rome Walking Tours","Small-group walking tours of the ancient city.","https://images.unsplash.com/photo-1488646953014-85cb44e25828","+39 06 482 3185"),
      ("italy_bite","Italy Bite","Food tours sampling Roman culinary traditions in Trastevere.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+39 06 4523 2374"),
    ],
  },
  {
    "name": "Barcelona",
    "desc": "Gaudi's city — a vibrant Mediterranean capital of architecture, beaches and cuisine.",
    "cover": "https://images.unsplash.com/photo-1511527661048-7fe73d85e9a4",
    "places": [
      ("Sagrada Familia","Gaudi's breathtaking unfinished basilica, under construction since 1882.","https://images.unsplash.com/photo-1583422409516-2895a77efded"),
      ("Park Guell","Gaudi's whimsical hilltop park with mosaics and panoramic city views.","https://images.unsplash.com/photo-1539037116277-4db20889f2d4"),
      ("La Rambla","The city's famous tree-lined pedestrian boulevard to the seafront.","https://images.unsplash.com/photo-1559682468-a6a29e7d9517"),
      ("Casa Batllo","Gaudi's masterpiece on Passeig de Gracia, nicknamed the House of Bones.","https://images.unsplash.com/photo-1564221710304-0b37c8b9d729"),
      ("Barceloneta Beach","The city's most popular urban beach along the Mediterranean coast.","https://images.unsplash.com/photo-1558618666-fcd25c85cd64"),
    ],
    "hotels": [
      ("hotel_arts_bcn","Hotel Arts Barcelona","Ritz-Carlton luxury in two 44-floor towers overlooking the Mediterranean.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.9,"+34 93 221 1000",480),
      ("w_barcelona","W Barcelona","Sail-shaped hotel on the seafront with rooftop pool and sea views.","https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",4.7,"+34 93 295 2800",420),
      ("mandarin_bcn","Mandarin Oriental Barcelona","Sleek luxury hotel on Passeig de Gracia in the heart of the Eixample.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.8,"+34 93 151 8888",500),
      ("casa_fuster","Grand Hotel Casa Fuster","Modernist 1908 landmark restored to its original Art Nouveau splendour.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.6,"+34 93 255 3000",320),
      ("majestic_bcn","Majestic Hotel Barcelona","Classic grand hotel on Passeig de Gracia since 1918.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.7,"+34 93 488 1717",360),
    ],
    "restaurants": [
      ("disfrutar_bcn","Disfrutar","Two-Michelin-star avant-garde restaurant by elBulli alumni.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",4.9,"+34 93 348 6896"),
      ("tickets_bcn","Tickets","Albert Adria's playful tapas bar with a fun creative menu.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.8,"+34 93 292 4254"),
      ("la_cova_fumada","La Cova Fumada","The original inventor of the bombas snack and fresh seafood.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.6,"+34 93 221 4061"),
    ],
    "cafes": [
      ("nomad_coffee","Nomad Coffee","Barcelona's leading specialty roastery with its flagship lab in Poblenou.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+34 93 310 7853"),
      ("satan_coffee","Satan's Coffee Corner","Tiny gem in Gothic Quarter serving outstanding espresso.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+34 93 000 0001"),
      ("federal_cafe","Federal Cafe Barcelona","Brunch institution in Sant Antoni known for avocado toast and flat whites.","https://images.unsplash.com/photo-1554118811-1e0d58224f24","+34 93 187 3607"),
      ("el_magnifico","Cafes El Magnifico","Family-run coffee importer since 1919 with legendary single-origin blends.","https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb","+34 93 319 3975"),
    ],
    "agencies": [
      ("bcn_day_tours","Barcelona Day Tours","Private guided tours of Sagrada Familia, Park Guell and Gothic Quarter.","https://images.unsplash.com/photo-1521791136064-7986c2920216","+34 93 268 2422"),
      ("runner_bean","Runner Bean Tours","Pay-what-you-wish free walking tours covering city highlights daily.","https://images.unsplash.com/photo-1502920917128-1aa500764ce7","+34 93 000 0002"),
      ("devour_bcn","Devour Barcelona","Authentic food and wine tours exploring Boqueria, tapas bars and cava.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+34 93 000 0003"),
    ],
  },
  {
    "name": "London",
    "desc": "A world capital of history, culture, theatre and extraordinary diversity.",
    "cover": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad",
    "places": [
      ("Big Ben","The iconic clock tower at the north end of the Palace of Westminster.","https://images.unsplash.com/photo-1529981188441-2cc7bb3e5e0c"),
      ("Tower Bridge","Victorian Gothic drawbridge spanning the Thames, opened in 1894.","https://images.unsplash.com/photo-1529953977-a98786b1b4f2"),
      ("London Eye","World's tallest cantilevered observation wheel on the South Bank.","https://images.unsplash.com/photo-1534430480872-3498386e7856"),
      ("Buckingham Palace","The official London residence of the British monarch since 1837.","https://images.unsplash.com/photo-1526129318478-62ed807ebdf9"),
      ("Hyde Park","One of London's eight Royal Parks and a green sanctuary in the city centre.","https://images.unsplash.com/photo-1533929736458-ca588d08c8be"),
    ],
    "hotels": [
      ("the_savoy","The Savoy","London's most famous hotel, opened in 1889 on the Strand.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.9,"+44 20 7836 4343",550),
      ("claridges","Claridges","Mayfair's quintessential Art Deco grande dame and long-time royal favourite.","https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",4.9,"+44 20 7629 8860",620),
      ("shangri_la_shard","Shangri-La at The Shard","Luxury hotel on floors 34-52 of Europe's tallest building.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.8,"+44 20 7234 8000",480),
      ("ham_yard_hotel","Ham Yard Hotel","Quirky Firmdale boutique with a private garden in the heart of Soho.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.7,"+44 20 3642 2000",380),
      ("south_place","South Place Hotel","London's first true boutique hotel in the City near Liverpool Street.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.7,"+44 20 3503 0000",320),
    ],
    "restaurants": [
      ("sketch_london","Sketch London","Avant-garde dining in a converted 18th-century townhouse in Mayfair.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",4.8,"+44 20 7659 4500"),
      ("ottolenghi_london","Ottolenghi","Yotam Ottolenghi's celebrated deli and restaurant with vibrant Middle Eastern dishes.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.7,"+44 20 7288 1454"),
      ("dishoom","Dishoom","Bombay-inspired café beloved for its black dal and breakfast bacon naan.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.8,"+44 20 7420 9320"),
    ],
    "cafes": [
      ("monmouth_coffee","Monmouth Coffee","Iconic specialty roaster in Borough Market — birthplace of London coffee culture.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+44 20 7645 3560"),
      ("ozone_coffee","Ozone Coffee Roasters","New Zealand-inspired roastery in Shoreditch with exceptional single-origins.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+44 20 7490 1039"),
      ("look_mum_no_hands","Look Mum No Hands","Cycling-themed café and workshop in Clerkenwell.","https://images.unsplash.com/photo-1554118811-1e0d58224f24","+44 20 7253 1025"),
      ("cafe_st_ali","Cafe St Ali London","Melbourne-style café in South London bringing Antipodean brunch.","https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb","+44 20 7378 9990"),
    ],
    "agencies": [
      ("london_walks","London Walks","World's biggest walking tour company with daily themed tours.","https://images.unsplash.com/photo-1521791136064-7986c2920216","+44 20 7624 3978"),
      ("golden_tours","Golden Tours","Britain's leading open-top bus tour operator with live guides.","https://images.unsplash.com/photo-1502920917128-1aa500764ce7","+44 20 7630 2028"),
      ("eating_london","Eating London Tours","Award-winning food tours of East London and Borough Market.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+44 20 3697 4747"),
    ],
  },
  {
    "name": "New York",
    "desc": "The city that never sleeps — a global capital of art, finance and culture.",
    "cover": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9",
    "places": [
      ("Statue of Liberty","Iconic copper statue gifted by France, a symbol of freedom since 1886.","https://images.unsplash.com/photo-1549294413-26f195200c16"),
      ("Central Park","840 acres of green refuge in the heart of Manhattan — the city's backyard.","https://images.unsplash.com/photo-1568515387631-8b650bbcdb90"),
      ("Times Square","Neon-lit crossroads of the world where Broadway meets Seventh Avenue.","https://images.unsplash.com/photo-1534430480872-3498386e7856"),
      ("Brooklyn Bridge","Iconic 1883 suspension bridge with spectacular Manhattan skyline views.","https://images.unsplash.com/photo-1541963463532-d68292c34b19"),
      ("Empire State Building","Art Deco skyscraper and New York's defining landmark since 1931.","https://images.unsplash.com/photo-1560969184-10fe8719e047"),
    ],
    "hotels": [
      ("the_plaza_nyc","The Plaza Hotel","National Historic Landmark on Fifth Avenue overlooking Central Park.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.9,"+1 212 759 3000",580),
      ("standard_highline","The Standard High Line","Provocative design hotel straddling the High Line with Hudson River views.","https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",4.7,"+1 212 645 4646",420),
      ("gramercy_park","Gramercy Park Hotel","Bohemian luxury hotel with access to Manhattan's only private park.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.6,"+1 212 920 3300",360),
      ("the_mark_nyc","The Mark Hotel","Refined luxury on the Upper East Side steps from the Metropolitan Museum.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.8,"+1 212 744 4300",520),
      ("arlo_soho","Arlo SoHo","Modern hotel in SoHo with a rooftop pool and vibrant social spaces.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.5,"+1 212 342 7000",280),
    ],
    "restaurants": [
      ("le_bernardin","Le Bernardin","Eric Ripert's world-famous four-star French seafood restaurant.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",5.0,"+1 212 554 1515"),
      ("eleven_madison","Eleven Madison Park","Three-Michelin-star seasonal American dining with stunning park views.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.9,"+1 212 889 0905"),
      ("peter_luger","Peter Luger Steak House","Brooklyn institution since 1887, serving porterhouse for two since forever.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.7,"+1 718 387 7400"),
    ],
    "cafes": [
      ("blue_bottle_nyc","Blue Bottle Coffee NY","Oakland-born coffee obsessives with multiple Manhattan locations.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+1 510 653 3394"),
      ("stumptown_nyc","Stumptown Coffee NY","Portland roastery beloved for Hairbender espresso in the West Village.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+1 212 337 0750"),
      ("abraco","Abraco NYC","Tiny East Village espresso bar with the best olive oil cake in New York.","https://images.unsplash.com/photo-1554118811-1e0d58224f24","+1 212 388 9731"),
      ("coffee_project_ny","Coffee Project NY","Award-winning East Village café known for coffee flights and deconstructed latte.","https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb","+1 212 228 7888"),
    ],
    "agencies": [
      ("nyc_tours","NYC Tours","Comprehensive sightseeing bus tours hitting all five boroughs' landmarks.","https://images.unsplash.com/photo-1521791136064-7986c2920216","+1 212 666 9090"),
      ("foods_of_ny","Foods of New York","Delicious walking food tours through Chelsea Market, SoHo and Greenwich Village.","https://images.unsplash.com/photo-1488646953014-85cb44e25828","+1 212 209 3370"),
      ("bigapple_tours","Big Apple Tours","Guided walking tours of Brooklyn, High Line and outer boroughs.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+1 212 913 9650"),
    ],
  },
  {
    "name": "Tokyo",
    "desc": "A city where ancient temples and neon-lit streets coexist in perfect harmony.",
    "cover": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf",
    "places": [
      ("Shibuya Crossing","World's busiest pedestrian crossing — a mesmerising spectacle at rush hour.","https://images.unsplash.com/photo-1540959733332-eab4deabeeaf"),
      ("Tokyo Tower","The iconic Eiffel-inspired lattice tower soaring 333 m over Shiba Park.","https://images.unsplash.com/photo-1536098561742-ca998e48cbcc"),
      ("Senso-ji","Tokyo's oldest Buddhist temple in Asakusa, accessible via the Thunder Gate.","https://images.unsplash.com/photo-1528360983277-13d401cdc186"),
      ("Akihabara","Electric Town — the global epicentre of anime, manga and gaming culture.","https://images.unsplash.com/photo-1542051841857-5f90071e7989"),
      ("Meiji Shrine","A tranquil Shinto shrine set within a 70-hectare forested park in Harajuku.","https://images.unsplash.com/photo-1553689175-cf8f0a3a3b8b"),
    ],
    "hotels": [
      ("peninsula_tokyo","The Peninsula Tokyo","Ultra-luxurious hotel at the intersection of Marunouchi and Ginza.","https://images.unsplash.com/photo-1566073771259-6a8506099945",4.9,"+81 3 6270 2888",680),
      ("aman_tokyo","Aman Tokyo","Serene Japanese luxury in a 33-floor tower overlooking the Imperial Palace.","https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",4.9,"+81 3 5224 3333",820),
      ("park_hyatt_tokyo","Park Hyatt Tokyo","Refined hotel from Lost in Translation on the top floors of a skyscraper.","https://images.unsplash.com/photo-1590490360182-c33d57733427",4.8,"+81 3 5322 1234",520),
      ("andaz_tokyo","Andaz Tokyo","Contemporary hotel with spectacular 52nd-floor views of the bay.","https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",4.7,"+81 3 3270 8800",460),
      ("hotel_okura","Hotel Okura Tokyo","Heritage luxury where mid-century Japanese modernism meets impeccable service.","https://images.unsplash.com/photo-1578898886225-c7c894047899",4.7,"+81 3 3582 0111",380),
    ],
    "restaurants": [
      ("sukiyabashi_jiro","Sukiyabashi Jiro","Legendary three-Michelin-star sushi temple immortalised in Jiro Dreams of Sushi.","https://images.unsplash.com/photo-1414235077428-338989a2e8c0",5.0,"+81 3 3535 3600"),
      ("narisawa","Narisawa","Innovative Satoyama cuisine bridging Japanese tradition and the natural world.","https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",4.9,"+81 3 5785 0799"),
      ("ichiran_tokyo","Ichiran Ramen","Solo-dining ramen booths serving the city's most famous tonkotsu broth.","https://images.unsplash.com/photo-1600891964092-4316c288032e",4.7,"+81 3 3796 6286"),
    ],
    "cafes": [
      ("fuglen_tokyo","Fuglen Tokyo","Oslo-born coffee bar that sparked Tokyo's specialty coffee revolution.","https://images.unsplash.com/photo-1509042239860-f550ce710b93","+81 3 3481 0884"),
      ("onibus_coffee","Onibus Coffee","Neighbourhood roastery in Nakameguro with direct-trade beans and a terrace.","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085","+81 3 6413 9279"),
      ("bear_pond","Bear Pond Espresso","Legendary Shimokitazawa café famed for its Angel Stain espresso shots.","https://images.unsplash.com/photo-1554118811-1e0d58224f24","+81 3 5454 2486"),
      ("streamer_coffee","Streamer Coffee Tokyo","Latte art pioneers from Shibuya serving competition-grade espresso.","https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb","+81 3 6427 3705"),
    ],
    "agencies": [
      ("japan_wonder","Japan Wonder Travel","Expert English-speaking guides for Tokyo tours and cultural experiences.","https://images.unsplash.com/photo-1521791136064-7986c2920216","+81 80 4773 2433"),
      ("sky_hop_bus","Sky Hop Bus Tokyo","Hop-on hop-off sightseeing bus connecting Shibuya, Asakusa and Akihabara.","https://images.unsplash.com/photo-1502920917128-1aa500764ce7","+81 3 5826 4480"),
      ("viator_japan","Viator Japan","Thousands of activities, tours and day trips across Japan bookable online.","https://images.unsplash.com/photo-1526772662000-3f88f10405ff","+81 3 0000 0001"),
    ],
  },
]

# ─── Flight catalogue (30 routes, real airlines) ─────────────────────────────
FLIGHT_CATALOGUE = [
  # (origin, destination, airline, flight_no, price, duration_h)
  ("Paris","Dubai","Air France","AF556",420,"6h 30m"),
  ("Paris","Istanbul","Air France","AF1391",180,"3h 45m"),
  ("Paris","London","Eurostar/Air France","AF820",120,"1h 20m"),
  ("Paris","New York","Air France","AF006",680,"8h 10m"),
  ("Paris","Tokyo","Air France","AF276",980,"14h 00m"),
  ("Paris","Barcelona","Vueling","VY8212",95,"2h 00m"),
  ("Paris","Rome","Air France","AF1136",140,"2h 15m"),
  ("Dubai","Istanbul","Emirates","EK119",280,"3h 50m"),
  ("Dubai","London","Emirates","EK003",620,"7h 20m"),
  ("Dubai","New York","Emirates","EK201",850,"14h 15m"),
  ("Dubai","Tokyo","Emirates","EK319",720,"11h 30m"),
  ("Dubai","Barcelona","Emirates","EK183",520,"7h 45m"),
  ("Dubai","Rome","Emirates","EK097",490,"6h 50m"),
  ("Istanbul","London","Turkish Airlines","TK1979",290,"3h 50m"),
  ("Istanbul","New York","Turkish Airlines","TK001",680,"10h 30m"),
  ("Istanbul","Tokyo","Turkish Airlines","TK023",750,"12h 45m"),
  ("Istanbul","Barcelona","Turkish Airlines","TK1851",230,"3h 25m"),
  ("Istanbul","Rome","Turkish Airlines","TK1867",190,"2h 45m"),
  ("London","New York","British Airways","BA117",540,"7h 30m"),
  ("London","Tokyo","British Airways","BA005",880,"12h 00m"),
  ("London","Barcelona","British Airways","BA472",130,"2h 10m"),
  ("London","Rome","British Airways","BA560",150,"2h 30m"),
  ("New York","Tokyo","American Airlines","AA159",760,"14h 00m"),
  ("New York","Barcelona","Delta","DL194",520,"8h 00m"),
  ("New York","Rome","American Airlines","AA90",580,"9h 30m"),
  ("Tokyo","Barcelona","Japan Airlines","JL7087",1100,"14h 30m"),
  ("Tokyo","Rome","Japan Airlines","JL7089",1050,"13h 45m"),
  ("Barcelona","Rome","Vueling","VY6802",85,"1h 50m"),
  ("Rome","Dubai","Alitalia","AZ791",380,"5h 45m"),
  ("Barcelona","New York","Level","IB2623",430,"9h 15m"),
]

# ═════════════════════════════════════════════════════════════════════════════
def run():
    print("\n" + "="*60)
    print("  Wanderly — Full SQLite Seeder")
    print("="*60)

    # ── Admin + demo users ────────────────────────────────────
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin','admin@wanderly.com','admin123',role='admin')
        print("Created superuser: admin / admin123")

    if not User.objects.filter(username='traveler').exists():
        User.objects.create_user('traveler','traveler@wanderly.com','traveler123',
            role='user', first_name='Alex', last_name='Traveler')
        print("Created demo user:  traveler / traveler123")

    admin_user = User.objects.get(username='admin')

    for city_data in CITIES:
        cname = city_data["name"]
        print(f"\n{'─'*50}  {cname}")

        city, created = City.objects.get_or_create(
            name=cname, defaults={'description': city_data['desc']})
        if created:
            print(f"  City created: {cname}")
            city_img(city, city_data['cover'])
        else:
            print(f"  City exists:  {cname}")

        # Places
        for pname, pdesc, purl in city_data.get('places', []):
            pl, c = Place.objects.get_or_create(name=pname, city=city,
                defaults={'description': pdesc})
            if c:
                print(f"  + Place: {pname}")
                place_img(pl, purl)

        # Hotels
        for uname, fname, desc, photo, rating, phone, price in city_data.get('hotels', []):
            p, c = get_or_create_partner(uname, fname, 'hotel', desc, phone)
            if c:
                hotel = Hotel.objects.create(partner=p, city=city, rating_avg=rating)
                partner_img(p, photo)
                print(f"  + Hotel: {fname}")
                post = Post.objects.create(author=p.user, city=city, post_type='service',
                    title=f"{fname}", description=desc,
                    price=decimal.Decimal(str(price)))
                post_img(post, photo)

        # Restaurants
        for uname, fname, desc, photo, rating, phone in city_data.get('restaurants', []):
            p, c = get_or_create_partner(uname, fname, 'restaurant', desc, phone)
            if c:
                rest = Restaurant.objects.create(partner=p, city=city, rating_avg=rating)
                partner_img(p, photo)
                print(f"  + Restaurant: {fname}")
                post = Post.objects.create(author=p.user, city=city, post_type='service',
                    title=f"{fname}", description=desc, price=decimal.Decimal('45.00'))
                post_img(post, photo)
                # Add a review from admin
                Rating.objects.get_or_create(user=admin_user, partner=p,
                    defaults={'stars': min(5, int(rating)), 'comment': f"Excellent experience at {fname}!"})

        # Cafés
        for uname, fname, desc, photo, phone in city_data.get('cafes', []):
            p, c = get_or_create_partner(uname, fname, 'coffee', desc, phone)
            if c:
                Coffee.objects.create(partner=p, city=city, rating_avg=4.5)
                partner_img(p, photo)
                print(f"  + Cafe: {fname}")
                post = Post.objects.create(author=p.user, city=city, post_type='service',
                    title=f"{fname}", description=desc, price=decimal.Decimal('8.00'))
                post_img(post, photo)

        # Agencies
        for uname, fname, desc, photo, phone in city_data.get('agencies', []):
            p, c = get_or_create_partner(uname, fname, 'agency', desc, phone)
            if c:
                Agency.objects.create(partner=p, rating_avg=4.6)
                partner_img(p, photo)
                print(f"  + Agency: {fname}")

    # ── Flights ───────────────────────────────────────────────
    print(f"\n{'─'*50}  Flights")
    traveler = User.objects.get(username='traveler')
    base_date = date.today() + timedelta(days=30)

    for i, (orig, dest, airline, fno, price, duration) in enumerate(FLIGHT_CATALOGUE):
        dep = base_date + timedelta(days=i * 3)
        Flight.objects.get_or_create(
            user=traveler, origin=orig, destination=dest,
            departure_date=dep, airline=airline, flight_number=fno,
            defaults={
                'flight_type': 'one_way',
                'price': decimal.Decimal(str(price)),
                'status': 'booked',
            }
        )
    print(f"  Created {len(FLIGHT_CATALOGUE)} flights in catalogue")

    print(f"\n{'='*60}")
    print("  Seed complete!")
    print(f"{'='*60}")
    print("  Accounts:")
    print("    Admin:    admin    / admin123")
    print("    Customer: traveler / traveler123")
    print("    Partners: <username> / partner123")
    print("  Admin: http://127.0.0.1:8000/admin/")
    print("  Site:  http://127.0.0.1:8000/\n")

if __name__ == '__main__':
    run()
