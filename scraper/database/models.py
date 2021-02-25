"""
MongoDB models as defined by the Document and DynamicDocument classes

http://docs.mongoengine.org/apireference.html?highlight=connect#documents
"""
from mongoengine import (
    Document, DynamicDocument, EmbeddedDocument, DynamicEmbeddedDocument, 
    StringField, DateField, DateTimeField, BooleanField, URLField, ListField,
    EmbeddedDocumentField, DictField, IntField
)
import os
import datetime

class SpoilerMode(Document):
    mode = StringField()
    title = StringField(unique=True)
    ends_at = DateTimeField()
    thumb = URLField()
    
    meta = {
        "indexes": ["ends_at"]
    }

class PodcastInfo(Document):
    title = StringField(required=True)
    description = StringField()
    img_url = URLField()
    url = URLField()
    updated_at = DateTimeField()
    added_at = DateTimeField(default=datetime.datetime.now)

class PodcastEpisode(Document):
    title = StringField(required=True, unique=True)
    description = StringField()
    link = URLField(required=True, unique=True)
    published = DateField()
    duration = StringField()
    file = URLField()
    new = BooleanField(default=True)
    added = DateTimeField(default=datetime.datetime.now)

    meta = {
        "indexes": ["published"],
        "ordering": ["-published"]
    }
    
class ScheduleShow(Document):
    name = StringField(required=True, unique_with="date")
    time = DateTimeField(required=True)
    date = DateField(unique_with="name")
    new = BooleanField(default=True)
    city = StringField()
    venue = StringField()
    thumb = StringField()
    card = URLField()
    spoiler_hours = IntField(default=14)
    updated_at = DateTimeField()
    added_at = DateTimeField(default=datetime.datetime.now)
    live_show = BooleanField(default=False)

    meta = {
        "indexes": ["name", "date"],
        "ordering": ["date"]
    }

class NonNJPWShow(Document):
    name = StringField(required=True, unique_with="date")
    time = DateTimeField(required=True)
    date = DateField(unique_with="name")
    spoiler_hours = IntField(default=12)
    added_at = DateTimeField(default=datetime.datetime.now)

    meta = {
        "indexes": ["name", "date"],
        "ordering": ["date"]
    }

class ResultShow(Document):
    name = StringField(required=True, unique_with="date")
    time = DateTimeField(required=True)
    date = DateField(unique_with="name")
    city = StringField()
    venue = StringField()
    thumb = StringField()
    card = URLField()
    updated_at = DateTimeField()
    added_at = DateTimeField(default=datetime.datetime.now)

    meta = {
        "indexes": ["name"],
        "ordering": ["-date"]
    }

class Profile(DynamicDocument):
    name = StringField(required=True, unique=True)
    link = URLField(required=True)
    render = URLField()
    new = BooleanField(default=True)
    updated_at = DateTimeField()
    added_at = DateTimeField(default=datetime.datetime.now)
    removed = BooleanField(default=False)
    attributes = DictField()

    meta = {
        "indexes": ["name"]
    }

class KennyAlarm(DynamicDocument):
    last_mention_time = DateTimeField()
    last_mention_user = StringField()
    last_mention_message = StringField()
    last_mention_link = StringField()
    record_days = IntField()
    trigger_terms = ListField()