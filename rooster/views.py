from django.http import HttpResponse
import strabrecht.settings
import untis, json

# Create your views here.
def index(request):
    return HttpResponse(open(strabrecht.settings.PROJECT_PATH + '/index.html').read().replace('UNTIS_JSON', untis.get_sources_json()))

def sources(request):
    return HttpResponse(untis.get_sources_json(), content_type="application/json")