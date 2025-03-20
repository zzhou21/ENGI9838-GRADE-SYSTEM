# app.py
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

# Import the db and models from app.models
from app.models import db, User, Course, Enrollment, Assignment, Submission, Grade
# Import all functions from each service
from app.services.user_service import (
    create_user, authenticate_user, get_user_by_id, get_user_by_username,
    update_user, delete_user
)
from app.services.course_service import (
    create_course as cs_create_course, get_course_by_id, get_all_courses,
    update_course as cs_update_course, delete_course as cs_delete_course
)
from app.services.assignment_service import (
    create_assignment, get_assignment_by_id, get_assignments_by_course,
    update_assignment, delete_assignment
)
from app.services.submission_service import (
    create_submission, get_submission_by_id, get_submissions_by_assignment,
    get_submissions_by_student, update_submission, delete_submission
)
from app.services.grade_service import (
    assign_grade, get_grade_by_submission, update_grade as gd_update_grade,
    delete_grade as gd_delete_grade
)

############################################################################
# 1) Flask Application Configuration
############################################################################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Zzy19980220@localhost:3306/grade_system"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup upload folder for assignment submissions
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Link our 'db' with this app
db.init_app(app)

############################################################################
# 2) Database Initialization (if not existed)
############################################################################

with app.app_context():
    db.create_all()

############################################################################
# 3) Helper Functions and Decorators
############################################################################

def role_required(role):
    """
    Decorator to check if user is logged in and has the required role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page", "error")
                return redirect(url_for('login'))
            
            if 'role' not in session or session['role'] != role:
                flash(f"You need to be a {role} to access this page", "error")
                return redirect(url_for('index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

############################################################################
# 4) Routes (using services)
############################################################################

@app.route('/')
def index():
    """
    Home page with links.
    """
    return render_template('index.html')


########################
# USER-RELATED ROUTES
########################

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route: calls create_user from user_service.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        role = request.form.get('role', 'student')
        try:
            create_user(username, password, email, role)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except ValueError as e:
            flash(f"Error: {e}", "error")
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route: calls authenticate_user.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return "Admin or unknown role - not handled."
        else:
            flash("Invalid credentials!", "error")
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Clears session and returns to homepage.
    """
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('index'))


