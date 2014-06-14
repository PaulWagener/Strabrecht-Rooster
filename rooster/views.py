from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import strabrecht.settings
import untis, json
from models import Source

# Create your views here.
def index(request):
    return HttpResponse(open(strabrecht.settings.PROJECT_PATH + '/index.html').read()
        #.replace('UNTIS_JSON', untis.get_sources_json())
        #.replace('UNTIS_STARTDATE', str(untis.get_start_date_for_untis_week('Dagelijks'))))
        .replace('DOMAIN', request.META['HTTP_HOST'])
        )

@csrf_exempt
def events(request, type, code, file_type):
    # Get the relevant source
    source = Source.get_source(type, code)
    events = source.get_events()

    if file_type == 'json':
        return HttpResponse(json.dumps([event.as_json() for event in events]))
    elif file_type == 'ics':
        return HttpResponse(str(events))