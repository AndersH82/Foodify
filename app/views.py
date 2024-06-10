from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Login, Profile, Recipe, Comment, LikeDislike
from .forms import UserForm, ProfileForm, RecipeForm, CommentForm
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.conf import settings
import os

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
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to a home page or any other page
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

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
        facebook_url = request.POST.get('facebook_url')
        instagram_url = request.POST.get('instagram_url')
        youtube_url = request.POST.get('youtube_url')
        twitter_url = request.POST.get('twitter_url')
        linkedin_url = request.POST.get('linkedin_url')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})
        
        if password == confirm_password:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                profile.phone_number = phone_number
                profile.address = address
                profile.picture = picture
                profile.facebook_url = facebook_url
                profile.instagram_url = instagram_url
                profile.youtube_url = youtube_url
                profile.twitter_url = twitter_url
                profile.linkedin_url = linkedin_url
                profile.save()
            
            auth_login(request, user)
            return redirect('profile', user_id=user.id)
        else:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
    else:
        return render(request, 'signup.html')
    
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
    recipe = get_object_or_404(Recipe, id=recipe_id)
    comments = recipe.comments.all()
    likes = recipe.likes_dislikes.filter(is_like=True).count()
    dislikes = recipe.likes_dislikes.filter(is_like=False).count()

    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.recipe = recipe
                comment.save()
                return redirect('recipe_detail', recipe_id=recipe.id)
        elif 'like' in request.POST or 'dislike' in request.POST:
            is_like = 'like' in request.POST
            LikeDislike.objects.update_or_create(
                user=request.user,
                recipe=recipe,
                defaults={'is_like': is_like}
            )
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        comment_form = CommentForm()

    return render(request, 'recipe.html', {
        'recipe': recipe,
        'comments': comments,
        'likes': likes,
        'dislikes': dislikes,
        'comment_form': comment_form
    })

def recipes_list(request):
    recipes = Recipe.objects.all()  
    return render(request, 'recipes_list.html', {'recipes': recipes})

@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user  
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
            return redirect('home')  
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'edit_recipe.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your profile has been deleted successfully.')
        return redirect('home')
    return render(request, 'delete_profile.html')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

