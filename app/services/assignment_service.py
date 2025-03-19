# app/services/assignment_service.py

from app.models import db, Assignment, Course, User

def create_assignment(course_id, title, description=None, due_date=None):
    """
    Create a new Assignment for a given course.

    :param course_id: The ID of the course to which this assignment belongs
    :param title: The assignment's title (required)
    :param description: Optional description of the assignment
    :param due_date: Optional due date (datetime object)
    :return: The created Assignment object
    """
    # Verify that the course exists
    course = Course.query.get(course_id)
    if not course:
        raise ValueError(f"Course with id={course_id} not found.")

    # Create and save the assignment
    new_assignment = Assignment(
        course_id=course_id,
        title=title,
        description=description,
        due_date=due_date
    )
    db.session.add(new_assignment)
    db.session.commit()
    return new_assignment

def get_assignment_by_id(assignment_id):
    """
    Retrieve an Assignment by its ID.

    :param assignment_id: Assignment primary key
    :return: Assignment object or None if not found
    """
    return Assignment.query.get(assignment_id)

def get_assignments_by_course(course_id):
    """
    Retrieve all assignments under a specific course.

    :param course_id: Course ID
    :return: List of Assignment objects
    """
    return Assignment.query.filter_by(course_id=course_id).all()

def update_assignment(assignment_id, new_title=None, new_description=None, new_due_date=None):

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return None

    if new_title is not None:
        assignment.title = new_title
    if new_description is not None:
        assignment.description = new_description
    if new_due_date is not None:
        assignment.due_date = new_due_date

    db.session.commit()
    return assignment

def delete_assignment(assignment_id):
    """
    Delete a specific assignment.

    :param assignment_id: The ID of the assignment to delete
    :return: True if deleted, False if not found
    """
    assignment = Assignment.query.get(assignment_id)
    if assignment:
        db.session.delete(assignment)
        db.session.commit()
        return True
    return False
