# app/services/grade_service.py

from app.models import db, Grade, Submission, User

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
