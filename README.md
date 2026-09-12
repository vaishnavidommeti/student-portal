# 🎓 Student Registration Portal

A simple and user-friendly **Student Registration Portal** developed using **Python Django**.

## 📌 About the Project

The Student Registration Portal allows students to enter and submit their academic and personal details through an online registration form.

The application stores student information securely in a database and provides an **Admin Panel** to view and manage registered students.

## ✨ Features

- 📝 Student Registration Form
- 👤 Student Name and Email
- 🎂 Age details
- 🎓 Course selection
- 📚 Current Year
- 🏫 Section selection
- 📖 Current Semester
- ✅ Registration success message
- 🔐 Django Admin Panel
- 🔎 Search registered students
- 💾 Database storage using SQLite

## 🛠️ Technologies Used

- Python
- Django
- HTML
- CSS
- SQLite
- Git & GitHub

## 📂 Project Structure

```text
studentregistration portal/
│
├── STUDENTS/
│   ├── migrations/
│   ├── templates/
│   │   └── home.html
│   ├── static/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── student_portal/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── db.sqlite3
├── manage.py
└── README.md
