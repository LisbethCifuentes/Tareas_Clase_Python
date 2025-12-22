from mongoengine import Document, StringField, IntField, BooleanField

class Pet(Document):
    name = StringField(required=True)
    species = StringField(required=True)
    age = IntField(required=True)
    owner = StringField(required=True)
    vaccinated = BooleanField(default=False)
