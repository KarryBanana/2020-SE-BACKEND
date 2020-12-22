import json

import pymysql
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from app01.models import *
import uuid
from app01 import models
from robin import settings
import simplejson
import random


def object_to_json(obj):
    return dict([(kk, obj.__dict__[kk]) for kk in obj.__dict__.keys() if kk != "_state"])


def responseTest(request):
    return HttpResponse("66666")


def check_mail(request):
    response = {}
    try:
        email = request.GET['email']
        str = request.GET['str']
        send_mail(
            subject='Robin',
            message=str,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email]
        )
        response['state'] = 1
        response['msg'] = "email(content is the str you upload) has been sent."
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


# 判断是否有重复的用户名：
@require_http_methods(["GET"])
def judgeRepetitiveUserName(request):
    response = {}
    name = request.GET["name"]
    if User.objects.filter(name=name):
        response['msg'] = "重复用户名"
        response['state'] = 0
    else:
        response['msg'] = "合法的用户名"
        response['state'] = 1
    return JsonResponse(response)


# 判断是否有重复的邮箱：
@require_http_methods(["GET"])
def judgeRepetitiveEmail(request):
    response = {}
    email = request.GET["email"]
    if User.objects.filter(email=email):
        response['msg'] = "重复邮箱"
        response['state'] = 0
    else:
        response['msg'] = "合法的邮箱"
        response['state'] = 1
    return JsonResponse(response)


# 根据标题关键字获取文章列表
@require_http_methods(["GET"])
def getPaperListByKey(request):
    try:
        key = request.GET['key']
        startIndex = request.GET['startIndex']
        startIndex = int(startIndex)
        paperList = Paper.objects.filter(title__icontains=key)[startIndex:startIndex + 50]
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
        keywordList = KeyWords.objects.filter(keyword__icontains=keyword)[startIndex:startIndex + 50]
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
        paper.venue_name = paper.venue.normalized_name
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
        return JsonResponse({"paperInfo": res, "authors": authors, "keywords": keywords, "urls": urls})
    except Exception as E:
        print(E)
        return HttpResponse("Error occured")


@require_http_methods(["GET"])
def getPaperListByAid(request):
    aid = request.GET['aid']
    a = Author.objects.get(aid=aid)
    list = AuthorOfPaper.objects.filter(author=a)
    gh = []
    k = 0
    for item in list:
        paper = object_to_json(item.paper)
        gh.append(paper)
        k += 1
    return JsonResponse({"size": k, "papers": gh, })


@require_http_methods(["POST"])
def complexSearch(request):
    search = simplejson.loads(request.body)
    papers = Paper.objects.all()
    if 'title' in search:
        method_of_title = search['title']['method']
        if method_of_title == "and":
            for key in search['title']['keys']:
                papers = papers.filter(title__contains=key)
        elif method_of_title == "or":
            p = Q()
            for key in search['title']['keys']:
                p = p | Q(title__contains=key)
            papers = papers.filter(p)
        elif method_of_title == "not":
            for key in search['title']['keys']:
                papers = papers.exclude(title__contains=key)

    if 'keyword' in search:
        method_of_keyword = search['keyword']['method']
        if method_of_keyword == "and":
            for key in search['keyword']['keys']:
                papers = papers.filter(keywordstr__contains=key)
        elif method_of_keyword == "or":
            p = Q()
            for key in search['keyword']['keys']:
                p = p | Q(keywordstr__contains=key)
            papers = papers.filter(p)
        elif method_of_keyword == "not":
            for key in search['keyword']['keys']:
                papers = papers.exclude(keywordstr__contains=key)
    if 'abstract' in search:
        method_of_abstract = search['keyword']['method']
        if method_of_abstract == "and":
            for key in search['abstract']['keys']:
                papers = papers.filter(abstract__contains=key)
        elif method_of_abstract == "or":
            p = Q()
            for key in search['abstract']['keys']:
                p = p | Q(abstract__contains=key)
            papers = papers.filter(p)
        elif method_of_abstract == "not":
            for key in search['abstract']['keys']:
                papers = papers.exclude(abstract__contains=key)

    if 'author' in search:
        method_of_author = search['author']['method']
        if method_of_author == "and":
            for key in search['author']['keys']:
                papers = papers.filter(authornamestr__contains=key)
        elif method_of_author == "or":
            p = Q()
            for key in search['author']['keys']:
                p = p | Q(authornamestr__contains=key)
            papers = papers.filter(p)
        elif method_of_author == "not":
            for key in search['author']['keys']:
                papers = papers.exclude(
                    authornamestr__contains=key)
    list = []
    startIndex = search["startIndex"]
    for item in papers[startIndex:startIndex + 20]:
        paper = object_to_json(item)
        authors = []
        AutherList = AuthorOfPaper.objects.filter(paper=item)
        for record in AutherList:
            authors.append({"name": record.author.name, "aid": record.author.aid})
        keywords = []
        keywordList = KeyWords.objects.filter(paper=item)
        for record in keywordList:
            keywords.append(record.keyword)

        paper['authors'] = authors
        paper['keywords'] = keywords
        list.append(paper)
    return JsonResponse({"res": list})


