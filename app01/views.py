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
        if User.objects.filter(email=email):
            return JsonResponse({"state":0})
        print(str)
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
        password = request.POST.get('password')
        email = request.POST.get('email')
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


# 文章详情页（从搜索或其他界面进入） 从这里创建浏览记录
@require_http_methods(["GET"])
def getPaperInfoByID(request):
    try:
        uid = request.GET['uid']
        token = request.GET['token']
        user = User.objects.get(uid=uid)
        pid = request.GET['pid']
        print(pid)
        paper = Paper.objects.get(pid=pid)
        Token = UserToken.objects.get(user=user)
        if Token.token != token:
            return JsonResponse({"msg": "you token is wrong,please login in again.", "state": 0})
        if BrowerHistory.objects.filter(user=user, paper=paper):
            history = BrowerHistory.objects.filter(user=user, paper=paper)[0]
            history.save()
        else:
            history = BrowerHistory()
            history.paper = paper
            history.user = user
            history.save()
        if paper.venue:
            paper.venue_name = paper.venue.normalized_name
        else:
            paper.venue_name = ""
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

 
def cancel_follow(request):
    uid = request.POST.get('uid')
    aid = request.POST.get('aid')
    try:
        user = User.objects.get(uid=uid)
        follow_author = Author.objects.get(aid=aid)
        followed = Follow.objects.get(user=user, followed_author=follow_author)
        followed.delete()
        return JsonResponse({"state": 1, "msg": "cancel follow success!"})
    except Exception as E:
        response = {'msg': "cancel follow failed", 'state': 0}
        print(E)
        return JsonResponse(response)


def followed(request):
    try:
        uid = request.POST.get('uid')
        user = User.objects.get(uid=uid)
        user_follow = Follow.objects.filter(user=user)
        ret = []
        for au in user_follow:
            author = Author.objects.get(aid=au.followed_author_id)
            tmp = {}
            tmp['aid'] = author.aid
            tmp['name'] = author.name
            tmp['field'] = author.field
            tmp['h_index'] = author.h_index
            if author.org:
                    tmp['org'] = author.org
            else:
                tmp['org'] = ""
            ret.append(tmp)
        return JsonResponse(ret, safe=False)
    except Exception as E:
        response = {'msg': "show followed error!", 'state': 0}
        print(E)
        return JsonResponse(response)
    
    
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
        uid = request.GET['uid']
        user = User.objects.get(uid=uid)
        token = request.GET['token']
        if user:
            if UserToken.objects.get(user=user, token=token):
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
                if Venue.objects.filter(vid=paper.venue_id):
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

@require_http_methods(["POST"])
def getAuthorInfoById(request):
    aid = request.POST.get('aid')
    print(aid)
    try:
        a = Author.objects.get(aid=aid)
        author = object_to_json(a)
        author.pop('is_recorded')
        author.pop('normalized_name')
        author.pop('org')
        links = AuthorOfPaper.objects.filter(author=a)
        papers = []
        organization = ""
        year = [0, 0, 0, 0, 0, 0, 0, 0]
        if AuthorOrg.objects.filter(author=a):
            organization = AuthorOrg.objects.filter(author=a)[0].org
        co_authors = []
        for link in links:
            paper = {'pid': link.paper.pid, 'title': link.paper.title, 'n_citation': link.paper.n_citation,
                     'year': link.paper.year}
            authors_of_the_paper = AuthorOfPaper.objects.filter(paper=link.paper)
            for co_au in authors_of_the_paper:
                co_authors.append(co_au.id)
            if 2011 <= link.paper.year <= 2018:
                year[link.paper.year - 2011] += 1
            papers.append(paper)
        author['organization'] = organization
        interests = []
        interestList = Interests.objects.filter(author=a)
        for item in interestList:
            interests.append({"interest": item.field, "weight": item.weight})
        return JsonResponse({"authorInfo": author, "papers": papers, "interests": interests,
                             "n_pubs_each_year": year, "co_authors": co_authors})
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


def getBrowerHistory(request):
    uid = request.GET['uid']
    token = request.GET['token']
    user = User.objects.get(uid=uid)
    if UserToken.objects.filter(user=user, token=token):
        history_list = BrowerHistory.objects.filter(user=user)
        histories = []
        for item in history_list:
            history = {"pid": item.paper.pid, "title": item.paper.title, "time": item.browertime}
            histories.append(history)
        return JsonResponse({"res": histories, "state": 1})
    else:
        return JsonResponse({"msg": "your token is wrong,please login in again.", "state": 0})


