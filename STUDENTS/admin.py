from django.contrib import admin
from .models import student

@admin.register(student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'course', 'age')
	search_fields = ('name', 'email', 'course')



