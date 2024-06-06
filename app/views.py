from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Login, Profile, Recipe
from .forms import UserForm, ProfileForm, RecipeForm
from django.contrib.auth import logout as auth_logout

def home(request):
    return render(request, 'home.html')

def profile(request, user_id):
    user_profile = get_object_or_404(Profile, user__id=user_id)
    latest_recipes = Recipe.objects.filter(user=user_profile.user).order_by('-created_at')[:4]
    return render(request, 'profile.html', {'profile': user_profile, 'latest_recipes': latest_recipes})

@login_required
def profiles_list(request):
    profiles = Profile.objects.all()
    return render(request, 'profiles_list.html', {'profiles': profiles})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', user_id=request.user.id)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def signup(request):
    return render(request, 'signup.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        picture = request.FILES.get('picture')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})
        
        if password == confirm_password:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # Profile creation is handled by the post_save signal
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                profile.phone_number = phone_number
                profile.address = address
                profile.picture = picture
                profile.save()
            
            auth_login(request, user)
            return redirect('profile', user_id=user.id)
        else:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
    else:
        return redirect('signup')
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            Login.objects.create(user=user, successful=True)
            return redirect('home')
        else:
            user = User.objects.filter(username=username).first()
            if user:
                Login.objects.create(user=user, successful=False)
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def recipe_detail(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    return render(request, 'recipe.html', {'recipe': recipe})

def recipes_list(request):
    recipes = Recipe.objects.all()  # Fetch all recipes from the database
    return render(request, 'recipes_list.html', {'recipes': recipes})

@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user  # Set the user to the currently logged-in user
            recipe.save()
            return redirect('profile', user_id=request.user.id)
    else:
        form = RecipeForm()
    return render(request, 'add_recipe.html', {'form': form})

@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to a success page or the recipe detail
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'edit_recipe.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')
   
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