@require_http_methods(["POST"])
def check_user(request):  # 注册
    response = {}
    try:
        name = request.POST.get('name')
        print("name", name)
        password = request.POST.get('password')
        print(password)
        if User.objects.filter(name=name):
            response['msg'] = "repetitive username"
            response['error_num'] = 1
            response['state'] = 0
        else:
            response['msg'] = "success"
            response['state'] = 1
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = -1
        response['state'] = 0
    return JsonResponse(response)


def hot_orgz(request):
    fields = ["Biology", "Chemistry", "Computer Science", "Engineering", "Material Science", "Mathematics", "Medicine",
              "Physics", "Political Science"]
    con = pymysql.connect(host="39.97.101.50", port=3306, user="root", password="123456", database="robin",
                          charset="utf8")
    cur = con.cursor()
    ln = request.POST["topnum"]
    field = fields[random.randint(0, 8)]
    field = request.POST['field']
    result = []
    op = random.randint(0, 1)
    if op == 0:
        sql = 'select app01_authororg.org,app01_authororg.id,app01_author.field from (app01_author JOIN app01_authororg ON (aid=author_id and app01_author.field="' + field + '" and app01_authororg.org!="")) group by app01_authororg.org order by count(*) desc limit ' + ln
        cur.execute(sql)
        for row in cur:
            tmp = {"OrgName": row[0], "OrgId": row[1]}
            result.append(tmp)
    else:
        sql = 'select app01_authororg.org,app01_authororg.id,app01_author.field from  app01_authororg JOIN (app01_author JOIN (app01_authorofpaper JOIN app01_paper ON app01_authorofpaper.paper_id=app01_paper.pid) ON app01_author.aid=app01_authorofpaper.author_id) ON app01_authororg.author_id = app01_author.aid and app01_author.field="' + field + '" and app01_authororg.org!="" group by app01_authororg.org order by count(*) desc limit ' + ln
        cur.execute(sql)
        for row in cur:
            tmp = {"OrgName": row[0], "OrgId": row[1]}
            result.append(tmp)
    con.close()
    return HttpResponse(json.dumps(result), content_type="application/json")


def hot_studyz(request):
    result = ["Material science", "Medicine", "Computer science", "Engineering",
              "Chemistry", "Mathematics", "Biology", "Physics", "Political science"]
    ln = request.POST["topnum"]
    return HttpResponse(json.dumps(result), content_type="application/json")


def hot_authorz(request):
    fields = ["Biology", "Chemistry", "Computer Science", "Engineering", "Material Science", "Mathematics", "Medicine",
              "Physics", "Political Science"]
    con = pymysql.connect(host="39.97.101.50", port=3306, user="root", password="123456", database="robin",
                          charset="utf8")
    cur = con.cursor()
    ln = request.POST["topnum"]
    field = fields[random.randint(0, 8)]
    field = request.POST['field']
    result = []
    op = random.randint(0, 1)
    op = 0
    if op == 0:
        sql = 'select name,aid from app01_author where field="' + field + '" order by n_citation desc limit ' + ln
        cur.execute(sql)
        for row in cur:
            tmp = {"AuthorName": row[0], "AuthorId": row[1]}
            result.append(tmp)
    else:
        sql = 'select app01_author.name,app01_author.aid from app01_author JOIN (app01_authorofpaper JOIN app01_paper ON (app01_authorofpaper.paper_id=app01_paper.pid)) ON app01_author.aid=app01_authorofpaper.author_id and app01_author.field="' + field + '" group by app01_author.aid order by count(*) desc limit ' + ln
        cur.execute(sql)
        for row in cur:
            tmp = {"AuthorName": row[0], "AuthorId": row[1]}
            result.append(tmp)
    con.close()
    return HttpResponse(json.dumps(result), content_type="application/json")


def hot_paperz(request):
    fields = ["Biology", "Chemistry", "Computer Science", "Engineering", "Material Science", "Mathematics", "Medicine",
              "Physics", "Political Science"]
    con = pymysql.connect(host="39.97.101.50", port=3306, user="root", password="123456", database="robin",
                          charset="utf8")
    cur = con.cursor()
    ln = request.POST["topnum"]
    field = request.POST['field']
    result = []
    sql = 'select title,pid from app01_paper where year>=2014 and year<=2018 and field="' + field + '"order by n_citation desc limit ' + ln
    cur.execute(sql)
    for row in cur:
        tmp = {"Title": row[0], "PaperId": row[1]}
        result.append(tmp)
    con.close()
    return HttpResponse(json.dumps(result), content_type="application/json")


def paper_recommend(request):
    key = random.randint(0,2000)
    plist = Paper.objects.filter(n_citation__gt=3000)[key:key+6]
    recommend = []
    for item in plist:
        paper = {"pid":item.pid,"title":item.title,"n_citation":item.n_citation}
        recommend.append(paper)
    return JsonResponse(recommend,safe=False)
