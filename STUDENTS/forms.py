from django import forms

from .models import student


class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = student
        fields = ('name', 'email', 'age', 'course', 'year', 'section', 'semester')
        labels = {
            'year': 'Current year of study',
            'section': 'Section',
            'semester': 'Current semester',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Jordan Lee', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'autocomplete': 'email'}),
            'age': forms.NumberInput(attrs={'placeholder': '18', 'min': '13', 'max': '100'}),
            'course': forms.TextInput(attrs={'placeholder': 'e.g. Computer Science'}),
            'year': forms.Select(choices=[('Year 1', 'Year 1'), ('Year 2', 'Year 2'), ('Year 3', 'Year 3'), ('Year 4', 'Year 4')]),
            'section': forms.Select(choices=[('A', 'Section A'), ('B', 'Section B'), ('C', 'Section C'), ('D', 'Section D')]),
            'semester': forms.Select(choices=[(str(number), f'Semester {number}') for number in range(1, 9)]),
        }

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 13 or age > 100:
            raise forms.ValidationError('Please enter an age between 13 and 100.')
        return age