def followAuthor(request):
    try:
        uid = request.POST.get('uid')
        aid = request.POST.get('aid')
        user = User.objects.get(uid=uid)
        try:
            author = Author.objects.get(aid=aid)
            print(author)
            if Follow.objects.filter(user=user, followed_author=author).exists():
                return JsonResponse({"res": 1, "msg": "follow success!"}, safe=False)
            else:
                Follow.objects.create(user=user, followed_author=author)
            # tmp = {}
            # tmp['user'] = user.uid
            # tmp['author'] = author.aid
            return JsonResponse({"res": 1, "msg": "follow success!"})
        except Author.DoesNotExist:
            return JsonResponse({"res": 0, "msg": "author does not exist!"})
    except Exception as E:
        return HttpResponse("Error occurs!")


def collect_paper(request):
    try:
        uid = request.POST.get('uid')
        pid = request.POST.get('pid')
        user = User.objects.get(uid=uid)
        try:
            paper = Paper.objects.get(pid=pid)
            print(paper)
            if Collection.objects.filter(user=user, paper=paper).exists():
                return JsonResponse({"res": 1, "msg": "collect success!"}, safe=False)
            else:
                Collection.objects.create(user=user, paper=paper)
            return JsonResponse({"res": 1, "msg": "collect success!"}, safe=False)
        except Paper.DoesNotExist:
            return JsonResponse({"res": 0, "msg": "paper does not exist!"})
    except Exception as E:
        print(E)
        return HttpResponse("Error occurs!")


def check_user_info(request):
    try:
        uid = request.GET.get('uid')
        user = User.objects.get(uid=uid)
        response = {}
        response['name'] = user.name
        response['email'] = user.email
        response['intro'] = user.intro
        return JsonResponse(response)
    except Exception as E:
        print(E)
        return HttpResponse("Error occurs!")


def edit_user_info(request):
    try:
        uid = request.POST.get('uid')
        user = User.objects.get(uid=uid)
        name = request.POST.get('name')
        email = request.POST.get('email')
        intro = request.POST.get('intro')
        if User.objects.filter(name=name).exists():
            return JsonResponse({"res": 0, "msg": "name exists!"})
        if User.objects.filter(email=email).exists():
            return JsonResponse({"res": 0, "msg": "email exists!"})

        user.name = name
        user.email = email
        user.intro = intro

        user.save()  # 保存修改
        return JsonResponse({"res": 1, "msg": "edit success!"})
    except Exception as E:
        print(E)
        return HttpResponse("Error occurs!")


def hot_author(request):
    try:
        # 可能耗时
        hot_author_list = Author.objects.all().order_by("-h_index")[0:10]
        ret = []
        for author in hot_author_list:
            ret.append(author.name)
        print(ret)
        return JsonResponse({"author_list": ret, "state": 1})
    except Exception as E:
        response = {}
        response['msg'] = "Get author error!"
        response['state'] = 0
        print(E)
        return JsonResponse(response)


def hot_paper(request):
    try:
        # 可能耗时
        hot_paper_list = Paper.objects.all().order_by("-n_citation")[0:1000]
        ret = []
        # year_first = hot_paper_list[0].year
        # ret.append(hot_paper_list[0].title)
        # for paper in hot_paper_list:
        #     if paper.year == year_first:
        #         continue
        #     else:
        #         ret.append(paper.title)
        #         year_first = paper.year
        for paper in hot_paper_list:
            if 2014 < paper.year < 2018:
                ret.append(paper.title)
        print(ret)
        return JsonResponse({"paper_list": ret, "state": 1})
    except Exception as E:
        response = {}
        response['msg'] = "Get paper error!"
        response['state'] = 0
        print(E)
        return JsonResponse(response)


