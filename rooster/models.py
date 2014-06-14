from django.db import models
import untis

# Create your models here.
class Source(models.Model):
    title = models.CharField(max_length=128)
    type = models.CharField(max_length=64, choices=(
        ('room', 'Classroom'),
        ('teacher', 'Teacher'),
        ('group', 'Group'),
        ('student', 'Student')))

    def get_code(self):
        return self.title.replace(' ', '_').replace('.', '')

    def as_json(self):
        return {
                'title': self.title,
                'type': self.type,
                'url': self.get_json_url()}

    def get_json_url(self):
        return '/%s/%s.json' % (self.type, self.get_code())

    """
    Return all events that can be retrieved for this source
    """
    def get_events(self):
        # TODO: Some sort of caching?
        return untis.get_events(self)


    @classmethod
    def get_sources(cls):
        # TODO: Some sort of caching?
        return untis.get_sources()

    @classmethod
    def get_source(cls, type, code):
        sources = Source.get_sources()
        for source in sources:
            if source.type == type and source.get_code() == code:
                return source

        return None

class Event(models.Model):
    source = models.ForeignKey(Source)

    title = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def as_json(self):
        return {'title': self.title, 'location': self.location, 'start': str(self.start), 'end': str(self.end)}
