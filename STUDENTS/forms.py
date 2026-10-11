from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Student, Submission

User = get_user_model()


class StudentRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autocomplete': 'name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    age = forms.IntegerField(min_value=13, max_value=100)
    department = forms.CharField(max_length=100)
    year = forms.ChoiceField(choices=Student.YEAR_CHOICES, label='Year of study')
    section = forms.ChoiceField(choices=Student.SECTION_CHOICES)
    semester = forms.ChoiceField(choices=Student.SEMESTER_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
        }
        labels = {'username': 'Username'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists() or Student.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email address already exists.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        name_parts = self.cleaned_data['name'].strip().split(maxsplit=1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                name=self.cleaned_data['name'].strip(),
                age=self.cleaned_data['age'],
                email=user.email,
                department=self.cleaned_data['department'].strip(),
                year=self.cleaned_data['year'],
                section=self.cleaned_data['section'],
                semester=self.cleaned_data['semester'],
            )
        return user


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('name', 'age')
        widgets = {'name': forms.TextInput(attrs={'autocomplete': 'name'})}

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 13 or age > 100:
            raise ValidationError('Enter an age between 13 and 100.')
        return age


class StudentAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or email'
        self.fields['username'].widget.attrs['autocomplete'] = 'username'

    def clean(self):
        identifier = self.cleaned_data.get('username')
        if identifier and '@' in identifier:
            user = User.objects.filter(email__iexact=identifier).only('username').first()
            if user:
                self.cleaned_data['username'] = user.get_username()
        return super().clean()


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('response',)
        widgets = {'response': forms.Textarea(attrs={'rows': 6})}