from django.urls import path, re_path
from django.views.generic import RedirectView

from . import api
from . import views

app_name = 'mapapp'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('pkmnadmin/', views.admin_page, name='admin'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('logout/', views.logout_page, name='logout'),
    path('pokedex/', views.pokedex_page, name='pokedex'),

    path('api/check_pkmn/', api.check_pkmn, name='check_pkmn'),
    path('api/get_user_pkmn/', api.get_user_pkmn, 
    name='get_user_pkmn'),
    path('api/capture_pkmn/', api.capture_pkmn, name='capture_pkmn'),
    path('api/add_pkmn/', api.add_pkmn, name='add_pkmn'),
    path('api/remove_pkmn/', api.remove_pkmn, name='remove_pkmn'),
    path('api/get_all_pkmn/', api.get_all_pkmn, name='get_all_pkmn'),
    path('api/shuffle_pkmn/', api.shuffle_pkmn, name='shuffle_pkmn'),
]
