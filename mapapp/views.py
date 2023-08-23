from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import user_pkmn
import pokepy

client = pokepy.V2Client()

# Create your views here.
def home_page(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    else:
        return redirect('mapapp:login')

def admin_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'admin.html')
    else:
        return redirect('mapapp:home')
    
def pokedex_page(request):
    if request.user.is_authenticated:
        dex = client.get_pokedex(1)[0].pokemon_entries
        pkmn_list = []
        user_pkmns = user_pkmn.objects.filter(user=request.user)

        for pkmn in dex:

            temp = {
                'id': pkmn.entry_number,
                'name': pkmn.pokemon_species.name,
                'captured': 0,
                'count': 0,
                'img': '',
            }

            if user_pkmns.filter(pkmn_id=pkmn.entry_number).exists():
                pkmn_img = client.get_pokemon(pkmn.entry_number)[0].sprites.front_default

                if user_pkmns.filter(pkmn_id=pkmn.entry_number).first().state == 1:
                    temp['captured'] = 2
                    temp['count'] = user_pkmns.filter(pkmn_id=pkmn.entry_number)[0].count
                else:
                    temp['captured'] = 1

                temp['img'] = pkmn_img

            pkmn_list.append(temp)

        return render(request, 'pokedex.html', {'pkmn_list': pkmn_list})
    else:
        return redirect('mapapp:login')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('mapapp:home')  
        
        else:
            error_message = "Invalid username or password."
    else:
        error_message = ""

    return render(request
    , 'login.html', {'error_message': error_message})

def signup_page(request):
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('mapapp:home')  
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

def logout_page(request):
    logout(request)
    return redirect('mapapp:login')