"""
Nümunə məlumatları yükləyir:  python manage.py seed_data
Şəkilləri Unsplash-dan yükləyir (internet lazımdır). İnternet yoxdursa, şəkilsiz yaradılır
və frontend öz meyvə şəkillərini göstərir.

  --flush   mövcud məzmunu silib yenidən yaradır
  --no-images  şəkil yükləmədən
"""
import urllib.request
from datetime import timedelta
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    AboutPage,
    Advantage,
    Category,
    CompanyValue,
    HeroSlide,
    News,
    Partner,
    Product,
    SiteSettings,
    Statistic,
)

ASSETS = Path(__file__).resolve().parent.parent.parent / "seed_assets"
UNSPLASH = "https://images.unsplash.com/photo-{}?w=1200&q=80&fm=jpg&fit=crop"

IMG = {
    "basket": "1619566636858-adf3ef46400b",
    "tropical": "1610832958506-aa56368176cf",
    "market": "1488459716781-31db52582fe9",
    "plate": "1490474418585-ba9bad8fd0ea",
    "bowl": "1519996529931-28324d5a630e",
    "shelves": "1542838132-92c53300491e",
    "apples": "1560806887-1e4cd0b6cbd6",
    "apple_close": "1567306226416-28f0efdc88ce",
    "apple": "1568702846914-96b305d2aaeb",
    "pear": "1615484477778-ca3b77940c25",
    "citrus": "1546548970-71785318a17b",
    "tangerine": "1557800636-894a64c1696f",
    "pineapple": "1550258987-190a2d41a8ba",
    "pineapple2": "1490885578174-acda8905c2c6",
    "mango": "1553279768-865429fa0078",
    "mangoes": "1601493700631-2b16ec4b4716",
    "banana": "1571771894821-ce9b6c11b08e",
    "banana2": "1528825871115-3581a5387919",
    "strawberry": "1464965911861-746a04b4bca6",
    "berries": "1596591606975-97ee5cef3a1e",
    "grapes": "1537640538966-79f369143f8f",
    "watermelon": "1563114773-84221bd62daa",
}


