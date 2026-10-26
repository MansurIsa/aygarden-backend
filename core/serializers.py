from rest_framework import serializers

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


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        exclude = ["id"]


class HeroSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlide
        fields = [
            "id", "badge", "title", "subtitle", "image", "button_text",
            "secondary_button_text", "secondary_button_link",
        ]


class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = ["id", "title", "value", "suffix", "icon"]


class CompanyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyValue
        fields = ["id", "title", "description", "icon"]


class AdvantageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advantage
        fields = ["id", "title", "description", "icon"]


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ["id", "name", "country", "logo", "website", "description"]


class AboutPageSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()
    advantages = serializers.SerializerMethodField()
    partners = serializers.SerializerMethodField()

    class Meta:
        model = AboutPage
        fields = [
            "title", "subtitle", "content", "image", "image_secondary", "experience_years",
            "vision", "mission", "values", "advantages", "partners",
        ]

    def get_values(self, obj):
        return CompanyValueSerializer(CompanyValue.objects.all(), many=True, context=self.context).data

    def get_advantages(self, obj):
        return AdvantageSerializer(Advantage.objects.all(), many=True, context=self.context).data

    def get_partners(self, obj):
        qs = Partner.objects.filter(is_active=True)
        return PartnerSerializer(qs, many=True, context=self.context).data


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image", "product_count"]


class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryMiniSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "short_description", "image", "origin",
            "season", "packaging", "is_featured", "category",
        ]


class ProductDetailSerializer(ProductListSerializer):
    gallery = ProductImageSerializer(many=True, read_only=True)
    related = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ["description", "gallery", "related"]

    def get_related(self, obj):
        qs = (
            Product.objects.filter(is_active=True, category=obj.category)
            .exclude(pk=obj.pk)
            .select_related("category")[:4]
        )
        return ProductListSerializer(qs, many=True, context=self.context).data


class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "slug", "excerpt", "image", "published_at"]


class NewsDetailSerializer(NewsListSerializer):
    latest = serializers.SerializerMethodField()

    class Meta(NewsListSerializer.Meta):
        fields = NewsListSerializer.Meta.fields + ["content", "latest"]

    def get_latest(self, obj):
        qs = News.objects.filter(is_active=True).exclude(pk=obj.pk)[:3]
        return NewsListSerializer(qs, many=True, context=self.context).data


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["full_name", "phone", "email", "subject", "message", "source"]

    def validate(self, attrs):
        if not attrs.get("phone") and not attrs.get("email"):
            raise serializers.ValidationError(
                {"phone": "Telefon nömrəsi və ya e-poçt ünvanından ən azı biri daxil edilməlidir."}
            )
        return attrs

    def validate_source(self, value):
        return value if value in ("contact", "banner", "product") else "contact"
