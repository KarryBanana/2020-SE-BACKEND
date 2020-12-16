from django.http import HttpResponse, JsonResponse
from app01.models import *


def object_to_json(obj):
    return dict([(kk, obj.__dict__[kk]) for kk in obj.__dict__.keys() if kk != "_state"])


def responseTest(request):
    return HttpResponse("66666")


def getPaperInfoByKey(request):
    try:
        key = request.GET['key']
        print(key)
        paperList = Paper.objects.filter(title__icontains=key)
        list = []
        for item in paperList:
            list.append(object_to_json(item))
        return JsonResponse({"res":list})
    except Exception as E:
        return HttpResponse("Error occured")