@require_http_methods(["GET"])
def Authentication(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                response['state'] = 1
                response['msg'] = "起飞！"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


def hot_field(request):
    ret = ["Material science", "Medicine", "Computer science", "Engineering",
           "Chemistry", "Mathematics", "Biology", "Physics", "Political science"]
    print(ret)
    return JsonResponse({"hot_field": ret, "state": 1})


def collected(request):
    try:
        uid = request.POST.get('uid')
        print(uid)
        user = User.objects.get(uid=uid)
        print(user)
        collected = Collection.objects.filter(user=user)
        ret = []
        for col in collected:
            paper = Paper.objects.get(pid=col.paper_id)
            print(paper)
            tmp = {}
            tmp['pid'] = paper.pid
            tmp['title'] = paper.title
            tmp['year'] = paper.year
            tmp['citation'] = paper.n_citation
            authors_this_paper = AuthorOfPaper.objects.filter(paper=paper)
            authors = []
            for a in authors_this_paper:
                authors.append(a.author.name)
            tmp['authors'] = authors
            if paper.venue:
                if Venue.objects.filter(vid=paper.venue_id) :
                    venue = Venue.objects.get(vid=paper.venue_id)
                    tmp['venue'] = venue.display_name
            else:
                tmp['venue'] = ""
            ret.append(tmp)
        return JsonResponse(ret, safe=False)
    except Exception as E:
        response = {}
        response['msg'] = "collect papers error!"
        response['state'] = 0
        print(E)
        return JsonResponse(response)


def cancel_collect(request):
    uid = request.POST.get('uid')
    pid = request.POST.get('pid')
    try:
        collected = Collection.objects.get(user_id=uid, paper_id=pid)
        collected.delete()
        return JsonResponse({"state": 1, "msg": "cancel collect success!"})
    except Exception as E:
        response = {'msg': "cancel collect failed", 'state': 0}
        print(E)
        return JsonResponse(response)


def getAuthorInfoById(request):
    aid = request.POST.get('aid')
    try:
        a = Author.objects.get(aid=aid)
        author = object_to_json(a)
        author.pop('is_recorded')
        links = AuthorOfPaper.objects.filter(author=a)
        papers = []
        for link in links:
            paper = {'pid': link.paper.pid, 'title': link.paper.title, 'n_citation': link.paper.n_citation,
                     'year': link.paper.year}
            papers.append(paper)
        return JsonResponse({"authorInfo": author, "papers": papers})
    except Exception as E:
        return JsonResponse({"msg": str(E), "state": 0})


def get():
    return seed_of_computer


@require_http_methods(["GET"])
def getPaperOfField(request):
    field = request.GET['field']
    print(field)
    paperList = Paper.objects.filter(field=field).order_by("-n_citation")[0:10]
    papers = []
    for item in paperList:
        paper = {'pid': item.pid, 'title': item.title, 'n_citation': item.n_citation}
        papers.append(paper)
    publish_num_of_recent_year = []
    start_year = 2014
    while start_year <= 2018:
        publish_num_of_recent_year.append({str(start_year):
                                               getseed(field)[start_year - 2014]})
        start_year += 1
    return JsonResponse({"TopPapers": papers, "n_pubs_each_year": publish_num_of_recent_year})


def getAuthorOfField(request):
    str = request.GET['field']
    if str == "Computer Science":
        file = open("app01/data/computer_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Biology":
        file = open("app01/data/biology_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Chemistry":
        file = open("app01/data/chemistry_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Medicine":
        file = open("app01/data/medicine_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Physics":
        file = open("app01/data/physic_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Political science":
        file = open("app01/data/political_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Mathematics":
        file = open("app01/data/mathematics_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Material Science":
        file = open("app01/data/material_author.json")
        data = json.load(file)
        return JsonResponse(data)
    if str == "Engineering":
        file = open("app01/data/engineering_author.json")
        data = json.load(file)
        return JsonResponse(data)


from app01.seed import *


def getseed(str):
    if str == "Computer Science":
        return seed_of_computer
    if str == "Biology":
        return seed_of_biology
    if str == "Chemistry":
        return seed_of_chemistry
    if str == "Medicine":
        return seed_of_medicine
    if str == "Physics":
        return seed_of_physic
    if str == "Political science":
        return seed_of_Political
    if str == "Mathematics":
        return seed_of_Mathematics
    if str == "Material Science":
        return seed_of_material
    if str == "Engineering":
        return seed_of_engieering
