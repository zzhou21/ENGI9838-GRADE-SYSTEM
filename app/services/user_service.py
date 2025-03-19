# app/services/user_service.py

from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

def create_user(username, password, email=None, role='student'):
    """
    build new User
    
    :param username:  user_name, must be unique
    :param password:  password
    :param email:     email, can be set as null
    :param role:      role will be default set as student
    :return:          return User
    """
    # check if the user name is unique
    existing = User.query.filter_by(username=username).first()
    if existing:
        raise ValueError(f"Username '{username}' already taken.")

    hashed_pwd = generate_password_hash(password)
    new_user = User(
        username=username,
        password=hashed_pwd,
        email=email,
        role=role
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user


def authenticate_user(username, password):

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None


def get_user_by_id(user_id):

    return User.query.get(user_id)


def get_user_by_username(username):
    
    return User.query.filter_by(username=username).first()


def update_user(user_id, new_email=None, new_role=None, new_password=None):
    """
    update the user with specific id
    """
    user = User.query.get(user_id)
    if not user:
        return None
    
    if new_email is not None:
        user.email = new_email
    
    if new_role is not None:
        user.role = new_role

    if new_password is not None:
        user.password = generate_password_hash(new_password)
    
    db.session.commit()
    return user


def delete_user(user_id):
    """
    delete the user with specific id
    """
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
