from django.db import models
import django.utils.timezone
import untis, urllib2, datetime, re

# Create your models here.
class Source(models.Model):
    title = models.CharField(max_length=128)
    type = models.CharField(max_length=64, choices=(
        ('room', 'Classroom'),
        ('teacher', 'Teacher'),
        ('group', 'Group'),
        ('student', 'Student')))

    def get_code(self):
        return re.sub('[^a-zA-Z0-9]+', '_', self.title).strip('_')

    def as_json(self):
        return {
                'title': self.title,
                'type': self.type,
                'url': self.get_json_url(),
                'ics': self.get_ics_url()}

    def get_url_base(self):
        return '/%s/%s' % (self.type, self.get_code())

    def get_json_url(self):
        return self.get_url_base() + '.json'

    def get_ics_url(self):
        return self.get_url_base() + '.ics'

    """
    Return all events that can be retrieved for this source
    """
    def get_events(self):
        return untis.get_events(self)


    @classmethod
    def get_sources(cls):
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
    repeated = models.BooleanField()
    location = models.CharField(max_length=128)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def as_json(self):
        return {'title': self.title, 'location': self.location, 'start': str(self.start), 'end': str(self.end)}

class Cache(models.Model):
    url = models.CharField(max_length=512, primary_key=True)
    html = models.TextField()
    downloaded = models.DateTimeField()

    @classmethod
    def read_url(cls, url):
        # Delete stale caches
        Cache.objects.filter(downloaded__lte=django.utils.timezone.now() - datetime.timedelta(hours=1)).delete()

        #
        try:
            return Cache.objects.get(url=url).html
        except Cache.DoesNotExist:
            print 'cache miss'
            html = urllib2.urlopen(url).read().decode('iso-8859-1')
            cache = Cache(url=url,html=html,downloaded=django.utils.timezone.now())
            cache.save()
            return html