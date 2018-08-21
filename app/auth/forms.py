from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from ..DBModel import User


class RegistrationForm(FlaskForm):
    id = StringField('学号', validators=[DataRequired(), Length(7, 9)])
    name = StringField('姓名', validators=[DataRequired()])
    major = StringField('专业', validators=[DataRequired()])
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(),
                                               EqualTo('password_repeat', '两次输入的密码不一致，请核对后重新输入！')])
    password_repeat = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.email).first():
            raise ValidationError('该邮箱已经被注册！')

    def validate_id(self, field):
        if User.query.filter_by(email=field.id).first():
            raise ValidationError('该学号已经被注册！')


class LoginForm(FlaskForm):
    id = StringField('学号', validators=[DataRequired(), Length(7, 9)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

