from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import StudentRegistrationForm
def home(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registered successfully')
            return redirect('home')
    else:
        form = StudentRegistrationForm()

    return render(request, 'STUDENTS/home.html', {'form': form})
