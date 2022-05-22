from django.urls import path
from . import views

app_name = 'exchange'

urlpatterns = [
    path('', views.exchange, name='exchange'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('card_holder/', views.card_holder, name='card_holder'),
    path('card/', views.card, name='card'),
    path('paper/<str:code>', views.paper, name='paper'),
    path('show_exchange/', views.show_exchange, name='show_exchange'),
]