@app.route('/user/update', methods=['GET','POST'])
@role_required('admin')  # Typically only admin can update users
def user_update():
    """
    Simple route to demonstrate update_user from user_service.
    Requires a form with user_id, new_email, new_role, new_password.
    """
    user = None
    if request.args.get('user_id'):
        user = get_user_by_id(request.args.get('user_id'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_email = request.form.get('new_email') or None
        new_role = request.form.get('new_role') or None
        new_password = request.form.get('new_password') or None

        updated = update_user(user_id, new_email, new_role, new_password)
        if updated:
            flash(f"User {updated.username} updated.", "success")
            return redirect(url_for('index'))
        else:
            flash("User not found.", "error")
    return render_template('user_update.html', user=user)


@app.route('/user/delete/<int:user_id>', methods=['GET'])
@role_required('admin')  # Typically only admin can delete users
def user_delete(user_id):
    """
    Demonstrates delete_user from user_service.
    """
    delete_user(user_id)
    flash(f"User {user_id} deleted if existed.", "info")
    return redirect(url_for('index'))


########################
# DASHBOARD ROUTES
########################

@app.route('/teacher_dashboard')
@role_required('teacher')
def teacher_dashboard():
    """
    Teacher's dashboard (requires role == 'teacher').
    Shows the teacher's information and links to their functions.
    """
    teacher = User.query.get(session['user_id'])
    return render_template('teacher_dashboard.html', teacher_name=teacher.username)


@app.route('/student_dashboard')
@role_required('student')
def student_dashboard():
    """
    Student's dashboard (requires role == 'student').
    Shows the student's information and links to their functions.
    """
    student = User.query.get(session['user_id'])
    return render_template('student_dashboard.html', student_name=student.username)


########################
# COURSE-RELATED ROUTES
########################

@app.route('/create_course', methods=['GET', 'POST'])
@role_required('teacher')
def create_course_route():
    """
    Calls course_service.create_course.
    """
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        course_code = request.form.get('course_code')
        desc = request.form.get('description','')
        teacher_id = session['user_id']
        try:
            cs_create_course(course_name, teacher_id, course_code, desc)
            flash("Course created successfully!", "success")
            return redirect(url_for('teacher_courses'))
        except ValueError as e:
            flash(str(e), "error")
    return render_template('create_course.html')


@app.route('/list_courses')
def list_courses():
    """
    Uses get_all_courses from course_service.
    """
    courses = get_all_courses()
    return render_template('list_courses.html', courses=courses)


@app.route('/course/update', methods=['GET','POST'])
@role_required('teacher')
def course_update():
    """
    Demonstrates update_course from course_service.
    Now with form pre-filling support.
    """
    # Find the course for pre-filling if we have an ID
    course = None
    if request.args.get('course_id'):
        course_id = request.args.get('course_id')
        course = get_course_by_id(course_id)
        
        # Check if this teacher is allowed to edit this course
        if course and course.teacher_id != session['user_id']:
            flash("You can only edit your own courses", "error")
            return redirect(url_for('teacher_courses'))
    
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        new_name = request.form.get('new_name') or None
        new_teacher_id = request.form.get('new_teacher_id') or None
        new_code = request.form.get('new_code') or None
        new_desc = request.form.get('new_desc') or None

        try:
            updated_course = cs_update_course(course_id, new_name, new_teacher_id, new_code, new_desc)
            if updated_course:
                flash(f"Course {updated_course.course_name} updated.", "success")
                return redirect(url_for('teacher_courses'))
            else:
                flash("Course not found.", "error")
        except ValueError as e:
            flash(str(e), "error")
    return render_template('course_update.html', course=course)


@app.route('/course/delete/<int:course_id>')
@role_required('teacher')
def course_delete(course_id):
    """
    Demonstrates delete_course from course_service.
    """
    # First check if this course belongs to the teacher
    course = get_course_by_id(course_id)
    if not course or course.teacher_id != session['user_id']:
        flash("You can only delete your own courses", "error")
        return redirect(url_for('teacher_courses'))
    
    deleted = cs_delete_course(course_id)
    if deleted:
        flash(f"Course {course_id} deleted.", "success")
    else:
        flash("Course not found.", "error")
    return redirect(url_for('teacher_courses'))


########################
# TEACHER COURSE MANAGEMENT ROUTES
########################

@app.route('/teacher_courses')
@role_required('teacher')
def teacher_courses():
    """
    Shows the courses taught by the teacher.
    """
    teacher_id = session['user_id']
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    return render_template('teacher_courses.html', courses=courses)


@app.route('/teacher_view_submissions')
@role_required('teacher')
def teacher_view_submissions():
    """
    Teacher views all submissions for their courses' assignments.
    """
    teacher_id = session['user_id']
    
    # Get all courses taught by this teacher
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    course_ids = [course.id for course in courses]
    
    # Get all assignments for these courses
    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
    assignment_ids = [assignment.id for assignment in assignments]
    
    # Get all submissions for these assignments
    submissions = Submission.query.filter(Submission.assignment_id.in_(assignment_ids)).all()
    
    # Enhance the submissions with additional info
    enhanced_submissions = []
    for sub in submissions:
        # Get student name
        student = User.query.get(sub.student_id)
        # Get assignment title
        assignment = Assignment.query.get(sub.assignment_id)
        # Get course name
        course = Course.query.get(assignment.course_id) if assignment else None
        
        # Add to enhanced submissions
        enhanced_submissions.append({
            'id': sub.id,
            'student_name': student.username if student else 'Unknown',
            'assignment_title': assignment.title if assignment else 'Unknown',
            'course_name': course.course_name if course else 'Unknown',
            'file_path': sub.file_path,
            'submitted_at': sub.submitted_at,
            'is_late': sub.is_late,
            'graded': True if sub.grade else False
        })
    
    return render_template('teacher_view_submissions.html', submissions=enhanced_submissions)


@app.route('/teacher_grade')
@role_required('teacher')
def teacher_grade():
    """
    Redirects to the grade assignment page.
    """
    return redirect(url_for('assign_grade_route'))


########################
# ASSIGNMENT ROUTES
########################

@app.route('/create_assignment', methods=['GET','POST'])
@role_required('teacher')
def create_assignment_route():
    """
    Calls assignment_service.create_assignment.
    """
    teacher_id = session['user_id']
    # Get all courses taught by this teacher for the dropdown
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    
    # Check if we have a course_id from query parameters
    course_id = request.args.get('course_id')
    selected_course = None
    if course_id:
        selected_course = get_course_by_id(course_id)
        if selected_course and selected_course.teacher_id != teacher_id:
            selected_course = None  # Reset if the course doesn't belong to this teacher
    
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        title = request.form.get('title')
        desc = request.form.get('description') or None
        due_date_str = request.form.get('due_date') or None
        
        # Convert due_date string to datetime object if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD", "error")
                return render_template('create_assignment.html', courses=courses, selected_course=selected_course)
        
        try:
            # Verify that this course belongs to the teacher
            course = get_course_by_id(course_id)
            if not course or course.teacher_id != teacher_id:
                flash("You can only create assignments for your own courses", "error")
                return render_template('create_assignment.html', courses=courses, selected_course=selected_course)
            
            new_assign = create_assignment(course_id, title, desc, due_date)
            flash(f"Assignment {new_assign.title} created.", "success")
            return redirect(url_for('teacher_courses'))
        except ValueError as e:
            flash(str(e), "error")
    
    return render_template('create_assignment.html', courses=courses, selected_course=selected_course)


@app.route('/assignment/update', methods=['GET','POST'])
@role_required('teacher')
def assignment_update():
    """
    Demonstrates update_assignment from assignment_service.
    """
    teacher_id = session['user_id']
    
    # Get the assignment for pre-filling if we have an ID
    assignment = None
    if request.args.get('assignment_id'):
        assignment_id = request.args.get('assignment_id')
        assignment = get_assignment_by_id(assignment_id)
        
        # Verify that this assignment belongs to one of the teacher's courses
        if assignment:
            course = get_course_by_id(assignment.course_id)
            if not course or course.teacher_id != teacher_id:
                flash("You can only edit assignments for your own courses", "error")
                return redirect(url_for('teacher_courses'))
    
    if request.method == 'POST':
        assignment_id = request.form.get('assignment_id')
        new_title = request.form.get('new_title') or None
        new_desc = request.form.get('new_desc') or None
        new_due_date_str = request.form.get('new_due_date') or None
        
        # Convert new_due_date string to datetime object if provided
        new_due_date = None
        if new_due_date_str:
            try:
                new_due_date = datetime.strptime(new_due_date_str, '%Y-%m-%d')
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD", "error")
                return render_template('assignment_update.html', assignment=assignment)
        
        # Verify that this assignment belongs to one of the teacher's courses
        assign = get_assignment_by_id(assignment_id)
        if assign:
            course = get_course_by_id(assign.course_id)
            if not course or course.teacher_id != teacher_id:
                flash("You can only edit assignments for your own courses", "error")
                return redirect(url_for('teacher_courses'))
        
        updated = update_assignment(assignment_id, new_title, new_desc, new_due_date)
        if updated:
            flash(f"Assignment {updated.title} updated.", "success")
            return redirect(url_for('teacher_courses'))
        else:
            flash("Assignment not found.", "error")
    
    return render_template('assignment_update.html', assignment=assignment)


@app.route('/assignment/delete/<int:assignment_id>')
@role_required('teacher')
def assignment_delete(assignment_id):
    """
    Demonstrates delete_assignment from assignment_service.
    """
    teacher_id = session['user_id']
    
    # Verify that this assignment belongs to one of the teacher's courses
    assignment = get_assignment_by_id(assignment_id)
    if assignment:
        course = get_course_by_id(assignment.course_id)
        if not course or course.teacher_id != teacher_id:
            flash("You can only delete assignments for your own courses", "error")
            return redirect(url_for('teacher_courses'))
    
    deleted = delete_assignment(assignment_id)
    if deleted:
        flash(f"Assignment {assignment_id} deleted.", "success")
    else:
        flash("Assignment not found.", "error")
    return redirect(url_for('teacher_courses'))


########################
# SUBMISSION ROUTES
########################

@app.route('/create_submission', methods=['GET','POST'])
@role_required('student')
def create_submission_route():
    """
    Calls submission_service.create_submission.
    Now with improved file upload support.
    """
    student_id = session['user_id']
    
    # Get all assignments the student can submit for
    enrollments = Enrollment.query.filter_by(user_id=student_id).all()
    course_ids = [enrollment.course_id for enrollment in enrollments]
    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
    
    # Check if we have an assignment_id from query parameters
    assignment_id = request.args.get('assignment_id')
    selected_assignment = None
    if assignment_id:
        selected_assignment = get_assignment_by_id(assignment_id)
    
    if request.method == 'POST':
        assignment_id = request.form.get('assignment_id')
        is_late = bool(request.form.get('is_late', False))
        
        # Verify that the student is enrolled in the course for this assignment
        assignment = get_assignment_by_id(assignment_id)
        if assignment:
            enrollment = Enrollment.query.filter_by(user_id=student_id, course_id=assignment.course_id).first()
            if not enrollment:
                flash("You must be enrolled in the course to submit assignments", "error")
                return render_template('create_submission.html', assignments=assignments, selected_assignment=selected_assignment)
        
        # Handle file upload with improved path handling
        file_path = None
        if 'submission_file' in request.files:
            file = request.files['submission_file']
            if file and file.filename:
                # Create a unique filename to avoid collisions
                filename = secure_filename(f"{student_id}_{assignment_id}_{file.filename}")
                
                # Save the file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Store the path with forward slashes only
                file_path = filename
                
                # Log the file path for debugging
                app.logger.info(f"File saved at: {file_path}")
        
        try:
            new_sub = create_submission(assignment_id, student_id, file_path, is_late)
            flash(f"Submission created. ID={new_sub.id}", "success")
            return redirect(url_for('student_submissions'))
        except ValueError as e:
            flash(str(e), "error")
    
    return render_template('create_submission.html', assignments=assignments, selected_assignment=selected_assignment)


@app.route('/submission/update', methods=['GET','POST'])
@role_required('student')
def submission_update():
    """
    Calls update_submission from submission_service.
    Now with file upload support for updates.
    """
    student_id = session['user_id']
    
    # Get the submission for pre-filling if we have an ID
    submission = None
    if request.args.get('submission_id'):
        submission_id = request.args.get('submission_id')
        submission = get_submission_by_id(submission_id)
        
        # Verify that this submission belongs to the student
        if submission and submission.student_id != student_id:
            flash("You can only update your own submissions", "error")
            return redirect(url_for('student_submissions'))
    
    if request.method == 'POST':
        submission_id = request.form.get('submission_id')
        sub = get_submission_by_id(submission_id)
        
        # Verify that this submission belongs to the student
        if not sub or sub.student_id != student_id:
            flash("You can only update your own submissions", "error")
            return redirect(url_for('student_submissions'))
        
        # Check if the submission already has a grade (can't update graded submissions)
        if sub.grade:
            flash("Cannot update a submission that has already been graded", "error")
            return redirect(url_for('student_submissions'))
        
        # Handle file upload
        new_file_path = None
        if 'new_submission_file' in request.files:
            file = request.files['new_submission_file']
            if file and file.filename:
                # Create a unique filename to avoid collisions
                filename = secure_filename(f"{student_id}_{sub.assignment_id}_{file.filename}")
                # Store only the filename in the database
                new_file_path = filename
                # Save using the full path
                file_full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_full_path)

        else:
            # No new file, so use the text input if provided
            new_file_path = request.form.get('new_file_path') or None
        
        new_is_late = request.form.get('new_is_late')
        if new_is_late is not None:
            new_is_late = bool(new_is_late)
        
        updated = update_submission(submission_id, new_file_path, new_is_late)
        if updated:
            flash("Submission updated.", "success")
            return redirect(url_for('student_submissions'))
        else:
            flash("Submission not found.", "error")
    
    return render_template('submission_update.html', submission=submission)


@app.route('/submission/delete/<int:submission_id>')
@role_required('student')
def submission_delete(submission_id):
    """
    Calls delete_submission from submission_service.
    """
    student_id = session['user_id']
    
    # Verify that this submission belongs to the student
    submission = get_submission_by_id(submission_id)
    if submission:
        if submission.student_id != student_id:
            flash("You can only delete your own submissions", "error")
            return redirect(url_for('student_submissions'))
        
        # Check if the submission already has a grade (can't delete graded submissions)
        if submission.grade:
            flash("Cannot delete a submission that has already been graded", "error")
            return redirect(url_for('student_submissions'))
    
    deleted = delete_submission(submission_id)
    if deleted:
        flash(f"Submission {submission_id} deleted.", "success")
    else:
        flash("Submission not found.", "error")
    return redirect(url_for('student_submissions'))


########################
# GRADE ROUTES
########################

@app.route('/assign_grade', methods=['GET','POST'])
@role_required('teacher')
def assign_grade_route():
    """
    Calls grade_service.assign_grade.
    """
    teacher_id = session['user_id']
    
    # Get submission info if we have a submission_id
    submission = None
    if request.args.get('submission_id'):
        submission_id = request.args.get('submission_id')
        submission = get_submission_by_id(submission_id)
        
        # Verify that this submission is for an assignment in one of the teacher's courses
        if submission:
            assignment = get_assignment_by_id(submission.assignment_id)
            if assignment:
                course = get_course_by_id(assignment.course_id)
                if not course or course.teacher_id != teacher_id:
                    flash("You can only grade submissions for your own courses", "error")
                    return redirect(url_for('teacher_view_submissions'))
    
    if request.method == 'POST':
        submission_id = request.form.get('submission_id')
        score = request.form.get('score')
        feedback = request.form.get('feedback') or None
        
        # Verify that this submission is for an assignment in one of the teacher's courses
        sub = get_submission_by_id(submission_id)
        if sub:
            assignment = get_assignment_by_id(sub.assignment_id)
            if assignment:
                course = get_course_by_id(assignment.course_id)
                if not course or course.teacher_id != teacher_id:
                    flash("You can only grade submissions for your own courses", "error")
                    return redirect(url_for('teacher_view_submissions'))
        
        try:
            assigned = assign_grade(submission_id, float(score), feedback)
            flash(f"Grade assigned. Score={assigned.score}", "success")
            return redirect(url_for('teacher_view_submissions'))
        except ValueError as e:
            flash(str(e), "error")
    
    return render_template('assign_grade.html', submission=submission)


@app.route('/grade/update', methods=['GET','POST'])
@role_required('teacher')
def grade_update():
    """
    Calls grade_service.update_grade.
    """
    teacher_id = session['user_id']
    
    # Get grade info if we have a grade_id
    grade = None
    if request.args.get('grade_id'):
        grade_id = request.args.get('grade_id')
        grade = Grade.query.get(grade_id)
        
        # Verify that this grade is for a submission of an assignment in one of the teacher's courses
        if grade:
            submission = get_submission_by_id(grade.submission_id)
            if submission:
                assignment = get_assignment_by_id(submission.assignment_id)
                if assignment:
                    course = get_course_by_id(assignment.course_id)
                    if not course or course.teacher_id != teacher_id:
                        flash("You can only update grades for your own courses", "error")
                        return redirect(url_for('teacher_view_submissions'))
    
    if request.method == 'POST':
        grade_id = request.form.get('grade_id')
        new_score = request.form.get('new_score')
        new_feedback = request.form.get('new_feedback') or None
        
        # Verify that this grade is for a submission of an assignment in one of the teacher's courses
        grd = Grade.query.get(grade_id)
        if grd:
            submission = get_submission_by_id(grd.submission_id)
            if submission:
                assignment = get_assignment_by_id(submission.assignment_id)
                if assignment:
                    course = get_course_by_id(assignment.course_id)
                    if not course or course.teacher_id != teacher_id:
                        flash("You can only update grades for your own courses", "error")
                        return redirect(url_for('teacher_view_submissions'))
        
        try:
            updated = gd_update_grade(grade_id, float(new_score), new_feedback)
            if updated:
                flash(f"Grade updated to {updated.score}.", "success")
                return redirect(url_for('teacher_view_submissions'))
            else:
                flash("Grade not found.", "error")
        except ValueError as e:
            flash(str(e), "error")
    
    return render_template('grade_update.html', grade=grade)


@app.route('/grade/delete/<int:grade_id>')
@role_required('teacher')
def grade_delete(grade_id):
    """
    Calls grade_service.delete_grade.
    """
    teacher_id = session['user_id']
    
    # Verify that this grade is for a submission of an assignment in one of the teacher's courses
    grade = Grade.query.get(grade_id)
    if grade:
        submission = get_submission_by_id(grade.submission_id)
        if submission:
            assignment = get_assignment_by_id(submission.assignment_id)
            if assignment:
                course = get_course_by_id(assignment.course_id)
                if not course or course.teacher_id != teacher_id:
                    flash("You can only delete grades for your own courses", "error")
                    return redirect(url_for('teacher_view_submissions'))
    
    deleted = gd_delete_grade(grade_id)
    if deleted:
        flash(f"Grade {grade_id} deleted.", "success")
    else:
        flash("Grade not found.", "error")
    return redirect(url_for('teacher_view_submissions'))

########################
# FILE ROUTES
########################

@app.route('/uploads/<path:filename>')
def download_file(filename):
    """
    Route to download files from uploads folder.
    Teachers can access all files, students can only access their own submissions.
    """
    if 'user_id' not in session:
        flash("Please login to access this file", "error")
        return redirect(url_for('login'))
    
    # Extract just the filename without any path information
    simple_filename = os.path.basename(filename)
    
    # Check user role and permissions
    user_role = session.get('role')
    user_id = session.get('user_id')
    
    # Log debugging information
    app.logger.info(f"Attempting to access file: {simple_filename}")
    app.logger.info(f"Upload folder path: {app.config['UPLOAD_FOLDER']}")
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], simple_filename)
    app.logger.info(f"Full file path: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        flash("Requested file does not exist", "error")
        return "File not found", 404
    
    if user_role == 'teacher':
        # Teachers can access all files
        return send_from_directory(app.config['UPLOAD_FOLDER'], simple_filename)
    elif user_role == 'student':
        # Check if the file belongs to this student
        # Extract student ID from the filename (assuming format: student_id_assignment_id_filename)
        parts = simple_filename.split('_', 2)
        if len(parts) >= 2 and str(user_id) == parts[0]:
            return send_from_directory(app.config['UPLOAD_FOLDER'], simple_filename)
        
        flash("You don't have permission to access this file", "error")
        return redirect(url_for('student_dashboard'))
    else:
        flash("You don't have permission to access this file", "error")
        return redirect(url_for('index'))


########################
# NEW STUDENT FUNCTIONALITY ROUTES
########################

@app.route('/student/assignments')
@role_required('student')
def student_assignments():
    """
    Route to view assignments for the courses the student is enrolled in.
    """
    student_id = session['user_id']
    # Get courses student enrolled in
    enrollments = Enrollment.query.filter_by(user_id=student_id).all()
    course_ids = [en.course_id for en in enrollments]
    
    # Get assignments for these courses
    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
    
    # Enhance assignments with course info
    enhanced_assignments = []
    for assignment in assignments:
        course = Course.query.get(assignment.course_id)
        enhanced_assignments.append({
            'id': assignment.id,
            'title': assignment.title,
            'description': assignment.description,
            'due_date': assignment.due_date,
            'course_id': assignment.course_id,
            'course_name': course.course_name if course else 'Unknown'
        })
    
    return render_template('student_assignments.html', assignments=enhanced_assignments)


@app.route('/student/submissions')
@role_required('student')
def student_submissions():
    """
    Route to view all submissions made by the student.
    """
    student_id = session['user_id']
    submissions = get_submissions_by_student(student_id)
    
    # Enhance submissions with assignment info
    enhanced_submissions = []
    for submission in submissions:
        assignment = get_assignment_by_id(submission.assignment_id)
        course = None
        if assignment:
            course = get_course_by_id(assignment.course_id)
        
        # Get grade info if available
        grade = None
        if submission.grade:
            grade = submission.grade
        
        enhanced_submissions.append({
            'id': submission.id,
            'assignment_id': submission.assignment_id,
            'assignment_title': assignment.title if assignment else 'Unknown',
            'course_name': course.course_name if course else 'Unknown',
            'file_path': submission.file_path,
            'submitted_at': submission.submitted_at,
            'is_late': submission.is_late,
            'grade': grade
        })
    
    return render_template('student_submissions.html', submissions=enhanced_submissions)


@app.route('/student/grades')
@role_required('student')
def student_grades():
    """
    Route to view all grades for the student's submissions using direct SQL queries.
    """
    student_id = session['user_id']

    graded_submissions = db.session.query(Submission, Grade).\
        join(Grade, Submission.id == Grade.submission_id).\
        filter(Submission.student_id == student_id).all()
    
    enhanced_grades = []
    for submission, grade in graded_submissions:
        assignment = get_assignment_by_id(submission.assignment_id)
        course = None
        if assignment:
            course = get_course_by_id(assignment.course_id)
        
        enhanced_grades.append({
            'id': grade.id,
            'submission_id': submission.id,
            'assignment_title': assignment.title if assignment else 'Unknown',
            'course_name': course.course_name if course else 'Unknown',
            'score': grade.score,
            'feedback': grade.feedback
        })
    
    return render_template('student_grades.html', grades=enhanced_grades)


@app.route('/student/enroll', methods=['GET', 'POST'])
@role_required('student')
def student_enroll():
    """
    Route for student course enrollment.
    """
    student_id = session['user_id']
    
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        
        # Check if the course exists
        course = get_course_by_id(course_id)
        if not course:
            flash("Course not found", "error")
            return redirect(url_for('student_enroll'))
        
        # Check if already enrolled
        exists = Enrollment.query.filter_by(user_id=student_id, course_id=course_id).first()
        if exists:
            flash(f"You are already enrolled in {course.course_name}", "info")
        else:
            new_enrollment = Enrollment(user_id=student_id, course_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()
            flash(f"Successfully enrolled in {course.course_name}", "success")
        
        return redirect(url_for('student_enroll'))
    else:
        courses = get_all_courses()
        enrollments = Enrollment.query.filter_by(user_id=student_id).all()
        enrolled_course_ids = [en.course_id for en in enrollments]
        return render_template('student_enroll.html', courses=courses, enrolled_course_ids=enrolled_course_ids)


########################
# REDIRECTS FOR MISSING ROUTES
########################

@app.route('/student_view_assignments')
@role_required('student')
def student_view_assignments():
    """
    Redirect to the implemented student assignments view.
    """
    return redirect(url_for('student_assignments'))


@app.route('/student_submit_work')
@role_required('student')
def student_submit_work():
    """
    Redirect to the implemented student submissions view.
    """
    return redirect(url_for('student_submissions'))


@app.route('/student_view_grades')
@role_required('student')
def student_view_grades():
    """
    Redirect to the implemented student grades view.
    """
    return redirect(url_for('student_grades'))


@app.route('/student_enrollment')
@role_required('student')
def student_enrollment():
    """
    Redirect to the implemented student enrollment view.
    """
    return redirect(url_for('student_enroll'))


############################################################################
# 5) Run the Server
############################################################################

if __name__ == '__main__':
    app.run(debug=True)