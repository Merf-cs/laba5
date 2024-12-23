from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.sales_form, name='sales_form'),
    path('upload/', views.upload_file, name='upload_file'),
    path('list/', views.sales_list, name='sales_list'),
    path('sales/edit/<int:sale_id>/', views.edit_sale, name='edit_sale'),
    path('sales/delete/<int:sale_id>/', views.delete_sale, name='delete_sale'),
    path('sales/list/', views.sales_list, name='sales_list'),
    path('sales/search_sales/', views.search_sales, name='search_sales'),  # Добавьте этот путь для поиска
]
