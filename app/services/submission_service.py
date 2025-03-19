# app/services/submission_service.py

from datetime import datetime
from app.models import db, Submission, Assignment, User

def create_submission(assignment_id, student_id, file_path=None, is_late=False):
    """
    Create a new submission record.

    :param assignment_id: The ID of the assignment being submitted
    :param student_id: The ID of the student making this submission
    :param file_path: Optional path or filename of the submitted file
    :param is_late: Boolean indicating if the submission is late
    :return: The newly created Submission object
    """
    # Verify that the assignment exists
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        raise ValueError("Assignment does not exist.")

    # Verify that the user is actually a 'student' if needed
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        raise ValueError("User does not exist or is not a student.")

    new_submission = Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        file_path=file_path,
        submitted_at=datetime.utcnow(),
        is_late=is_late
    )
    db.session.add(new_submission)
    db.session.commit()
    return new_submission

def get_submission_by_id(submission_id):
    """
    Retrieve a Submission by its ID.

    :param submission_id: Submission primary key
    :return: Submission object or None
    """
    return Submission.query.get(submission_id)

def get_submissions_by_assignment(assignment_id):
    """
    Retrieve all submissions for a specific assignment.

    :param assignment_id: Assignment ID
    :return: List of Submission objects
    """
    return Submission.query.filter_by(assignment_id=assignment_id).all()

def get_submissions_by_student(student_id):
    """
    Retrieve all submissions made by a specific student.

    :param student_id: The student's user ID
    :return: List of Submission objects
    """
    return Submission.query.filter_by(student_id=student_id).all()

def update_submission(submission_id, new_file_path=None, new_is_late=None):

    submission = Submission.query.get(submission_id)
    if not submission:
        return None

    if new_file_path is not None:
        submission.file_path = new_file_path
    if new_is_late is not None:
        submission.is_late = new_is_late

    db.session.commit()
    return submission

def delete_submission(submission_id):
    """
    Delete a submission record.

    :param submission_id: The submission's ID
    :return: True if deletion succeeded, False if not found
    """
    submission = Submission.query.get(submission_id)
    if submission:
        db.session.delete(submission)
        db.session.commit()
        return True
    return False
