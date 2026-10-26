from django.urls import path

from . import views

urlpatterns = [
    path("settings/", views.SiteSettingsView.as_view(), name="settings"),
    path("slides/", views.HeroSlideListView.as_view(), name="slides"),
    path("statistics/", views.StatisticListView.as_view(), name="statistics"),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("partners/", views.PartnerListView.as_view(), name="partners"),
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path("categories/<slug:slug>/", views.CategoryDetailView.as_view(), name="category-detail"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("news/", views.NewsListView.as_view(), name="news"),
    path("news/<slug:slug>/", views.NewsDetailView.as_view(), name="news-detail"),
    path("contact/", views.ContactCreateView.as_view(), name="contact"),
    path("search/", views.SearchView.as_view(), name="search"),
]
