from django.urls import path

from .views import import_products_view

app_name = "imports"

urlpatterns = [
    path('import-products/', import_products_view, name='import-products'),
]
