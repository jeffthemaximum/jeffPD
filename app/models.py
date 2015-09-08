from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin
from . import db, login_manager
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'users', 'polymorphic_on': type}

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True


def convert_users_to_teachers():
    users = User.query.all()
    for user in users:
        if user.type != 'coach' and user.type != 'teacher':
            teacher = Teacher(
                email=user.email,
                username=user.username,
                password_hash=user.password_hash,
                first_name=user.first_name,
                last_name=user.last_name)
            db.session.delete(user)
            db.session.commit()
            db.session.add(teacher)
            db.session.commit()


class Teacher(User):
    __tablename__ = 'teachers'
    __mapper_args__ = {'polymorphic_identity': 'teachers'}
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # teachers have many logs
    logs = db.relationship(
        'Log',
        secondary='log_teacher_link'
    )
    # teachers can have many coaches
    coaches = db.relationship(
        'Coach',
        secondary='coach_teacher_link'
    )


class Coach(User):
    __tablename__ = 'coaches'
    __mapper_args__ = {'polymorphic_identity': 'coach'}
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # coaches have many logs
    logs = db.relationship('Log', backref='coach', lazy='dynamic')
    # coaches have many teachers
    teachers = db.relationship(
        Teacher,
        secondary='coach_teacher_link'
    )


class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    next = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # logs have many teachers
    teachers = db.relationship(
        Teacher,
        secondary='log_teacher_link'
    )
    # logs have one coach
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'))
    # tags for easy searching
    hardware = db.Column(db.Boolean, default=False)
    coteach = db.Column(db.Boolean, default=False)
    coplan = db.Column(db.Boolean, default=False)
    jeffpd_publication = db.Column(db.Boolean, default=False)
    google_maintenance = db.Column(db.Boolean, default=False)
    teacher_chromebook_help = db.Column(db.Boolean, default=False)
    contact_nit = db.Column(db.Boolean, default=False)
    general_teacher_tech_help = db.Column(db.Boolean, default=False)
    google_resources = db.Column(db.Boolean, default=False)
    email_help = db.Column(db.Boolean, default=False)
    unbelieavble = db.Column(db.Boolean, default=False)


class LogTeacherLink(db.Model):
    __tablename__ = 'log_teacher_link'
    log_id = db.Column(db.Integer, db.ForeignKey('logs.id'), primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'),
        primary_key=True)
    log = db.relationship(Log, backref=db.backref("teacher_assoc"))
    teacher = db.relationship(Teacher, backref=db.backref("log_assoc"))


class CoachTeacherLink(db.Model):
    __tablename__ = 'coach_teacher_link'
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'),
        primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey(
        'coaches.id'),
        primary_key=True)
    teacher = db.relationship(Teacher, backref=db.backref("coach_assoc"))
    coach = db.relationship(Coach, backref=db.backref("teacher_assoc"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
