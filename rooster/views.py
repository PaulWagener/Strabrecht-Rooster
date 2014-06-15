from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import strabrecht.settings
import untis, json
from models import Source

# Create your views here.
def index(request):
    return HttpResponse(open(strabrecht.settings.PROJECT_PATH + '/index.html').read()
        .replace('UNTIS_JSON', untis.get_sources_json())
        .replace('UNTIS_STARTDATE', str(untis.get_start_date_for_untis_week('Dagelijks')))
        .replace('DOMAIN', request.META['HTTP_HOST'])
        )

@csrf_exempt
def events(request, type, code, file_type):
    # Get the relevant source
    source = Source.get_source(type, code)

    events = source.get_events()

    if file_type == 'json':
        return HttpResponse(json.dumps([event.as_json() for event in events]), content_type='application/json')
    elif file_type == 'ics':
        format = '%Y%m%dT%H%M00Z'

        content = 'BEGIN:VCALENDAR\r\n'
        content += 'VERSION:2.0\r\n'
        content += 'PRODID:-//hacksw/handcal//NONSGML v1.0//EN\r\n'

        for event in events:
            content += 'BEGIN:VEVENT\r\n'
            content += 'DTSTART:' + event.start.strftime(format) + '\r\n'
            content += 'DTEND:' + event.end.strftime(format) + '\r\n'
            content += 'SUMMARY:' + event.title + '\r\n'
            content += 'LOCATION:' + event.location + '\r\n'
            if event.repeated:
                content += 'RRULE:FREQ=WEEKLY;COUNT=10' + '\r\n'
            content += 'END:VEVENT\r\n'

        content += 'END:VCALENDAR'

        response = HttpResponse(content)
        response['Content-Type'] = 'text/calendar; charset-utf-8'
        response['Content-Disposition'] = 'inline; filename=%s.ics' % code
        response['Cache-Control'] = 'max-age=7200, private, must-revalidate'
        return response

