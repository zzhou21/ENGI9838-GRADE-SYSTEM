# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    The 'users' table keeps user information: username, password, email, role.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    role = db.Column(
        db.Enum('student', 'teacher', 'admin', name='user_role_enum'),
        default='student'
    )
    courses_taught = db.relationship('Course', backref='teacher_user', lazy=True)

class Course(db.Model):
    """
    The 'courses' table keeps course_name, teacher_id, course_code, etc.
    """
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Enrollment(db.Model):
    """
    The 'enrollments' table for a many-to-many relationship between students and courses.
    """
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    user = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

class Assignment(db.Model):
    """
    The 'assignments' table for tasks/exams under a course.
    """
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)

    course = db.relationship('Course', backref='assignments')

class Submission(db.Model):
    """
    The 'submissions' table for a student's assignment submission.
    """
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_late = db.Column(db.Boolean, default=False)

    assignment = db.relationship('Assignment', backref='submissions')
    student = db.relationship('User', backref='submissions')

class Grade(db.Model):
    """
    The 'grades' table for the teacher's feedback on a submission.
    """
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)

    submission = db.relationship(
        'Submission', 
        foreign_keys=[submission_id],
        backref=db.backref('grade', uselist=False),
        primaryjoin="Grade.submission_id==Submission.id"
    )