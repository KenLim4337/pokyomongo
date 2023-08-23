from django.db import models
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Sum
import pokepy

class user_pkmn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pkmn_id = models.IntegerField()
    state = models.IntegerField(default=0)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + ' - ' + str(self.pkmn_id)
    
    def get_pkmn(self):
        client = pokepy.V2Client()
        return client.get_pokemon(self.pkmn_id)
    
class pkmn_locations(models.Model):
    pkmn_id = models.IntegerField()
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return str(self.pkmn_id) + ' - ' + str(self.lat) + ' - ' + str(self.lon)
    
    def get_pkmn(self):
        client = pokepy.V2Client()
        return client.get_pokemon(self.pkmn_id)
    

