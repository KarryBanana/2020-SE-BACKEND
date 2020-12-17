from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from app01.models import *
import uuid
from app01 import models


# token = uuid.uuid4()
# models.UserToken.objects.update_or_create(user=user, defaults={'token': token})

def object_to_json(obj):
    return dict([(kk, obj.__dict__[kk]) for kk in obj.__dict__.keys() if kk != "_state"])


def responseTest(request):
    return HttpResponse("66666")


# 根据标题关键字获取文章列表
@require_http_methods(["GET"])
def getPaperListByKey(request):
    try:
        key = request.GET['key']
        startIndex = request.GET['startIndex']
        startIndex = int(startIndex)
        paperList = Paper.objects.filter(title__icontains=key)[startIndex:startIndex+50]
        list = []
        for item in paperList:
            paper = object_to_json(item)
            paper.pop('abstract')
            list.append(paper)
        return JsonResponse({"res": list})
    except Exception as E:
        return HttpResponse("Error occured")


# 根据文章关键词查找文章
@require_http_methods(["GET"])
def getPaperListByKeyword(request):
    try:
        keyword = request.GET['keyword']
        startIndex = request.GET['startIndex']
        startIndex = int(startIndex)
        keywordList = KeyWords.objects.filter(keyword__icontains=keyword)[startIndex:startIndex+50]
        list = []
        for item in keywordList:
            paper = object_to_json(item.paper)
            paper.pop('abstract')
            list.append(paper)
        return JsonResponse({"res": list})
    except Exception as E:
        return HttpResponse("Error occured")


@require_http_methods(["POST"])
def register(request):  # 注册
    response = {}
    try:
        name = request.POST.get('name')
        print("name", name)
        password = request.POST.get('password')
        print(password)
        email = request.POST.get('email')
        if User.objects.filter(name=name):
            response['msg'] = "repetitive username"
            response['error_num'] = 1
            response['state'] = 0
        elif User.objects.filter(email=email):
            response['msg'] = "repetitive email"
            response['error_num'] = 2
            response['state'] = 0
        else:
            p = User()
            p.name = name
            p.password = password
            p.email = email
            p.save()
            response['msg'] = "success"
            response['state'] = 1
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = -1
        response['state'] = 0
    return JsonResponse(response)


@require_http_methods(["POST"])
def login(request):
    response = {}
    try:
        name = request.POST.get('name')
        password = request.POST.get('password')
        if User.objects.filter(name=name):
            user = User.objects.get(name=name)
            if user.password == password:
                token = uuid.uuid4()
                models.UserToken.objects.update_or_create(user=user, defaults={'token': token})
                response['msg'] = "login successfully!"
                response['state'] = 1
                response['name'] = name
                response['token'] = token
                response['uid'] = user.uid
                response['aid'] = user.aid
            else:
                response['msg'] = "Wrong username or password,try again!"
                response['error_num'] = 1
                response['state'] = 0
        else:
            response['msg'] = "Wrong username or password,try again!"
            response['error_num'] = 2
            response['state'] = 0
    except Exception as e:
        response['msg'] = "unknown error"
        response['error_num'] = -1
        response['state'] = 0

    return JsonResponse(response)


# 文章详情页（从搜索或其他界面进入）
@require_http_methods(["GET"])
def getPaperInfoByID(request):
    try:
        pid = request.GET['pid']
        paper = Paper.objects.get(pid=pid)
        res = object_to_json(paper)
        authors = []
        AutherList = AuthorOfPaper.objects.filter(paper=paper)
        for record in AutherList:  # 只需要id name rank
            au = object_to_json(record)
            au.pop('id')
            au.pop('paper_id')
            au['name'] = record.author.name
            authors.append(au)
        keywords = []
        keywordList = KeyWords.objects.filter(paper=paper)
        for record in keywordList:  # 只需要id name rank
            keywords.append(record.keyword)
        urls = []
        urlList = PaperURL.objects.filter(paper=paper)
        for record in urlList:  # 只需要id name rank
            urls.append(record.url)
        return JsonResponse({"paperInfo": res,"authors":authors,"keywords":keywords,"urls":urls})
    except Exception as E:
        print(E)
        return HttpResponse("Error occured")
