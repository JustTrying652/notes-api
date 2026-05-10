from app import db
import bcrypt

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    notes = db.relationship("Note", backref="owner", lazy=True)

    def set_password(self, plain_password):
        self.password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, plain_password):
        return bcrypt.checkpw(plain_password.encode("utf-8"), self.password.encode("utf-8"))