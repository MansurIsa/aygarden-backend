from django.db.models import Count, Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import (
    AboutPage,
    Category,
    HeroSlide,
    News,
    Partner,
    Product,
    SiteSettings,
    Statistic,
)
from .serializers import (
    AboutPageSerializer,
    CategorySerializer,
    ContactMessageSerializer,
    HeroSlideSerializer,
    NewsDetailSerializer,
    NewsListSerializer,
    PartnerSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    SiteSettingsSerializer,
    StatisticSerializer,
)


class SiteSettingsView(APIView):
    """GET /api/settings/ — loqo, favicon, əlaqə məlumatları, sosial şəbəkələr."""

    def get(self, request):
        serializer = SiteSettingsSerializer(SiteSettings.load(), context={"request": request})
        return Response(serializer.data)


class HeroSlideListView(generics.ListAPIView):
    serializer_class = HeroSlideSerializer
    pagination_class = None
    queryset = HeroSlide.objects.filter(is_active=True)


class StatisticListView(generics.ListAPIView):
    serializer_class = StatisticSerializer
    pagination_class = None
    queryset = Statistic.objects.filter(is_active=True)


class PartnerListView(generics.ListAPIView):
    serializer_class = PartnerSerializer
    pagination_class = None
    queryset = Partner.objects.filter(is_active=True)


class AboutPageView(APIView):
    """GET /api/about/ — vizyon, missiya, dəyərlər, üstünlüklər, tərəfdaşlar."""

    def get(self, request):
        serializer = AboutPageSerializer(AboutPage.load(), context={"request": request})
        return Response(serializer.data)


def _active_categories():
    return Category.objects.filter(is_active=True).annotate(
        product_count=Count("products", filter=Q(products__is_active=True))
    )


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        return _active_categories()


class CategoryDetailView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        return _active_categories()


class ProductListView(generics.ListAPIView):
    """
    GET /api/products/
      ?category=<slug>   kateqoriyaya görə filtr
      ?search=<söz>      ad / təsvir üzrə axtarış
      ?featured=true     yalnız seçilmiş məhsullar
      ?page=, ?page_size=
    """

    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True, category__is_active=True).select_related("category")
        params = self.request.query_params
        if category := params.get("category"):
            qs = qs.filter(category__slug=category)
        if search := params.get("search", "").strip():
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(short_description__icontains=search)
                | Q(description__icontains=search)
                | Q(category__name__icontains=search)
            )
        if params.get("featured") in ("1", "true", "True"):
            qs = qs.filter(is_featured=True)
        return qs


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("gallery")
        )


class NewsListView(generics.ListAPIView):
    serializer_class = NewsListSerializer

    def get_queryset(self):
        qs = News.objects.filter(is_active=True)
        if search := self.request.query_params.get("search", "").strip():
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
        return qs


class NewsDetailView(generics.RetrieveAPIView):
    serializer_class = NewsDetailSerializer
    lookup_field = "slug"
    queryset = News.objects.filter(is_active=True)


class ContactCreateView(generics.CreateAPIView):
    """POST /api/contact/ — əlaqə forması və bannerdəki "Müraciət et"."""

    serializer_class = ContactMessageSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Müraciətiniz qəbul olundu. Tezliklə sizinlə əlaqə saxlayacağıq."},
            status=status.HTTP_201_CREATED,
        )


class SearchView(APIView):
    """GET /api/search/?q=<söz> — məhsul, kateqoriya və xəbərlər üzrə ümumi axtarış."""

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if len(q) < 2:
            return Response({"query": q, "products": [], "categories": [], "news": []})

        ctx = {"request": request}
        products = (
            Product.objects.filter(is_active=True, category__is_active=True)
            .filter(Q(name__icontains=q) | Q(short_description__icontains=q) | Q(category__name__icontains=q))
            .select_related("category")[:12]
        )
        categories = _active_categories().filter(Q(name__icontains=q) | Q(description__icontains=q))[:6]
        news = News.objects.filter(is_active=True).filter(
            Q(title__icontains=q) | Q(excerpt__icontains=q)
        )[:6]
        return Response({
            "query": q,
            "products": ProductListSerializer(products, many=True, context=ctx).data,
            "categories": CategorySerializer(categories, many=True, context=ctx).data,
            "news": NewsListSerializer(news, many=True, context=ctx).data,
        })