class Command(BaseCommand):
    help = "aygarden.az üçün nümunə məlumatları yaradır"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true")
        parser.add_argument("--no-images", action="store_true")

    # ------------------------------------------------------------------
    def _download(self, key):
        if self.no_images:
            return None
        if key in self._cache:
            return self._cache[key]
        try:
            req = urllib.request.Request(UNSPLASH.format(IMG[key]), headers={"User-Agent": "aygarden-seed"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
        except Exception as exc:  # noqa: BLE001
            self.stdout.write(self.style.WARNING(f"  şəkil yüklənmədi ({key}): {exc}"))
            data = None
        self._cache[key] = data
        return data

    def _attach(self, obj, field, key, name=None):
        data = self._download(key)
        if data:
            getattr(obj, field).save(f"{name or key}.jpg", ContentFile(data), save=False)

    def _attach_file(self, obj, field, filename):
        path = ASSETS / filename
        if path.exists():
            getattr(obj, field).save(filename, ContentFile(path.read_bytes()), save=False)

    # ------------------------------------------------------------------
    def handle(self, *args, **opts):
        self.no_images = opts["no_images"]
        self._cache = {}

        if opts["flush"]:
            for model in (Product, Category, News, HeroSlide, Statistic, CompanyValue, Advantage, Partner):
                model.objects.all().delete()
            SiteSettings.objects.all().delete()
            AboutPage.objects.all().delete()

        self.seed_settings()
        self.seed_slides()
        self.seed_statistics()
        self.seed_about()
        self.seed_catalog()
        self.seed_news()
        self.stdout.write(self.style.SUCCESS("✔ Nümunə məlumatlar hazırdır."))

    def seed_settings(self):
        s = SiteSettings.load()
        s.site_name = "aygarden.az"
        s.slogan = "Təbiətin ən təzə nemətləri"
        s.phone = s.phone or "+994 50 123 45 67"
        s.phone_secondary = s.phone_secondary or "+994 12 345 67 89"
        s.whatsapp = s.whatsapp or "994501234567"
        s.email = s.email or "info@aygarden.az"
        s.address = s.address or "Bakı şəhəri, Xətai rayonu, Babək prospekti 25"
        s.working_hours = s.working_hours or "B.e – Şənbə: 09:00 – 18:00"
        s.map_embed_url = s.map_embed_url or (
            "https://www.google.com/maps?q=Baku%2C%20Azerbaijan&output=embed"
        )
        s.facebook = s.facebook or "https://facebook.com/"
        s.instagram = s.instagram or "https://instagram.com/"
        s.linkedin = s.linkedin or "https://linkedin.com/"
        s.youtube = s.youtube or "https://youtube.com/"
        s.footer_text = s.footer_text or (
            "aygarden.az — Azərbaycanın münbit bağlarından və dünyanın ən yaxşı fermalarından "
            "təzə meyvələrin tədarükü və ixracı."
        )
        s.meta_description = s.meta_description or "aygarden.az — təzə meyvələrin onlayn kataloqu."
        if not s.logo:
            self._attach_file(s, "logo", "logo.png")
        if not s.favicon:
            self._attach_file(s, "favicon", "logo-icon.png")
        s.save()
        self.stdout.write("• Parametrlər")

    def seed_slides(self):
        if HeroSlide.objects.exists():
            return
        data = [
            ("Təzə · Təbii · Keyfiyyətli", "Təbiətin ən təzə nemətləri süfrənizdə",
             "Azərbaycanın münbit bağlarından və dünyanın ən yaxşı fermalarından seçilmiş meyvələr.", "basket"),
            ("Geniş çeşid", "Hər mövsümün dadı bir ünvanda",
             "Alma, nar, sitrus, tropik və giləmeyvələr — 120-dən çox məhsul çeşidi.", "tropical"),
            ("Etibarlı tərəfdaş", "Topdan satış və ixrac üçün peşəkar həllər",
             "Soyuq zəncirli logistika, sertifikatlı keyfiyyət və vaxtında çatdırılma.", "market"),
        ]
        for i, (badge, title, sub, img) in enumerate(data):
            slide = HeroSlide(badge=badge, title=title, subtitle=sub, order=i)
            self._attach(slide, "image", img, f"slide-{i}")
            slide.save()
        self.stdout.write("• Bannerlər")

    def seed_statistics(self):
        if Statistic.objects.exists():
            return
        for i, (title, value, suffix, icon) in enumerate([
            ("Komanda üzvü", 85, "+", "users"),
            ("Məhsul çeşidi", 120, "+", "apple"),
            ("İllik tədarük (ton)", 3500, "+", "truck"),
            ("Tərəfdaş ölkə", 14, "", "globe"),
        ]):
            Statistic.objects.create(title=title, value=value, suffix=suffix, icon=icon, order=i)
        self.stdout.write("• Statistika")

    def seed_about(self):
        about = AboutPage.load()
        if not about.content:
            about.subtitle = "Haqqımızda"
            about.title = "Təbiətdən süfrənizə — keyfiyyətli meyvə tədarükü"
            about.content = (
                "aygarden.az 2014-cü ildən bəri Azərbaycanın müxtəlif bölgələrindən — Quba, Qusar, Göyçay, "
                "Lənkəran və Şəkidən təzə meyvələrin tədarükü ilə məşğuldur. Məqsədimiz təbiətin ən gözəl "
                "nemətlərini ən yüksək keyfiyyətlə müştərilərimizə çatdırmaqdır.\n\n"
                "Müasir soyuducu anbarlarımız, peşəkar komandamız və beynəlxalq standartlara uyğun "
                "qablaşdırma xəttimiz sayəsində həm yerli bazara, həm də xarici ölkələrə məhsul ixrac edirik."
            )
            about.experience_years = 12
            about.vision = (
                "Regionda təzə meyvə tədarükü sahəsində ən etibarlı və innovativ brend olmaq, "
                "Azərbaycan meyvələrini dünya bazarlarında layiqincə təmsil etmək."
            )
            about.mission = (
                "Fermerlərlə ədalətli əməkdaşlıq quraraq, təbii və sağlam meyvələri ən təzə halda, "
                "davamlı və ekoloji təmiz üsullarla hər süfrəyə çatdırmaq."
            )
            self._attach(about, "image", "plate", "about-1")
            self._attach(about, "image_secondary", "apples", "about-2")
            about.save()

        if not CompanyValue.objects.exists():
            for i, (t, d, ic) in enumerate([
                ("Təbiilik", "Məhsullarımız kimyəvi qatqılardan uzaq, təbii üsullarla yetişdirilir.", "leaf"),
                ("Keyfiyyət", "Hər partiya laboratoriya nəzarətindən keçir və standartlara uyğun seçilir.", "award"),
                ("Etibarlılıq", "Verdiyimiz sözə sadiq qalır, öhdəliklərimizi vaxtında yerinə yetiririk.", "shield"),
                ("Davamlılıq", "Ekoloji tarazlığı qoruyan kənd təsərrüfatı təcrübələrini dəstəkləyirik.", "seedling"),
            ]):
                CompanyValue.objects.create(title=t, description=d, icon=ic, order=i)

        if not Advantage.objects.exists():
            for i, (t, d, ic) in enumerate([
                ("Birbaşa bağdan", "Vasitəçisiz, birbaşa fermerlərdən təzə məhsul tədarükü.", "apple"),
                ("Soyuq zəncir", "Müasir soyuducu anbarlar və refrijeratorlu nəqliyyat.", "warehouse"),
                ("Sürətli çatdırılma", "Ölkə daxilində 24 saat ərzində çatdırılma imkanı.", "truck"),
                ("Beynəlxalq standartlar", "GLOBALG.A.P. və HACCP tələblərinə uyğun proseslər.", "globe"),
                ("Fərdi qablaşdırma", "Müştərinin tələbinə uyğun brendləşdirilmiş qablaşdırma.", "box"),
                ("Peşəkar komanda", "Aqronom və logistika mütəxəssislərindən ibarət komanda.", "users"),
            ]):
                Advantage.objects.create(title=t, description=d, icon=ic, order=i)

        if not Partner.objects.exists():
            for i, (n, c, d) in enumerate([
                ("FreshLink GmbH", "Almaniya", "Avropa bazarına ixracda strateji tərəfdaş"),
                ("Agro Trade LLC", "Rusiya", "Topdan satış və paylama şəbəkəsi"),
                ("Gulf Fruits Co.", "BƏƏ", "Körfəz ölkələrinə tədarük"),
                ("Anadolu Tarım", "Türkiyə", "Logistika və qablaşdırma həlləri"),
                ("Silk Road Foods", "Qazaxıstan", "Orta Asiya bazarında distribütor"),
                ("Baltic Fresh", "Latviya", "Baltikyanı ölkələrə ixrac"),
            ]):
                Partner.objects.create(name=n, country=c, description=d, order=i)
        self.stdout.write("• Haqqımızda")

    def seed_catalog(self):
        if Category.objects.exists():
            return
        catalog = {
            ("Alma və armud", "apples", "Quba və Qusarın məşhur alma bağlarından seçmə sortlar."): [
                ("Qırmızı Quba alması", "apple_close", "Quba, Azərbaycan", "Sentyabr – Mart", "18 kq karton qutu", True),
                ("Golden alma", "apple", "Qusar, Azərbaycan", "Sentyabr – Fevral", "18 kq karton qutu", False),
                ("Santa Maria armudu", "pear", "Quba, Azərbaycan", "Avqust – Noyabr", "12 kq karton qutu", True),
            ],
            ("Sitrus meyvələri", "citrus", "Lənkəran-Astara bölgəsinin günəşli sitrus bağlarından."): [
                ("Lənkəran naringisi", "tangerine", "Lənkəran, Azərbaycan", "Noyabr – Fevral", "10 kq taxta yeşik", True),
                ("Sitrus qarışığı", "citrus", "Astara, Azərbaycan", "Noyabr – Mart", "15 kq karton qutu", False),
            ],
            ("Tropik meyvələr", "tropical", "Dünyanın tropik bölgələrindən idxal olunan ekzotik meyvələr."): [
                ("Ananas", "pineapple", "Kosta-Rika", "İl boyu", "6 ədəd / qutu", True),
                ("Manqo", "mango", "Peru", "Oktyabr – Mart", "4 kq karton qutu", False),
                ("Banan", "banana", "Ekvador", "İl boyu", "18 kq karton qutu", True),
                ("Kent manqosu", "mangoes", "Braziliya", "Noyabr – Fevral", "4 kq karton qutu", False),
            ],
            ("Giləmeyvələr", "berries", "Ətirli və vitaminlə zəngin təzə giləmeyvələr."): [
                ("Çiyələk", "strawberry", "Xaçmaz, Azərbaycan", "May – İyul", "2 kq plastik qab", True),
                ("Giləmeyvə qarışığı", "berries", "Şəki, Azərbaycan", "İyun – Avqust", "1 kq plastik qab", False),
            ],
            ("Üzüm", "grapes", "Gəncə və Şamaxı üzüm bağlarından süfrə sortları."): [
                ("Qara üzüm", "grapes", "Şamaxı, Azərbaycan", "Avqust – Oktyabr", "8 kq karton qutu", True),
            ],
            ("Bostan məhsulları", "watermelon", "Sabirabad və Saatlının şirəli qarpız və yemişləri."): [
                ("Sabirabad qarpızı", "watermelon", "Sabirabad, Azərbaycan", "İyul – Sentyabr", "Toplu (ədəd)", True),
            ],
        }
        for ci, ((cname, cimg, cdesc), products) in enumerate(catalog.items()):
            cat = Category(name=cname, description=cdesc, order=ci)
            self._attach(cat, "image", cimg, f"cat-{ci}")
            cat.save()
            for pi, (pname, pimg, origin, season, pack, featured) in enumerate(products):
                p = Product(
                    category=cat, name=pname, origin=origin, season=season, packaging=pack,
                    is_featured=featured, order=pi,
                    short_description=f"{origin} bölgəsindən seçilmiş, təzə və keyfiyyətli {pname.lower()}.",
                    description=(
                        f"{pname} — {origin} bağlarından toplanan, ətirli və şirəli meyvədir. "
                        "Məhsul yığımdan dərhal sonra çeşidlənir, soyuducu anbarlarda saxlanılır və "
                        "beynəlxalq standartlara uyğun qablaşdırılır.\n\n"
                        "Topdan satış və ixrac üçün sifarişlər qəbul olunur. Ətraflı məlumat üçün "
                        "bizimlə əlaqə saxlayın."
                    ),
                )
                self._attach(p, "image", pimg, f"product-{ci}-{pi}")
                p.save()
        self.stdout.write("• Kateqoriyalar və məhsullar")

    def seed_news(self):
        if News.objects.exists():
            return
        now = timezone.now()
        for i, (title, img) in enumerate([
            ("Quba alma bağlarında yeni mövsümün ilk məhsulu yığıldı", "apples"),
            ("aygarden.az Berlin Fruit Logistica sərgisində iştirak etdi", "market"),
            ("Yeni soyuducu anbar kompleksimiz istifadəyə verildi", "shelves"),
            ("Lənkəran naringisinin ixrac coğrafiyası genişlənir", "tangerine"),
            ("Sağlam qidalanmada mövsümi meyvələrin rolu", "bowl"),
            ("Tropik meyvələr çeşidimiz yenilənib", "pineapple2"),
        ]):
            n = News(
                title=title,
                excerpt="Şirkətimizin fəaliyyəti və meyvə bazarındakı son yeniliklər haqqında qısa məlumat.",
                content=(
                    f"{title}.\n\n"
                    "aygarden.az komandası olaraq müştərilərimizə ən təzə və keyfiyyətli məhsulları "
                    "çatdırmaq üçün fəaliyyətimizi davamlı genişləndiririk. Bu yenilik çərçivəsində "
                    "tərəfdaşlarımızla əməkdaşlığı gücləndirir, logistika imkanlarımızı artırırıq.\n\n"
                    "Ətraflı məlumat üçün bizimlə əlaqə saxlaya bilərsiniz."
                ),
                published_at=now - timedelta(days=i * 9),
            )
            self._attach(n, "image", img, f"news-{i}")
            n.save()
        self.stdout.write("• Xəbərlər")
