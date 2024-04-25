# app/models.py

from database import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def json(self):
        return {'id': self.id,'username': self.username, 'email': self.email}


class Indicator(db.Model):
    __tablename__ = 'indicators'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(80), nullable=True)
    #frequency is either monthly, quarterly, yearly or weekly 
    frequency = db.Column(db.String(80), nullable=False)
    indicator_type = db.Column(db.String(80), nullable=False )

    def json(self):
        return {'id': self.id,'name': self.name, 'description': self.description}
    

class IndicatorsData(db.Model):
    __tablename__ = 'indicators_data'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicators.id'))
    value = db.Column(db.Float, nullable=False)
    score= db.Column(db.Integer, nullable=False)

    def json(self):
        return {'id': self.id,'date': self.date, 'value': self.value, 'score': self.score}
    
class COTIndicator(db.Model):
    __tablename__ = 'cot_indicators'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    asset = db.Column(db.String(80), nullable=False)
    long = db.Column(db.Integer, nullable=False)
    short = db.Column(db.Integer, nullable=False)
    open_interest = db.Column(db.Integer, nullable=False)
    net = db.Column(db.Integer, nullable=False)
    change_in_net = db.Column(db.Integer, nullable=True)
    long_change_percentage = db.Column(db.Float, nullable=True)
    short_change_percentage = db.Column(db.Float, nullable=True)
    score= db.Column(db.Integer, nullable=True)

    def json(self):
        return {'id': self.id,'date': self.date, 'asset': self.asset,
        'long': self.long, 'short': self.short, 'open_interest': self.open_interest, 'net': self.net, 'change_in_net': self.change_in_net, 'long_change_percentage': self.long_change_percentage, 'short_change_percentage': self.short_change_percentage, 'score': self.score,'score': self.score}


class AssetScore(db.Model):
    __tablename__ = 'asset_scores'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    asset = db.Column(db.String(80), nullable=False)
    score= db.Column(db.Integer, nullable=False)

    def json(self):
        return {'id': self.id,'date': self.date, 'asset': self.asset, 'score': self.score}