
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Game, CardSelection
from .utils import get_random_cards
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
import random
from .models import Game, CardSelection, Profile



from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import LoginForm, SignUpForm



def main_view(request):
    return render(request,'main.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('main')
            else:
                messages.error(request, '로그인에 실패했습니다. 사용자명과 비밀번호를 확인하세요.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('main')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('main')


@login_required
def ranking_view(request):
    profiles = Profile.objects.order_by('-score')[:3]  # 상위 3명의 사용자
    if profiles:
        max_score = profiles[0].score
    else:
        max_score = 1
    for profile in profiles:
        profile.bar_height = (profile.score / max_score) * 100  # 막대의 높이를 최대 100%로 비율 조정

    return render(request, 'ranking.html', {'profiles': profiles})

def get_random_cards():
    return random.sample(range(1, 11), 5)

@login_required
def create_game(request):
    if request.method == 'POST':
        defender = User.objects.get(id=request.POST['defender_id'])
        game = Game.objects.create(attacker=request.user, defender=defender)
        return redirect('Cardgame:select_card', game_id=game.id)
    return render(request, 'create_game.html', {'users': User.objects.exclude(id=request.user.id)})

@login_required
def select_card(request, game_id):
    game = Game.objects.get(id=game_id)
    user = request.user

    if request.method == 'POST':
        selected_card = int(request.POST.get('selected_card'))
        CardSelection.objects.create(game=game, user=user, selected_card=selected_card)

        if user == game.attacker:
            game.attacker_card = selected_card
        elif user == game.defender:
            game.defender_card = selected_card

        if game.attacker_card is not None and game.defender_card is not None:
            game.calculate_result()
            game.save()
            return redirect('Cardgame:game_result', game_id=game.id)
        else:
            game.save()

    cards = get_random_cards()
    return render(request, 'select_card.html', {'game': game, 'cards': cards})





@login_required
def game_list(request):
    games = Game.objects.filter(Q(attacker=request.user) | Q(defender=request.user)).order_by('-timestamp')
    return render(request, 'game_list.html', {'games': games})

def cancel_game(request, game_id):
    game = Game.objects.get(id=game_id)
    if request.user == game.attacker and game.defender_card is None:
        game.delete()
    return redirect('Cardgame:game_list')



@login_required
def game_detail(request, game_id):
    game = Game.objects.get(id=game_id)
    user = request.user

    if request.method == 'POST':
        if 'cancel_game' in request.POST and request.user == game.attacker and game.defender_card is None:
            game.delete()
            return redirect('Cardgame:game_list')
        elif 'counter_attack' in request.POST and request.user == game.defender and game.defender_card is None:
            return redirect('Cardgame:select_card', game_id=game.id)

    return render(request, 'game_detail.html', {'game': game, 'user': user})


# @login_required
# def game_result(request, game_id):
#     game = Game.objects.get(id=game_id)
#     return render(request, 'game_result.html', {'game': game})
@login_required
def game_result(request, game_id):
    game = Game.objects.get(id=game_id)
    context = {
        'game': game,
        'result': game.result,
        'winner': game.winner.username if game.winner else 'Draw',
        'attacker_score': game.attacker.profile.score,
        'defender_score': game.defender.profile.score,
    }
    return render(request, 'game_result.html', context)



#---------------------------------------------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import StartGameForm
from django.http import HttpResponseForbidden
from .models import Game, CardSelection, GameStatus,Profile, get_random_cards
from django.contrib import messages

@login_required
def start_game(request):
    if request.method == 'POST':
        form = StartGameForm(request.POST, request=request)
        if form.is_valid():
            game = form.save(commit=False)
            game.attacker = request.user
            game.attacker_card = form.cleaned_data['card']
            game.save()
            GameStatus.objects.create(game=game, status='pending')
            if 'random_cards' in request.session:
                del request.session['random_cards']
            return redirect('Cardgame:game_list')
    else:
        form = StartGameForm(request=request)
    return render(request, 'start_game.html', {'form': form})

# @login_required
# def game_list(request):
#     games = Game.objects.filter(attacker=request.user) | Game.objects.filter(defender=request.user)
#     games = games.select_related('gamestatus')
#     return render(request, 'Cardgame/game_list.html', {'games': games})

@login_required
def counter_attack(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # 현재 사용자가 defender인지 확인
    if request.user != game.defender:
        messages.error(request, "You are not authorized to counter-attack in this game.")
        return redirect('game_list')
    
    # 게임 상태 확인
    game_status, created = GameStatus.objects.get_or_create(game=game)
    if game_status.status != 'pending':
        messages.error(request, "This game is not in a state where you can counter-attack.")
        return redirect('game_list')
    
    if request.method == 'POST':
        selected_card = int(request.POST.get('selected_card'))
        
        # 카드 선택 저장
        CardSelection.objects.create(game=game, user=request.user, selected_card=selected_card)
        
        # 게임 업데이트
        game.defender_card = selected_card
        game.save()
        
        # Ensure profiles exist for both attacker and defender
        Profile.objects.get_or_create(user=game.attacker)
        Profile.objects.get_or_create(user=game.defender)
        
        # 게임 결과 계산
        game.calculate_result()
        
        # 게임 상태 업데이트
        game_status.status = 'completed'
        game_status.save()
        
        # 게임 결과 페이지로 리다이렉트
        return redirect('game_result', game_id=game.id)
    
    random_cards = get_random_cards()
    
    context = {
        'game': game,
        'random_cards': random_cards,
    }
    
    return render(request, 'Cardgame/counter_attack.html', context)


def filter_game_list(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    attacker = game.attacker
    defender = game.defender
    games = Game.objects.filter(
        Q(attacker=request.user, defender=defender) |
        Q(attacker=attacker, defender=request.user)
    ).order_by('-timestamp')
    
    ctx = {
        'games': games,
        'opponent': defender if request.user == attacker else attacker
    }
    return render(request, 'filter_game_list.html', ctx)