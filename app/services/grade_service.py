# app/services/grade_service.py

from app.models import db, Grade, Submission, User, Assignment, Course
from sqlalchemy import func
from collections import defaultdict

def assign_grade(submission_id, score, feedback=None):
    """
    Assign a grade to a particular submission.

    :param submission_id: The ID of the submission being graded
    :param score: Numerical score
    :param feedback: Optional text feedback
    :return: The newly created or updated Grade object
    """
    # Validate the submission
    submission = Submission.query.get(submission_id)
    if not submission:
        raise ValueError("Submission does not exist.")

    # If there is already a grade, update it; otherwise create a new one
    existing_grade = Grade.query.filter_by(submission_id=submission_id).first()
    if existing_grade:
        existing_grade.score = score
        existing_grade.feedback = feedback
        db.session.commit()
        return existing_grade
    else:
        new_grade = Grade(
            submission_id=submission_id,
            score=score,
            feedback=feedback
        )
        db.session.add(new_grade)
        db.session.commit()
        return new_grade

def get_grade_by_submission(submission_id):
    """
    Retrieve the grade for a specific submission.

    :param submission_id: Submission ID
    :return: Grade object or None if no grade exists
    """
    return Grade.query.filter_by(submission_id=submission_id).first()

def update_grade(grade_id, new_score=None, new_feedback=None):
    """
    Update an existing grade.

    :param grade_id: The ID of the grade to update
    :param new_score: Optional new score
    :param new_feedback: Optional new feedback
    :return: The updated Grade object or None if not found
    """
    grade = Grade.query.get(grade_id)
    if not grade:
        return None

    if new_score is not None:
        grade.score = new_score
    if new_feedback is not None:
        grade.feedback = new_feedback

    db.session.commit()
    return grade

def delete_grade(grade_id):
    """
    Delete a Grade entry.

    :param grade_id: The ID of the grade to delete
    :return: True if deletion succeeded, False otherwise
    """
    grade = Grade.query.get(grade_id)
    if grade:
        db.session.delete(grade)
        db.session.commit()
        return True
    return False

def get_assignment_stats(assignment_id):
    """
    Get statistics for an assignment.
    Returns average, maximum, minimum scores and grade distribution.

    :param assignment_id: Assignment ID
    :return: Dictionary with statistics information
    """
    # Get the assignment
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        raise ValueError(f"Assignment with ID {assignment_id} not found.")
    
    # Get all submissions for this assignment
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    submission_ids = [sub.id for sub in submissions]
    
    # Get all grades for these submissions
    grades = Grade.query.filter(Grade.submission_id.in_(submission_ids)).all() if submission_ids else []
    
    # Calculate statistics
    scores = [grade.score for grade in grades] if grades else []
    
    stats = {
        'assignment': assignment,
        'total_submissions': len(submissions),
        'graded_submissions': len(grades),
        'average_score': sum(scores) / len(scores) if scores else 0,
        'max_score': max(scores) if scores else 0,
        'min_score': min(scores) if scores else 0,
        'scores': scores,  # For distribution chart
        'submissions': submissions  # All submissions with their information
    }
    
    return stats

def get_course_assignments_stats(course_id):
    """
    Get statistics for all assignments in a course.

    :param course_id: Course ID
    :return: List of dictionaries with assignment statistics
    """
    # Get the course
    course = Course.query.get(course_id)
    if not course:
        raise ValueError(f"Course with ID {course_id} not found.")
    
    # Get all assignments for this course
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    # Get statistics for each assignment
    assignment_stats = []
    for assignment in assignments:
        try:
            stats = get_assignment_stats(assignment.id)
            assignment_stats.append({
                'assignment': assignment,
                'stats': stats
            })
        except ValueError:
            # If there's an error, add basic assignment info without stats
            assignment_stats.append({
                'assignment': assignment,
                'stats': {
                    'total_submissions': 0,
                    'graded_submissions': 0,
                    'average_score': 0,
                    'max_score': 0,
                    'min_score': 0,
                    'scores': [],
                    'submissions': []
                }
            })
    
    return assignment_stats

def get_student_grades_by_assignment(assignment_id):
    """
    Get all student grades for a specific assignment, including student information.

    :param assignment_id: Assignment ID
    :return: List of dictionaries with student grade information
    """
    # Get all submissions for this assignment
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    
    student_grades = []
    for submission in submissions:
        student = User.query.get(submission.student_id)
        grade = get_grade_by_submission(submission.id)
        
        student_grades.append({
            'student_id': student.id,
            'student_name': student.username,
            'submission_id': submission.id,
            'submitted_at': submission.submitted_at,
            'is_late': submission.is_late,
            'file_path': submission.file_path,
            'score': grade.score if grade else None,
            'feedback': grade.feedback if grade else None,
            'grade_id': grade.id if grade else None
        })
    
    return student_grades

def get_score_distribution(scores, bins=10):
    """
    Calculate score distribution across specified number of bins.

    :param scores: List of scores
    :param bins: Number of bins to divide scores into
    :return: Dictionary with bin ranges and counts
    """
    if not scores:
        return {}
    
    # Create bins from 0 to 100
    bin_size = 100 / bins
    bin_ranges = [(i * bin_size, (i + 1) * bin_size) for i in range(bins)]
    
    # Count scores in each bin
    distribution = defaultdict(int)
    for score in scores:
        for i, (lower, upper) in enumerate(bin_ranges):
            if i == bins - 1:  # Last bin includes the upper boundary
                if lower <= score <= upper:
                    distribution[f"{lower:.0f}-{upper:.0f}"] += 1
                    break
            else:
                if lower <= score < upper:
                    distribution[f"{lower:.0f}-{upper:.0f}"] += 1
                    break
    
    return dict(distribution)