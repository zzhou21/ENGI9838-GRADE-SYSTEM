# app/services/course_service.py

from app.models import db, Course, User

def create_course(course_name, teacher_id, course_code=None, description=None):

    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != 'teacher':
        raise ValueError("Invalid teacher_id or user is not a teacher.")

    if course_code:
        existing_code = Course.query.filter_by(course_code=course_code).first()
        if existing_code:
            raise ValueError(f"Course code '{course_code}' is already used.")

    new_course = Course(
        course_name=course_name,
        course_code=course_code,
        description=description,
        teacher_id=teacher_id
    )
    db.session.add(new_course)
    db.session.commit()
    return new_course

def get_course_by_id(course_id):
    return Course.query.get(course_id)

def get_all_courses():
    return Course.query.all()

def update_course(course_id, new_name=None, new_teacher_id=None, 
                  new_code=None, new_description=None):
    
    course = Course.query.get(course_id)
    if not course:
        return None
    
    if new_name is not None:
        course.course_name = new_name
    
    if new_teacher_id is not None:
        teacher = User.query.get(new_teacher_id)
        if not teacher or teacher.role != 'teacher':
            raise ValueError("Invalid teacher_id or user is not a teacher.")
        course.teacher_id = new_teacher_id
    
    if new_code is not None:
        course.course_code = new_code

    if new_description is not None:
        course.description = new_description

    db.session.commit()
    return course

def delete_course(course_id):
    course = Course.query.get(course_id)
    if course:
        db.session.delete(course)
        db.session.commit()
        return True
    return False
