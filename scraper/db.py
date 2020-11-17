from mongoengine import (
    Document, StringField, DateField, BooleanField, URLField
)
import os

class PodcastInfo(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    img_url = URLField()
    url = URLField()

class PodcastEpisode(Document):
    title = StringField(required=True)
    description = StringField()
    link = URLField(required=True, unique=True)
    published = DateField()
    duration = StringField()
    file_url = URLField()
    new = BooleanField(default=True)
    
class Show(Document):
    name = StringField(required=True, unique_with="date")
    date = StringField(required=True, unique_with="name")
    city = StringField()
    venue = StringField()
    thumb = StringField() 

class Profile(Document):
    name = StringField(required=True, unique=True)
    link = URLField(required=True)
    render = URLField()
    unit = StringField()
    bio = StringField()
    height = StringField()
    weight = StringField()
    birthday = StringField()
    birthplace = StringField()
    bloodtype = StringField()
    debut = StringField()
    finisher = StringField()
    theme = StringField()
    blog = URLField()
    twitter = URLField()
