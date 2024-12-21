from db import db

class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Зв'язок з користувачем (Item належить користувачу)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', backref=db.backref('items', lazy=True))

    def __init__(self, name, price, user_id):
        self.name = name
        self.price = price
        self.user_id = user_id

    def json(self):
        return {'id': self.id, 'name': self.name, 'price': self.price, 'user_id': self.user_id}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
