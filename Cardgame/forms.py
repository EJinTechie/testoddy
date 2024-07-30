from django import forms
from .models import CardSelection
from django.contrib.auth.models import User
from .models import Game, get_random_cards

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class CardSelectionForm(forms.ModelForm):
    class Meta:
        model = CardSelection
        fields = ['selected_card', 'game']


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='필수 항목입니다.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': '사용자명',
            'email': '이메일',
            'password1': '비밀번호',
            'password2': '비밀번호 확인',
        }
        help_texts = {
            'username': '필수 항목입니다. 150자 이하, 문자, 숫자, @/./+/-/_ 만 가능합니다.',
            'password1': '비밀번호는 8자 이상이어야 하며, 너무 흔한 비밀번호는 사용할 수 없습니다.',
            'password2': '위와 동일한 비밀번호를 입력하세요.',
        }


class StartGameForm(forms.ModelForm):
    defender = forms.ModelChoiceField(queryset=User.objects.exclude(username='admin'), label='Select Opponent')
    card = forms.ChoiceField(choices=[], label='Select Card')

    class Meta:
        model = Game
        fields = ['defender', 'card']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(StartGameForm, self).__init__(*args, **kwargs)
        
        if self.request:
            if 'random_cards' not in self.request.session:
                self.request.session['random_cards'] = get_random_cards()
            
            self.fields['card'].choices = [(str(i), str(i)) for i in self.request.session['random_cards']]

    def clean_card(self):
        selected_card = self.cleaned_data['card']
        if self.request and 'random_cards' in self.request.session:
            if int(selected_card) not in self.request.session['random_cards']:
                raise forms.ValidationError("Selected card is not one of the available choices.")
        return int(selected_card)
