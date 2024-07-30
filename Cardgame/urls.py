from django.urls import path
from . import views


app_name = 'Cardgame'

urlpatterns = [
    path('', views.main_view, name='main'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('cardgame', views.game_list, name='game_list'),  
    path('cardgame/create/', views.create_game, name='create_game'),
    path('cardgame/select_card/<int:game_id>/', views.select_card, name='select_card'),
    path('cardgame/game_result/<int:game_id>/', views.game_result, name='game_result'),
    path('cardgame/game_detail/<int:game_id>/', views.game_detail, name='game_detail'),
    path('cardgame/cancel_game/<int:game_id>/', views.cancel_game, name='cancel_game'),

    path('start/', views.start_game, name='start_game'),
    # path('list/', views.game_list, name='game_list'),
    path('cardgame/counter-attack/<int:game_id>/', views.counter_attack, name='counter_attack'),
    #path('game-result/<int:game_id>/', views.game_result, name='game_result'),

    path('ranking/', views.ranking_view, name='ranking'),
    # path('cardgame/filter_game_list/<int:user_id>/', views.filter_game_list, name='filter_game_list'),
    path('cardgame/filter_game_list/<int:game_id>/', views.filter_game_list, name='filter_game_list'),
]


