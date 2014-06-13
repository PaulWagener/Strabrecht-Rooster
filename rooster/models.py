from django.db import models

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
                'json_url': self.get_json_url()}

    def get_json_url(self):
        return '/%s/%s.json' % (self.type, self.get_code())