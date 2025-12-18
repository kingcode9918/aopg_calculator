# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class Item(db.Model):
#     __tablename__ = "items"

#     id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(50), nullable=False)  # 'buff' or 'accessory'
#     name = db.Column(db.String(100), nullable=False)
#     type = db.Column(db.String(50), nullable=False)      # buff type or accessory slot

#     # Stats
#     strength = db.Column(db.Float, default=0)
#     stamina = db.Column(db.Float, default=0)
#     defense = db.Column(db.Float, default=0)
#     sword = db.Column(db.Float, default=0)
#     gun = db.Column(db.Float, default=0)
#     haki = db.Column(db.Float, default=0)
#     fruit = db.Column(db.Float, default=0)

#     def values_dict(self):
#         return {
#             "strength": self.strength,
#             "stamina": self.stamina,
#             "defense": self.defense,
#             "sword": self.sword,
#             "gun": self.gun,
#             "haki": self.haki,
#             "fruit": self.fruit
#         }

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # "buff" or "accessory"
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    # Buff stats
    strength = db.Column(db.Float, default=1.0)
    sword = db.Column(db.Float, default=1.0)
    gun = db.Column(db.Float, default=1.0)
    fruit = db.Column(db.Float, default=1.0)

    # Accessory stats
    stamina = db.Column(db.Float, default=0)
    defense = db.Column(db.Float, default=0)
    haki = db.Column(db.Float, default=0)

    def values_dict(self):
        return {
            "strength": self.strength,
            "sword": self.sword,
            "gun": self.gun,
            "fruit": self.fruit,
            "stamina": self.stamina,
            "defense": self.defense,
            "haki": self.haki
        }

