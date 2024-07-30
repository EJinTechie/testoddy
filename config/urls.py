from django.contrib import admin
from django.urls import path, include

from Cardgame import views as cardgame_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Cardgame.urls')),
    path('', cardgame_views.main_view, name='main'),
    path('accounts/', include('allauth.urls')),
   
]

# from django.contrib.auth import views as auth_views
# from django.urls import reverse_lazy

# from . import views

# urlpatterns = [
#     path('cardgame/', include('Cardgame.urls')),
#     path('accounts/login/', auth_views.LoginView.as_view(success_url=reverse_lazy('start_game')), name='login'),
#     path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
#     path('accounts/', include('django.contrib.auth.urls')),
#     path('', views.main_page, name='main_page'),
# ]
