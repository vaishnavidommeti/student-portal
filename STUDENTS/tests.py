from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import (
	Assignment,
	Assessment,
	Attendance,
	Enrollment,
	Grade,
	Notice,
	Student,
	Subject,
	Submission,
)

User = get_user_model()


class StudentPortalTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='student.one',
			email='student.one@example.edu',
			password='GoodPassword!238',
		)
		self.student = Student.objects.create(
			user=self.user,
			name='Jordan Lee',
			age=20,
			email=self.user.email,
			department='Computer Science',
		)
		self.other_user = User.objects.create_user(
			username='student.two',
			email='student.two@example.edu',
			password='GoodPassword!238',
		)
		self.other_student = Student.objects.create(
			user=self.other_user,
			name='Casey Morgan',
			age=21,
			email=self.other_user.email,
			department='Design',
		)
		self.subject = Subject.objects.create(
			code='CS101',
			title='Foundations of Computing',
			department='Computer Science',
			semester=1,
		)
		self.enrollment = Enrollment.objects.create(student=self.student, subject=self.subject)
		self.assignment = Assignment.objects.create(
			subject=self.subject,
			title='First lab',
			instructions='Describe your approach.',
		)
		self.client.force_login(self.user)

	def test_homepage_renders_registration_for_guests(self):
		self.client.logout()
		response = self.client.get(reverse('home'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Create your account')
		self.assertTemplateUsed(response, 'STUDENTS/home.html')

	def test_registration_creates_hashed_account_and_student_id(self):
		self.client.logout()
		response = self.client.post(reverse('home'), {
			'username': 'new.student',
			'email': 'new.student@example.edu',
			'name': 'Avery Kim',
			'age': 19,
			'department': 'Biology',
			'year': 'Year 1',
			'section': 'A',
			'semester': 'Semester 1',
			'password1': 'LongUniquePassword!482',
			'password2': 'LongUniquePassword!482',
		})
		self.assertRedirects(response, reverse('dashboard'))
		user = User.objects.get(username='new.student')
		profile = Student.objects.get(user=user)
		self.assertTrue(user.check_password('LongUniquePassword!482'))
		self.assertNotEqual(user.password, 'LongUniquePassword!482')
		self.assertTrue(profile.student_id.startswith('STU'))
		self.assertEqual(profile.department, 'Biology')
		self.assertEqual(int(response.wsgi_request.user.pk), user.pk)

	def test_duplicate_registration_email_is_rejected(self):
		self.client.logout()
		response = self.client.post(reverse('home'), {
			'username': 'another.student',
			'email': self.student.email,
			'name': 'Taylor Reed',
			'age': 19,
			'department': 'Biology',
			'year': 'Year 1',
			'section': 'A',
			'semester': 'Semester 1',
			'password1': 'LongUniquePassword!482',
			'password2': 'LongUniquePassword!482',
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'already exists')
		self.assertFalse(User.objects.filter(username='another.student').exists())

	def test_login_accepts_email_and_username(self):
		self.client.logout()
		response = self.client.post(reverse('login'), {
			'username': self.user.email,
			'password': 'GoodPassword!238',
		})
		self.assertRedirects(response, reverse('dashboard'))
		self.client.post(reverse('logout'))
		response = self.client.post(reverse('login'), {
			'username': self.user.username,
			'password': 'GoodPassword!238',
		})
		self.assertRedirects(response, reverse('dashboard'))

	def test_dashboard_shows_only_signed_in_student_summary(self):
		response = self.client.get(reverse('dashboard'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.student.student_id)
		self.assertContains(response, 'Foundations of Computing')
		self.assertNotContains(response, self.other_student.student_id or 'CASEY')

	def test_student_can_edit_only_their_own_profile(self):
		response = self.client.post(reverse('profile_edit'), {'name': 'Jordan Taylor', 'age': 22})
		self.assertRedirects(response, reverse('dashboard'))
		self.student.refresh_from_db()
		self.other_student.refresh_from_db()
		self.user.refresh_from_db()
		self.assertEqual(self.student.name, 'Jordan Taylor')
		self.assertEqual(self.student.age, 22)
		self.assertEqual(self.user.first_name, 'Jordan')
		self.assertEqual(self.other_student.name, 'Casey Morgan')

	def test_student_pages_require_login_and_profile(self):
		self.client.logout()
		for url_name in ('dashboard', 'subjects', 'attendance', 'grades', 'assignments', 'notices'):
			response = self.client.get(reverse(url_name))
			self.assertRedirects(response, f'{reverse("login")}?next={reverse(url_name)}')

		staff_without_profile = User.objects.create_user(
			username='staff.member',
			email='staff@example.edu',
			password='GoodPassword!238',
			is_staff=True,
		)
		self.client.force_login(staff_without_profile)
		self.assertEqual(self.client.get(reverse('dashboard')).status_code, 403)

	def test_assignment_records_and_submission_are_student_scoped(self):
		other_subject = Subject.objects.create(
			code='DS101',
			title='Design Studio',
			department='Design',
			semester=1,
		)
		other_assignment = Assignment.objects.create(
			subject=other_subject,
			title='Private design task',
			instructions='Not assigned to this student.',
		)
		response = self.client.get(reverse('assignments'))
		self.assertContains(response, self.assignment.title)
		self.assertNotContains(response, other_assignment.title)
		self.assertEqual(
			self.client.get(reverse('submit_assignment', args=[other_assignment.pk])).status_code,
			404,
		)
		response = self.client.post(
			reverse('submit_assignment', args=[self.assignment.pk]),
			{'response': 'I tested the solution with three examples.'},
		)
		self.assertRedirects(response, reverse('assignments'))
		submission = Submission.objects.get(assignment=self.assignment, student=self.student)
		self.assertEqual(submission.response, 'I tested the solution with three examples.')

	def test_attendance_grades_and_notices_render_for_student(self):
		Attendance.objects.create(enrollment=self.enrollment, status=Attendance.Status.PRESENT)
		assessment = Assessment.objects.create(subject=self.subject, title='Quiz one', max_score=20)
		Grade.objects.create(student=self.student, assessment=assessment, score=18)
		Notice.objects.create(title='Lab room update', body='The lab opens at nine.')
		Notice.objects.create(title='Design review', body='Private department notice.', department='Design')

		self.assertContains(self.client.get(reverse('attendance')), 'Present')
		self.assertContains(self.client.get(reverse('grades')), 'Quiz one')
		notice_response = self.client.get(reverse('notices'))
		self.assertContains(notice_response, 'Lab room update')
		self.assertNotContains(notice_response, 'Design review')

	def test_grade_cannot_exceed_assessment_maximum(self):
		assessment = Assessment.objects.create(subject=self.subject, title='Midterm', max_score=25)
		grade = Grade(student=self.student, assessment=assessment, score=26)
		with self.assertRaises(ValidationError):
			grade.full_clean()

	def test_submission_score_cannot_exceed_assignment_maximum(self):
		submission = Submission(
			assignment=self.assignment,
			student=self.student,
			response='Completed work.',
			score=101,
		)
		with self.assertRaises(ValidationError):
			submission.full_clean()

	def test_staff_dashboard_and_admin_are_staff_only(self):
		self.assertEqual(self.client.get(reverse('staff_dashboard')).status_code, 302)
		staff_user = User.objects.create_user(
			username='admin.member',
			email='admin@example.edu',
			password='GoodPassword!238',
			is_staff=True,
		)
		self.client.force_login(staff_user)
		self.assertEqual(self.client.get(reverse('staff_dashboard')).status_code, 200)
		view_students = Permission.objects.get(
			codename='view_student',
			content_type__app_label='STUDENTS',
		)
		staff_user.user_permissions.add(view_students)
		self.assertEqual(self.client.get(reverse('admin:STUDENTS_student_changelist')).status_code, 200)
