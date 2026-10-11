from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


def generate_student_id():
    return f'STU{uuid4().hex[:12].upper()}'


def current_academic_year():
    today = timezone.localdate()
    start_year = today.year if today.month >= 8 else today.year - 1
    return f'{start_year}-{start_year + 1}'


class Student(models.Model):
    YEAR_CHOICES = [(f'Year {number}', f'Year {number}') for number in range(1, 5)]
    SECTION_CHOICES = [(letter, f'Section {letter}') for letter in 'ABCD']
    SEMESTER_CHOICES = [(f'Semester {number}', f'Semester {number}') for number in range(1, 9)]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        null=True,
        blank=True,
    )
    student_id = models.CharField(max_length=15, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(13)])
    email = models.EmailField()
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, default='Year 1')
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='A')
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, default='Semester 1')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = generate_student_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.student_id or "unassigned"})'


class Subject(models.Model):
    SEMESTER_CHOICES = [(number, f'Semester {number}') for number in range(1, 9)]

    code = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=120)
    department = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES)
    credits = models.PositiveSmallIntegerField(default=3)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.title}'


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='enrollments')
    academic_year = models.CharField(max_length=9, default=current_academic_year)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    enrolled_at = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['subject__code']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'academic_year'],
                name='unique_student_subject_year',
            ),
        ]

    def __str__(self):
        return f'{self.student} - {self.subject}'


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'
        EXCUSED = 'excused', 'Excused'

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=Status.choices)
    note = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['enrollment', 'date'], name='unique_daily_attendance'),
        ]

    def __str__(self):
        return f'{self.enrollment} - {self.date}: {self.get_status_display()}'


class Assessment(models.Model):
    class Category(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        COURSEWORK = 'coursework', 'Coursework'
        EXAM = 'exam', 'Exam'
        PROJECT = 'project', 'Project'

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.COURSEWORK)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100, validators=[MinValueValidator(0.01)])
    held_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-held_on', 'title']

    def __str__(self):
        return f'{self.subject.code}: {self.title}'


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='grades')
    score = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    feedback = models.CharField(max_length=500, blank=True)
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assessment__held_on', 'assessment__title']
        constraints = [
            models.UniqueConstraint(fields=['student', 'assessment'], name='unique_student_assessment_grade'),
        ]

    def clean(self):
        super().clean()
        if self.assessment_id and self.score is not None and self.score > self.assessment.max_score:
            raise ValidationError({'score': 'Score cannot exceed the assessment maximum.'})

    def __str__(self):
        return f'{self.student} - {self.assessment}: {self.score}'


class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=140)
    instructions = models.TextField()
    due_at = models.DateTimeField(null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100, validators=[MinValueValidator(0.01)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_at', '-created_at']

    def __str__(self):
        return f'{self.subject.code}: {self.title}'


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    response = models.TextField()
    submitted_at = models.DateTimeField(auto_now=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        constraints = [
            models.UniqueConstraint(fields=['assignment', 'student'], name='unique_student_assignment_submission'),
        ]

    def clean(self):
        super().clean()
        if self.assignment_id and self.score is not None and self.score > self.assignment.max_score:
            raise ValidationError({'score': 'Score cannot exceed the assignment maximum.'})

    def __str__(self):
        return f'{self.student} - {self.assignment}'


class Notice(models.Model):
    title = models.CharField(max_length=160)
    body = models.TextField()
    department = models.CharField(max_length=100, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title