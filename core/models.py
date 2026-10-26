from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .utils import az_slugify, unique_slug

ICON_CHOICES = [
    ("leaf", "Yarpaq"),
    ("apple", "Alma"),
    ("users", "Komanda"),
    ("box", "Məhsul / qutu"),
    ("truck", "Logistika"),
    ("globe", "Dünya / ixrac"),
    ("award", "Mükafat / keyfiyyət"),
    ("shield", "Etibarlılıq"),
    ("heart", "Sağlamlıq"),
    ("handshake", "Tərəfdaşlıq"),
    ("sun", "Günəş / təbiət"),
    ("star", "Ulduz"),
    ("clock", "Zaman"),
    ("warehouse", "Anbar"),
    ("seedling", "Cücərti"),
    ("smile", "Məmnun müştəri"),
]


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Yaradılma tarixi", auto_now_add=True)
    updated_at = models.DateTimeField("Yenilənmə tarixi", auto_now=True)

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """Yalnız bir qeydi olan model (məs. sayt parametrləri)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and type(self).objects.exists():
            raise ValidationError("Bu bölmə üçün yalnız bir qeyd yaradıla bilər.")
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj


# --------------------------------------------------------------------------
# Parametrlər
# --------------------------------------------------------------------------
class SiteSettings(SingletonModel):
    site_name = models.CharField("Saytın adı", max_length=120, default="aygarden.az")
    slogan = models.CharField("Şüar", max_length=255, blank=True, default="Təbiətin ən təzə nemətləri")
    logo = models.ImageField("Loqo", upload_to="settings/", blank=True, null=True)
    logo_footer = models.ImageField(
        "Footer loqosu (ağ fon üçün olmayan)", upload_to="settings/", blank=True, null=True
    )
    favicon = models.ImageField("Favicon", upload_to="settings/", blank=True, null=True)

    phone = models.CharField("Əlaqə nömrəsi", max_length=40, blank=True)
    phone_secondary = models.CharField("Əlavə nömrə", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp nömrəsi", max_length=40, blank=True, help_text="Məs: 994501234567")
    email = models.EmailField("E-poçt", blank=True)
    address = models.CharField("Ünvan", max_length=255, blank=True)
    working_hours = models.CharField("İş saatları", max_length=120, blank=True)
    map_embed_url = models.URLField(
        "Google Maps embed linki", max_length=1000, blank=True,
        help_text="Google Maps → Paylaş → Xəritəni yerləşdir → src içindəki link",
    )

    facebook = models.URLField("Facebook", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    youtube = models.URLField("YouTube", blank=True)
    tiktok = models.URLField("TikTok", blank=True)
    telegram = models.URLField("Telegram", blank=True)

    footer_text = models.TextField("Footer mətni", blank=True)
    meta_description = models.CharField("SEO təsviri", max_length=300, blank=True)
    meta_keywords = models.CharField("SEO açar sözlər", max_length=300, blank=True)

    class Meta:
        verbose_name = "Parametrlər"
        verbose_name_plural = "Parametrlər"

    def __str__(self):
        return "Sayt parametrləri"


# --------------------------------------------------------------------------
# Ana səhifə
# --------------------------------------------------------------------------
class HeroSlide(TimeStampedModel):
    badge = models.CharField("Kiçik başlıq", max_length=80, blank=True)
    title = models.CharField("Başlıq", max_length=200)
    subtitle = models.TextField("Alt mətn", blank=True)
    image = models.ImageField("Şəkil", upload_to="slides/", blank=True, null=True)
    button_text = models.CharField("Düymə mətni", max_length=50, default="Müraciət et")
    secondary_button_text = models.CharField("İkinci düymə mətni", max_length=50, blank=True, default="Məhsullar")
    secondary_button_link = models.CharField("İkinci düymə linki", max_length=200, blank=True, default="/mehsullar")
    order = models.PositiveIntegerField("Sıra", default=0)
    is_active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlər"

    def __str__(self):
        return self.title


class Statistic(models.Model):
    title = models.CharField("Başlıq", max_length=80, help_text="Məs: Komanda üzvü")
    value = models.PositiveIntegerField("Rəqəm")
    suffix = models.CharField("Şəkilçi", max_length=10, blank=True, help_text="Məs: +, %, t")
    icon = models.CharField("İkon", max_length=30, choices=ICON_CHOICES, default="leaf")
    order = models.PositiveIntegerField("Sıra", default=0)
    is_active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Statistika"
        verbose_name_plural = "Statistika"

    def __str__(self):
        return f"{self.title}: {self.value}{self.suffix}"


# --------------------------------------------------------------------------
# Haqqımızda
# --------------------------------------------------------------------------
class AboutPage(SingletonModel):
    title = models.CharField("Başlıq", max_length=200, default="Təbiətdən süfrənizə")
    subtitle = models.CharField("Kiçik başlıq", max_length=200, blank=True, default="Haqqımızda")
    content = models.TextField("Əsas mətn", blank=True)
    image = models.ImageField("Şəkil", upload_to="about/", blank=True, null=True)
    image_secondary = models.ImageField("İkinci şəkil", upload_to="about/", blank=True, null=True)
    experience_years = models.PositiveIntegerField("Təcrübə (il)", default=10)

    vision = models.TextField("Vizyonumuz", blank=True)
    mission = models.TextField("Missiyamız", blank=True)

    class Meta:
        verbose_name = "Haqqımızda səhifəsi"
        verbose_name_plural = "Haqqımızda səhifəsi"

    def __str__(self):
        return "Haqqımızda"


class CompanyValue(models.Model):
    title = models.CharField("Başlıq", max_length=120)
    description = models.TextField("Təsvir", blank=True)
    icon = models.CharField("İkon", max_length=30, choices=ICON_CHOICES, default="heart")
    order = models.PositiveIntegerField("Sıra", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Dəyərimiz"
        verbose_name_plural = "Dəyərlərimiz"

    def __str__(self):
        return self.title


class Advantage(models.Model):
    title = models.CharField("Başlıq", max_length=120)
    description = models.TextField("Təsvir", blank=True)
    icon = models.CharField("İkon", max_length=30, choices=ICON_CHOICES, default="award")
    order = models.PositiveIntegerField("Sıra", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Üstünlüyümüz"
        verbose_name_plural = "Üstünlüklərimiz"

    def __str__(self):
        return self.title


class Partner(models.Model):
    name = models.CharField("Ad", max_length=150)
    country = models.CharField("Ölkə", max_length=80, blank=True)
    logo = models.ImageField("Loqo", upload_to="partners/", blank=True, null=True)
    website = models.URLField("Vebsayt", blank=True)
    description = models.CharField("Qısa təsvir", max_length=255, blank=True)
    order = models.PositiveIntegerField("Sıra", default=0)
    is_active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Beynəlxalq tərəfdaş"
        verbose_name_plural = "Beynəlxalq tərəfdaşlıqlar"

    def __str__(self):
        return self.name


# --------------------------------------------------------------------------
# Məhsullar
# --------------------------------------------------------------------------
class Category(TimeStampedModel):
    name = models.CharField("Ad", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True, blank=True, allow_unicode=False)
    description = models.TextField("Təsvir", blank=True)
    image = models.ImageField("Şəkil", upload_to="categories/", blank=True, null=True)
    order = models.PositiveIntegerField("Sıra", default=0)
    is_active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Kateqoriya"
        verbose_name_plural = "Kateqoriyalar"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, az_slugify(self.name), self.pk)
        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    category = models.ForeignKey(
        Category, verbose_name="Kateqoriya", on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField("Ad", max_length=160)
    slug = models.SlugField("Slug", max_length=180, unique=True, blank=True)
    short_description = models.CharField("Qısa təsvir", max_length=255, blank=True)
    description = models.TextField("Ətraflı təsvir", blank=True)
    image = models.ImageField("Əsas şəkil", upload_to="products/", blank=True, null=True)
    origin = models.CharField("Mənşə", max_length=100, blank=True, help_text="Məs: Quba, Azərbaycan")
    season = models.CharField("Mövsüm", max_length=100, blank=True, help_text="Məs: Sentyabr – Noyabr")
    packaging = models.CharField("Qablaşdırma", max_length=150, blank=True, help_text="Məs: 10 kq karton qutu")
    is_featured = models.BooleanField("Ana səhifədə göstər", default=False)
    order = models.PositiveIntegerField("Sıra", default=0)
    is_active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Məhsul"
        verbose_name_plural = "Məhsullar"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Product, az_slugify(self.name), self.pk)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField("Şəkil", upload_to="products/gallery/")
    order = models.PositiveIntegerField("Sıra", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Qalereya şəkli"
        verbose_name_plural = "Qalereya"

    def __str__(self):
        return f"{self.product.name} — şəkil {self.pk}"


# --------------------------------------------------------------------------
# Xəbərlər
# --------------------------------------------------------------------------
class News(TimeStampedModel):
    title = models.CharField("Başlıq", max_length=220)
    slug = models.SlugField("Slug", max_length=240, unique=True, blank=True)
    excerpt = models.CharField("Qısa mətn", max_length=300, blank=True)
    content = models.TextField("Mətn")
    image = models.ImageField("Şəkil", upload_to="news/", blank=True, null=True)
    published_at = models.DateTimeField("Dərc tarixi", default=timezone.now)
    is_active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Xəbər"
        verbose_name_plural = "Xəbərlər"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(News, az_slugify(self.title), self.pk)
        super().save(*args, **kwargs)


# --------------------------------------------------------------------------
# Müraciətlər
# --------------------------------------------------------------------------
class ContactMessage(models.Model):
    full_name = models.CharField("Ad, soyad", max_length=150)
    phone = models.CharField("Telefon", max_length=40, blank=True)
    email = models.EmailField("E-poçt", blank=True)
    subject = models.CharField("Mövzu", max_length=200, blank=True)
    message = models.TextField("Mesaj")
    source = models.CharField("Mənbə", max_length=40, default="contact", help_text="contact / banner")
    is_read = models.BooleanField("Oxunub", default=False)
    created_at = models.DateTimeField("Göndərilmə tarixi", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Müraciət"
        verbose_name_plural = "Müraciətlər"

    def __str__(self):
        return f"{self.full_name} — {self.created_at:%d.%m.%Y %H:%M}"
