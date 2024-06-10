from django import forms
from django.contrib.auth.models import User
from .models import Profile, Recipe, Comment

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'picture', 'facebook_url', 'instagram_url', 'youtube_url', 'twitter_url', 'linkedin_url']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        user = profile.user
        user.username = self.cleaned_data.get('username', user.username)
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        if commit:
            user.save()
            profile.save()
        return profile

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'ingredients', 'preparation_time', 'cooking_time', 'instructions', 'serving_size', 'tips', 'picture']

    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']