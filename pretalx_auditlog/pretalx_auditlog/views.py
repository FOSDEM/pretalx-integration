# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from pghistory.models import Events

def last_changes(n=20):
    n = 50
    events = Events.objects.order_by("-pgh_created_at")[:n].values()
    # text = [str(i["pgh_diff"]) for i in events]
    text = ""
    print(events)
    for ev in events:
        text += f'model: {ev["pgh_model"]}<br>time:{ev["pgh_created_at"]}<br>label:{ev["pgh_label"]}<br>'
        if ev["pgh_diff"] is not None:
            text += f'diff: {ev["pgh_diff"]}<br>'
        else:
            text += f'data: {ev["pgh_data"]}<br>'
        text += f'obj_id: {ev["pgh_obj_id"]}<br>'
        
        if "pgh_context" in ev and ev["pgh_context"] is not None:
            text += f'user: {ev["pgh_context"]["user"]}<br>'
            text += f'url: {ev["pgh_context"]["url"]}<br>'
        text += "<hr>"
    return HttpResponse(text)
