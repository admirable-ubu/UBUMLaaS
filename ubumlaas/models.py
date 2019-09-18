import variables as v
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from flask_login import UserMixin

@v.login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def get_experiments(idu):
    listexp = Experiment.query.filter(Experiment.idu== idu).all()
    for i in listexp:
        i.starttime = datetime.fromtimestamp(i.starttime).strftime("%d/%m/%Y - %H:%M:%S")
        if i.endtime is not None:
            i.endtime = datetime.fromtimestamp(i.endtime).strftime("%d/%m/%Y - %H:%M:%S")
    return listexp


class User(v.db.Model, UserMixin):
    
    __tablename__ = 'users'

    id = v.db.Column(v.db.Integer, primary_key=True)
    email = v.db.Column(v.db.String(64), unique=True, index=True)
    username = v.db.Column(v.db.String(64), unique=True, index=True)
    password_hash = v.db.Column(v.db.String(128))

    def __init__(self, email, username, password):
        """User constructor
        
        Arguments:
            email {string} -- User's email
            username {string} -- User name identifer
            password {string} -- User's password
        """
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Compare input password with current password
        
        Arguments:
            password {string} -- Input password
        
        Returns:
            boolean -- True if both password match, instead False 
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Email: {self.email} Username: {self.username}"

    def __str__(self):
        return self.__repr__() + f" Email: {self.email}"

    def to_dict(self):
        return {"id": self.id, "email": self.email, "username": self.username, "password": self.password_hash}


class Experiment(v.db.Model):

    __tablename__ = 'experiments'

    id = v.db.Column(v.db.Integer, primary_key=True)
    idu = v.db.Column(
        v.db.Integer,
        v.db.ForeignKey('users.id'),
    )
    alg_name = v.db.Column(v.db.String(64))
    alg_config = v.db.Column(v.db.Text)
    data = v.db.Column(v.db.String(128))
    result = v.db.Column(v.db.Text, nullable=True)
    starttime = v.db.Column(v.db.Integer)
    endtime = v.db.Column(v.db.Integer, nullable=True)

    def __init__(self, idu, alg_name, alg_config, data, result, starttime, endtime):
        """Experiment constructor
        
        Arguments:
            idu {integer} -- User who lauch experiment
            alg_name {string} -- Experiment's algorithm name
            alg_config {string} -- Experiment's algorithm configuration
            data {string} -- Experiment data
            result {string} -- Experiment result
            starttime {integer} -- Experiment start timestamp
            endtime {integer} -- Experiment end timestamp
        """
        self.idu = idu
        self.alg_name = alg_name
        self.alg_config = alg_config
        self.data = data
        self.result = result
        self.starttime = starttime
        self.endtime = endtime

    def to_dict(self):
        return {"id": self.id, "idu": self.idu, "alg_name": self.alg_name,
            "alg_config": self.alg_config, "data": self.data,
            "result": self.result, "starttime": self.starttime, 
            "endtime": self.endtime}

        
