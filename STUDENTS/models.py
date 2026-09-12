from django.db import models


class student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()
    course = models.CharField(max_length=100)
    year = models.CharField(max_length=20, default='Year 1')
    section = models.CharField(max_length=20, default='A')
    semester = models.CharField(max_length=20, default='Semester 1')

    def __str__(self):
        return self.name