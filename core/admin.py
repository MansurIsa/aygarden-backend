from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AboutPage,
    Advantage,
    Category,
    CompanyValue,
    ContactMessage,
    HeroSlide,
    News,
    Partner,
    Product,
    ProductImage,
    SiteSettings,
    Statistic,
)


def thumb(field_name, size=56):
    def _thumb(obj):
        img = getattr(obj, field_name)
        if img:
            return format_html(
                '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:8px" />',
                img.url, size, size,
            )
        return "—"

    _thumb.short_description = "Şəkil"
    return _thumb


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Ümumi", {"fields": ("site_name", "slogan", "logo", "logo_footer", "favicon")}),
        ("Əlaqə", {"fields": (
            "phone", "phone_secondary", "whatsapp", "email", "address", "working_hours", "map_embed_url",
        )}),
        ("Sosial şəbəkələr", {"fields": ("facebook", "instagram", "linkedin", "youtube", "tiktok", "telegram")}),
        ("Footer və SEO", {"fields": ("footer_text", "meta_description", "meta_keywords")}),
    )


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("preview", "title", "order", "is_active")
    list_display_links = ("preview", "title")
    list_editable = ("order", "is_active")
    preview = thumb("image")


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("title", "value", "suffix", "icon", "order", "is_active")
    list_editable = ("value", "suffix", "order", "is_active")


@admin.register(AboutPage)
class AboutPageAdmin(SingletonAdmin):
    fieldsets = (
        ("Giriş", {"fields": ("subtitle", "title", "content", "image", "image_secondary", "experience_years")}),
        ("Vizyon və missiya", {"fields": ("vision", "mission")}),
    )


@admin.register(CompanyValue)
class CompanyValueAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "country", "order", "is_active")
    list_display_links = ("preview", "name")
    list_editable = ("order", "is_active")
    preview = thumb("logo")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "slug", "order", "is_active")
    list_display_links = ("preview", "name")
    list_editable = ("order", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    preview = thumb("image")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "category", "origin", "is_featured", "is_active", "order")
    list_display_links = ("preview", "name")
    list_editable = ("is_featured", "is_active", "order")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    inlines = [ProductImageInline]
    preview = thumb("image")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("preview", "title", "published_at", "is_active")
    list_display_links = ("preview", "title")
    list_editable = ("is_active",)
    search_fields = ("title", "content")
    date_hierarchy = "published_at"
    prepopulated_fields = {"slug": ("title",)}
    preview = thumb("image")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "subject", "source", "is_read", "created_at")
    list_filter = ("is_read", "source", "created_at")
    list_editable = ("is_read",)
    search_fields = ("full_name", "phone", "email", "message")
    readonly_fields = ("full_name", "phone", "email", "subject", "message", "source", "created_at")
