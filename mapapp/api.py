from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.models import User
import pokepy
from .models import user_pkmn, pkmn_locations
import random
import numpy as np

client = pokepy.V2Client()

max_lat = 43.003726
min_lat = 42.717577
max_lon = 74.775853
min_lon = 74.433841

def check_pkmn(request):
    global_pkmns = pkmn_locations.objects.all()

    # Get user location
    user_lat = float(request.GET.get('lat'))
    user_lon = float(request.GET.get('lng'))

    threshold = 2000
    # Get all pokemon within 200 meters of user
    nearby_pkmn = []
    for pkmn in global_pkmns:
        pkmn_lat = pkmn.lat
        pkmn_lon = pkmn.lon

        distance = haversine(user_lon, user_lat, pkmn_lon, pkmn_lat)

        if distance < threshold:
            nearby_pkmn.append(get_pkmn_json(pkmn))

    return JsonResponse(nearby_pkmn, safe=False)

def get_user_pkmn(request):
    if request.user.is_authenticated:
        user = request.user
        user_pkmn = user_pkmn.objects.filter(user=user)
        return JsonResponse(user_pkmn, safe=False)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

def capture_pkmn(request):
    pkmn_id = int(request.GET.get('pkmn_id'))
    user = request.user
    number_captured = user_pkmn.objects.filter(user_id=user.id).count()
    capture_bonus = int(np.floor(number_captured/10))

     # Roll d20
    roll = random.randint(1, 20)

    # Get pokemon from pokepy
    pkmn = client.get_pokemon(pkmn_id)[0]
    
    capture_rate = int(np.floor(pkmn.base_experience/10))

    # Cap capture rate at 20, floor at 2
    if capture_rate > 20:
        capture_rate = 20
    elif capture_rate < 2:
        capture_rate = 2
    
    result = {
        'success': False,
        'roll': roll,
        'roll_bonus': capture_bonus,
        'roll_requirement': capture_rate,
        'pkmn_info': get_pkmn_json(pkmn_locations.objects.filter(pkmn_id=pkmn_id)[0])
    }
    
    required_roll = capture_rate - capture_bonus

    # If roll is 20, crit success
    if roll == 20:
        result['success'] = True
    # If roll is 1, crit fail
    elif roll == 1:
        result['success'] = False
    # Else, compare roll to capture rate
    else:
        # Cap required roll at 2
        if required_roll < 2:
            required_roll = 2

        if roll + capture_bonus >= capture_rate:
            result['success'] = True
        else:
            result['success'] = False

    current_pkmn = user_pkmn.objects.filter(user_id=user.id, pkmn_id=pkmn_id)

    if result['success']:
        if len(current_pkmn) > 0:
            # If pokemon already in user's dex, adjust to captured
            current_pkmn = current_pkmn[0]
            current_pkmn.state = 1
            current_pkmn.count += 1
            current_pkmn.save()
        else:
            # Else add new entry to user's dex
            new_pkmn = user_pkmn(user_id=user.id, pkmn_id=pkmn_id, state=1, count=1)
            new_pkmn.save()
    else:
        if len(current_pkmn) == 0:
            # If not seen add new entry to user's dex
            new_pkmn = user_pkmn(user_id=user.id, pkmn_id=pkmn_id, state=0, count=0)
            new_pkmn.save()

    
    return JsonResponse(result, safe=False)


def add_pkmn(request):
    return

def remove_pkmn(request):
    return

def get_all_pkmn(request):
    global_pkmn = pkmn_locations.objects.all()

    results = []

    # Get all pokemon from pokepy
    for pkmn in global_pkmn:
        results.append(get_pkmn_json(pkmn))

    return JsonResponse(results, safe=False)



def shuffle_pkmn(request):
    number = int(request.POST.get('number'))
    shuffle_type = request.POST.get('shuffleType')

    if shuffle_type == 'full':
        # Generate N pokemon with IDs from 1 through 898
        pkmn_gen = gen_pkmn(number, 1, 898)
        # Purge all pkmn_locations, then re-add them
        pkmn_locations.objects.all().delete()

        # Add all pokemon to the database
        for pkmn in pkmn_gen:
            new_pkmn = pkmn_locations(pkmn_id=pkmn[0], lat=pkmn[1], lon=pkmn[2])
            new_pkmn.save()

    elif shuffle_type == 'partial': 
        # Shuffle the locations of pokemon currently in the map
        
        # Get all pokemon currently in the map
        current_pkmn = pkmn_locations.objects.all()

        if len(current_pkmn) > 0:
            # Get a new location for each existing pokemon
            pkmn_gen = gen_pkmn(len(current_pkmn), 1, 898)

            for pkmn in current_pkmn:
                new_location = random.choice(pkmn_gen)

                # Update the location of the pokemon
                pkmn.lat = new_location[1]
                pkmn.lon = new_location[2]
                pkmn.save()

                # Remove the new location from the list of available locations
                pkmn_gen.remove(new_location)
        else:
            # If table empty, do a full shuffle
            shuffle_pkmn(request, number, 'full')

    return HttpResponse(f'Shuffled {number} pokemon {shuffle_type}ly.')


# Helper functions
def gen_pkmn(number, range_min, range_max):
    # Bound min and max to 1 and 898
    if range_min < 1:
        range_min = 1
    if range_max > 898:
        range_max = 898

    pkmn_nums = random.sample(range(range_min, range_max), number)

    results = []

    # assign lat and long to each pokemon
    for num in pkmn_nums:
        lat = round(random.uniform(min_lat, max_lat), 6)
        lon = round(random.uniform(min_lon, max_lon), 6)
        results.append((num, lat, lon))

    return results

# Get pokemon info and return as json 
def get_pkmn_json(pkmnlocation):
    id = pkmnlocation.pkmn_id
    pkmn = client.get_pokemon(id)[0]
    name = pkmn.name
    img = pkmn.sprites.front_default
    lat = pkmnlocation.lat
    lon = pkmnlocation.lon
    capture_roll = int(np.floor(pkmn.base_experience/10))

    # Cap capture roll at 20
    if capture_roll > 20:
        capture_roll = 20

    return {
        'id': id,
        'name': name,
        'img': img,
        'lat': lat,
        'lon': lon,
        'capture_roll': capture_roll
    }
    

# Haversine distance to calculate meter distance between two coordinates based on https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000 # Radius of earth in meters. 

    return c * r