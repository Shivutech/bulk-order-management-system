from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.create_order, name='create_order'),
    path('<int:id>/', views.order_detail, name='order_detail'),
    path('<int:id>/status/', views.update_order_status, name='update_order_status'),
]