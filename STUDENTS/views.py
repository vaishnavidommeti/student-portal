from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import StudentProfileForm, StudentRegistrationForm, SubmissionForm
from .models import (
    Assignment,
    Attendance,
    Enrollment,
    Grade,
    Notice,
    Student,
    Subject,
    Submission,
)


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = StudentRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your student account is ready.')
        return redirect('dashboard')
    return render(request, 'STUDENTS/home.html', {'form': form})


def _student_for(request):
    try:
        return request.user.student_profile
    except Student.DoesNotExist as error:
        raise PermissionDenied('A student profile is required to view this page.') from error


def _visible_notices(student):
    return Notice.objects.filter(is_published=True).filter(
        Q(department='') | Q(department__iexact=student.department)
    )


@login_required
def dashboard(request):
    student = _student_for(request)
    enrollments = Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE)
    attendance = Attendance.objects.filter(enrollment__in=enrollments)
    total_sessions = attendance.exclude(status=Attendance.Status.EXCUSED).count()
    attended = attendance.filter(status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE]).count()
    attendance_rate = round(attended * 100 / total_sessions) if total_sessions else None
    assignments = Assignment.objects.filter(subject__enrollments__in=enrollments).distinct()
    upcoming_assignments = assignments.filter(due_at__gte=timezone.now()).select_related('subject')[:5]
    context = {
        'student': student,
        'enrollments': enrollments.select_related('subject'),
        'subject_count': enrollments.count(),
        'attendance_rate': attendance_rate,
        'recent_grades': Grade.objects.filter(student=student).select_related('assessment__subject')[:5],
        'upcoming_assignments': upcoming_assignments,
        'notices': _visible_notices(student)[:4],
    }
    return render(request, 'STUDENTS/dashboard.html', context)


@login_required
def profile_edit(request):
    student = _student_for(request)
    form = StudentProfileForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        profile = form.save()
        name_parts = profile.name.strip().split(maxsplit=1)
        request.user.first_name = name_parts[0]
        request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        request.user.save(update_fields=['first_name', 'last_name'])
        messages.success(request, 'Your profile was updated.')
        return redirect('dashboard')
    return render(request, 'STUDENTS/profile_edit.html', {'form': form, 'student': student})


@login_required
def subjects(request):
    student = _student_for(request)
    enrollments = Enrollment.objects.filter(student=student).select_related('subject')
    return render(request, 'STUDENTS/records.html', {
        'title': 'My subjects',
        'description': 'Your current and completed subject enrollments.',
        'columns': ['Code', 'Subject', 'Department', 'Semester', 'Credits', 'Status'],
        'rows': [[enrollment.subject.code, enrollment.subject.title, enrollment.subject.department, enrollment.subject.get_semester_display(), enrollment.subject.credits, enrollment.get_status_display()] for enrollment in enrollments],
        'empty_message': 'No subjects have been assigned to your profile yet.',
    })


@login_required
def attendance_records(request):
    student = _student_for(request)
    records = Attendance.objects.filter(enrollment__student=student).select_related('enrollment__subject')
    return render(request, 'STUDENTS/records.html', {
        'title': 'Attendance',
        'description': 'A record of attendance across your enrolled subjects.',
        'columns': ['Date', 'Subject', 'Status', 'Note'],
        'rows': [[record.date, record.enrollment.subject.title, record.get_status_display(), record.note or '—'] for record in records],
        'empty_message': 'Attendance records will appear here when they are added.',
    })


@login_required
def grades(request):
    student = _student_for(request)
    records = Grade.objects.filter(student=student).select_related('assessment__subject')
    return render(request, 'STUDENTS/records.html', {
        'title': 'Marks & grades',
        'description': 'Assessment results recorded for your subjects.',
        'columns': ['Assessment', 'Subject', 'Category', 'Score', 'Maximum', 'Date'],
        'rows': [[grade.assessment.title, grade.assessment.subject.code, grade.assessment.get_category_display(), grade.score, grade.assessment.max_score, grade.assessment.held_on or '—'] for grade in records],
        'empty_message': 'Grades will appear here after your instructors publish results.',
    })


@login_required
def assignments(request):
    student = _student_for(request)
    enrollments = Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE)
    records = Assignment.objects.filter(subject__enrollments__in=enrollments).distinct().select_related('subject')
    submissions = {
        submission.assignment_id: submission
        for submission in Submission.objects.filter(student=student, assignment__in=records)
    }
    items = [
        {'assignment': assignment, 'submission': submissions.get(assignment.pk)}
        for assignment in records
    ]
    return render(request, 'STUDENTS/assignments.html', {
        'assignments': items,
        'now': timezone.now(),
    })


@login_required
def submit_assignment(request, assignment_id):
    student = _student_for(request)
    assignment = get_object_or_404(
        Assignment.objects.filter(subject__enrollments__student=student).select_related('subject'),
        pk=assignment_id,
    )
    submission = Submission.objects.filter(assignment=assignment, student=student).first()
    form = SubmissionForm(request.POST or None, instance=submission)
    if request.method == 'POST' and form.is_valid():
        submission = form.save(commit=False)
        submission.assignment = assignment
        submission.student = student
        submission.save()
        messages.success(request, 'Your submission was saved.')
        return redirect('assignments')
    return render(request, 'STUDENTS/submit_assignment.html', {
        'assignment': assignment,
        'form': form,
        'submission': submission,
    })


@login_required
def notices(request):
    return render(request, 'STUDENTS/notices.html', {
        'notices': _visible_notices(_student_for(request)),
    })


@staff_member_required
def staff_dashboard(request):
    context = {
        'student_count': Student.objects.count(),
        'subject_count': Subject.objects.count(),
        'attendance_count': Attendance.objects.count(),
        'assignment_count': Assignment.objects.count(),
        'recent_students': Student.objects.order_by('-id')[:6],
    }
    return render(request, 'STUDENTS/staff_dashboard.html', context)
