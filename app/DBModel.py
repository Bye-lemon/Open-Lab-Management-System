from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
import hashlib
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class Permission:
    ACCESS = 1
    RENT = 2
    MANAGE = 4
    ADMIN = 8


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('users', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if not self.permissions:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def initial_roles():
        roles = {
            'Student': [Permission.ACCESS, Permission.RENT],
            'Guard': [Permission.ACCESS, Permission.RENT, Permission.MANAGE],
            'Teacher': [Permission.ACCESS, Permission.RENT, Permission.MANAGE, Permission.ADMIN]
        }
        for item in roles:
            role = Role.query.filter_by(name=item).first()
            if not role:
                role = Role(name=item)
            role.permissions = 0
            for permission in roles[item]:
                role.permissions += permission
            db.session.add(role)
        db.session.commit()

    def has_permisssion(self, permission):
        return self.permissions & permission == permission


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    major = db.Column(db.String(64))
    role = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    is_confirmed = db.Column(db.Boolean, default=False)
    is_allowed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    coin = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.role:
            if self.email == current_app.config['ADMINISTRATOR_EMAIL']:
                self.role = Role.query.filter_by(name='Teacher').first()
            else:
                self.role = Role.query.filter_by(name='Student').first()
        if self.email and not self.avatar_hash:
            self.avatar_hash = hashlib.md5(self.email.lower().encoding('utf-8')).hexdigest()

    def __repr__(self):
        return '<User %s>' % self.name

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.is_confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.lower().encodind('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def allow(self):
        self.is_allowed = True

    def can(self, permission):
        return self.role.has_permisssion(permission)

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Course(db.Model):
    pass


class Tool(db.Model):
    pass


class Power(db.Model):
    pass


class Good(db.Model):
    pass
# 积分兑换商品