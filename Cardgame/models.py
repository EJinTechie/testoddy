from django.db import models
from django.contrib.auth.models import User
import random

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Game(models.Model):
    attacker = models.ForeignKey(User, related_name='games_attacked', on_delete=models.CASCADE)
    defender = models.ForeignKey(User, related_name='games_defended', on_delete=models.CASCADE)
    attacker_card = models.IntegerField(null=True, blank=True)
    defender_card = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=20, null=True, blank=True)  # "attacker_win", "defender_win", "draw"
    winner = models.ForeignKey(User, related_name='games_won', on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attacker.username} vs {self.defender.username}"

    def calculate_result(self):
        if self.attacker_card is None or self.defender_card is None:
            return

        attacker_profile, _ = Profile.objects.get_or_create(user=self.attacker)
        defender_profile, _ = Profile.objects.get_or_create(user=self.defender)

        if self.attacker_card == self.defender_card:
            self.result = "draw"
            self.winner = None
        else:
            # 랜덤으로 승자 결정
            if random.choice([True, False]):
                winner_profile = attacker_profile
                loser_profile = defender_profile
                winner_card = self.attacker_card
                loser_card = self.defender_card
                self.result = "attacker_win"
                self.winner = self.attacker
            else:
                winner_profile = defender_profile
                loser_profile = attacker_profile
                winner_card = self.defender_card
                loser_card = self.attacker_card
                self.result = "defender_win"
                self.winner = self.defender

            winner_profile.score += winner_card
            loser_profile.score -= loser_card

        attacker_profile.save()
        defender_profile.save()

    def save(self, *args, **kwargs):
        if self.attacker_card is not None and self.defender_card is not None and self.result is None:
            self.calculate_result()
        super(Game, self).save(*args, **kwargs)
               
class Card(models.Model):
    number = models.IntegerField()
    game = models.ForeignKey(Game, related_name='cards', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner.username} - Card {self.number}"

class GameStatus(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])

    def __str__(self):
        return f"Game {self.game.id} - {self.status}"

class CardSelection(models.Model):
    game = models.ForeignKey(Game, related_name='selections', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_card = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} selected {self.selected_card} for Game {self.game.id}"

def get_random_cards():
    return random.sample(range(1, 11), 5)

# get_random_cards 함수는 변경하지 않았습니다.
