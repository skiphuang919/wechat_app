from .. import db
from flask import current_app
from ..model import User
from tools import get_db_unique_id
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def add_user(open_id=None, name=None, email=None, gender=None, city=None, slogan=None):
    user = User(user_id=get_db_unique_id(),
                open_id=open_id,
                name=name,
                email=email,
                gender=gender,
                city=city,
                slogan=slogan)
    db.session.add(user)
    db.session.commit()
    return user


def get_user(user_id=None, open_id=None, name=None, email=None):
    if user_id is not None:
        return User.query.filter_by(user_id=user_id).first()
    elif open_id is not None:
        return User.query.filter_by(open_id=open_id).first()
    elif name is not None:
        return User.query.filter_by(name=name).first()
    elif email is not None:
        return User.query.filter_by(email=email).first()
    else:
        return None


def is_email_exist(email):
    user = get_user(email=email)
    return True if user else False


def is_name_exist(name):
    user = get_user(name=name)
    return True if user else False


def generate_confirm_token(user_id, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'confirm': user_id})


def confirm(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return False

    if data.get('confirm') is None:
        return False

    user_obj = get_user(user_id=data.get('confirm'))
    if user_obj is None:
        return False

    user_obj.confirmed = True
    db.session.add(user_obj)
    db.session.commit()
    return True
