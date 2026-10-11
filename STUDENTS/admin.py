from django.contrib import admin

from .models import (
	Assignment,
	Assessment,
	Attendance,
	Enrollment,
	Grade,
	Notice,
	Student,
	Submission,
	Subject,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('student_id', 'name', 'email', 'department', 'year', 'semester')
	list_filter = ('department', 'year', 'semester', 'section')
	search_fields = ('student_id', 'name', 'email', 'department')
	readonly_fields = ('student_id',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ('code', 'title', 'department', 'semester', 'credits')
	list_filter = ('department', 'semester')
	search_fields = ('code', 'title', 'department')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
	list_display = ('student', 'subject', 'academic_year', 'status', 'enrolled_at')
	list_filter = ('academic_year', 'status', 'subject__department', 'subject__semester')
	search_fields = ('student__student_id', 'student__name', 'subject__code', 'subject__title')
	autocomplete_fields = ('student', 'subject')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ('enrollment', 'date', 'status')
	list_filter = ('status', 'date', 'enrollment__subject')
	search_fields = ('enrollment__student__student_id', 'enrollment__student__name', 'enrollment__subject__code')
	autocomplete_fields = ('enrollment',)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
	list_display = ('title', 'subject', 'category', 'held_on', 'max_score')
	list_filter = ('category', 'subject__department', 'subject__semester')
	search_fields = ('title', 'subject__code', 'subject__title')
	autocomplete_fields = ('subject',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
	list_display = ('student', 'assessment', 'score', 'recorded_at')
	list_filter = ('assessment__subject', 'assessment__category')
	search_fields = ('student__student_id', 'student__name', 'assessment__title')
	autocomplete_fields = ('student', 'assessment')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
	list_display = ('title', 'subject', 'due_at', 'max_score')
	list_filter = ('subject__department', 'subject__semester', 'due_at')
	search_fields = ('title', 'subject__code', 'subject__title')
	autocomplete_fields = ('subject',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
	list_display = ('student', 'assignment', 'submitted_at', 'score')
	list_filter = ('assignment__subject', 'submitted_at')
	search_fields = ('student__student_id', 'student__name', 'assignment__title')
	autocomplete_fields = ('student', 'assignment')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
	list_display = ('title', 'department', 'published_at', 'is_published')
	list_filter = ('is_published', 'department', 'published_at')
	search_fields = ('title', 'body', 'department')



