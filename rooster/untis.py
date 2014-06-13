import urllib2, ast, re, json
from models import Source

# Download all available calendar sources from Untis
def get_sources():
    html = urllib2.urlopen('http://rooster.strabrecht.nl/weken/Dagelijks/frames/navbar.htm').read().decode('iso-8859-1')

    sources = []

    for teacher in ast.literal_eval(re.search('var teachers = (\[.*?\])', html).group(1)):
        sources.append(Source(title=teacher, type='teacher'))

    for group in ast.literal_eval(re.search('var classes = (\[.*?\])', html).group(1)):
        sources.append(Source(title=group, type='group'))

    for student in ast.literal_eval(re.search('var students = (\[.*?\])', html).group(1)):
        sources.append(Source(title=student, type='student'))

    for room in ast.literal_eval(re.search('var rooms = (\[.*?\])', html).group(1)):
        sources.append(Source(title=student, type='room'))
    return sources

def get_sources_json():
    return json.dumps([s.as_json() for s in get_sources()])