"""
Module to abstract away all the idiosyncracies of the Untis timetabling website
"""
import ast, re, json, datetime, lxml.html, pytz
import rooster.models

timetable = [
    (datetime.time( 8, 30, 0), datetime.time( 8, 55, 0)), # 1
    (datetime.time( 8, 55, 0), datetime.time( 9, 20, 0)), # 2
    (datetime.time( 9, 20, 0), datetime.time( 9, 45, 0)), # 3
    (datetime.time( 9, 45, 0), datetime.time(10, 10, 0)), # 4
    (datetime.time(10, 10, 0), datetime.time(10, 35, 0)), # 5
    (datetime.time(10, 35, 0), datetime.time(11, 00, 0)), # 6
    (datetime.time(11, 00, 0), datetime.time(11, 25, 0)), # 7
    (datetime.time(11, 25, 0), datetime.time(11, 50, 0)), # 8
    (datetime.time(11, 50, 0), datetime.time(12, 15, 0)), # 9
    (datetime.time(12, 15, 0), datetime.time(12, 40, 0)), # 10
    (datetime.time(12, 40, 0), datetime.time(13,  5, 0)), # 11
    (datetime.time(13,  5, 0), datetime.time(13, 30, 0)), # 12
    (datetime.time(13, 30, 0), datetime.time(13, 55, 0)), # 13
    (datetime.time(13, 55, 0), datetime.time(14, 20, 0)), # 14
    (datetime.time(14, 20, 0), datetime.time(14, 45, 0)), # 15
    (datetime.time(14, 45, 0), datetime.time(15, 10, 0)), # 16
    (datetime.time(15, 10, 0), datetime.time(15, 35, 0)), # 17
    (datetime.time(15, 35, 0), datetime.time(16, 00, 0)), # 18
]

# Download all available calendar sources from Untis
def get_sources(untis_week='Dagelijks'):
    html = rooster.models.Cache.read_url('http://rooster.strabrecht.nl/weken/%s/frames/navbar.htm' % untis_week)

    sources = []

    for teacher in ast.literal_eval(re.search('var teachers = (\[.*?\])', html).group(1)):
        sources.append(rooster.models.Source(title=teacher, type='teacher'))

    for group in ast.literal_eval(re.search('var classes = (\[.*?\])', html).group(1)):
        sources.append(rooster.models.Source(title=group, type='group'))

    for student in ast.literal_eval(re.search('var students = (\[.*?\])', html).group(1)):
        sources.append(rooster.models.Source(title=student, type='student'))

    for room in ast.literal_eval(re.search('var rooms = (\[.*?\])', html).group(1)):
        sources.append(rooster.models.Source(title=room, type='room'))

    return sources

def get_sources_json():
    return json.dumps([s.as_json() for s in get_sources()])


def get_object_index(source, untis_week):
    """
    Get the index for a source
    This is needed for the calendar URL's
    """
    index = 0
    for s in get_sources(untis_week):
        if s.type == source.type:
            index += 1

        if s.title == source.title:
            return index

    return -1

def get_start_date_for_untis_week(untis_week):
    """
    Get the monday date for an 'Untis week' (Dagelijks, dezeweek, volgendrooster)
    """
    html = rooster.models.Cache.read_url('http://rooster.strabrecht.nl/weken/%s/frames/navbar.htm' % untis_week)
    date_string = re.search('<option value="[0-9]+">([0-9-]+)', html).group(1)
    return datetime.datetime.strptime(date_string, '%d-%m-%Y').date()

def get_events(source):
    """
    Get a list of events for a particular source
    """
    # Get untis index number for the object
    start_date = get_start_date_for_untis_week('Dagelijks')

    events_current = get_events_for_untis_week(source, start_date, 'Dagelijks')
    events_regular = get_events_for_untis_week(source, start_date + datetime.timedelta(days=7), 'dezeweek', repeated=True)

    return events_current +events_regular



def get_events_for_untis_week(source, monday_date, untis_week, repeated=False):
    # Generate the URL
    type_letter = {
        'teacher': 't',
        'room': 'r',
        'group': 'c',
        'student': 's',
    }[source.type]
    week_number = get_start_date_for_untis_week(untis_week).isocalendar()[1]
    index = get_object_index(source, untis_week)
    url = 'http://rooster.strabrecht.nl/weken/%s/%02d/%s/%s%s.htm' % (untis_week, week_number, type_letter, type_letter, str(index).zfill(5))

    # Parse the page
    html = rooster.models.Cache.read_url(url)
    tree = lxml.html.fromstring(html)

    # An array to deal with the colspan system
    occupied = [0, 0, 0, 0, 0]
    events = []
    hour = 0
    # Each hour is two <tr>, with the first one starting after the header
    for hour_tr in tree.find('.//table')[1::2]:
        day = 0
        # We are at the next hour, subtract all occupied
        occupied = [max(0, x - 1) for x in occupied]

        # Go through the days (<td> tags in this <tr>), skip the first column which contains the hour information
        for day_td in hour_tr[1:]:

            # Skip through days that are still occupied by colspan cells
            while occupied[day] > 0:
                day += 1

            date = monday_date + datetime.timedelta(days=day)

            hours = int(day_td.get('rowspan')) / 2
            occupied[day] += hours

            # Get rid of whitespace
            text = ' '.join(day_td.text_content().split()).strip()
            location = ''
            if text:
                if text.split()[-1].isdigit():
                    location = text.split()[-1]
                    text = ' '.join(text.split()[:-1])

                text = str(hour + 1) + '. ' + text

                start = datetime.datetime.combine(date, timetable[hour][0])
                end = datetime.datetime.combine(date, timetable[int(hour+hours-1)][1])

                start_utc = pytz.timezone('CET').localize(start).astimezone(pytz.utc)
                end_utc = pytz.timezone('CET').localize(end).astimezone(pytz.utc)

                event = rooster.models.Event(start=start_utc, end=end_utc, title=text, location=location, source=source, repeated=repeated)
                events.append(event)

            day += 1
        hour += 1

    return events
