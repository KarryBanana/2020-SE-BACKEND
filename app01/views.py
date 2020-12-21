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
def getPaperInfoByKey(request):
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
def getPaperInfoByKeyword(request):
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


def hot_field(request):
    ret = ["Material science", "Medicine", "Computer science", "Engineering",
           "Chemistry", "Mathematics", "Biology", "Physics", "Political science"]
    print(ret)
    return JsonResponse({"hot_field": ret, "state": 1})


def collected(request):
    try:
        uid = request.POST.get('uid')
        user = User.objects.get(uid=uid)
        collected = Collection.objects.filter(user=user)
        ret = []
        for col in collected:
            paper = Paper.objects.get(pid=col.paper_id)
            tmp = {}
            tmp['title'] = paper.title
            tmp['year'] = paper.year
            authors_this_paper = AuthorOfPaper.objects.filter(paper=paper)
            authors = []
            for a in authors_this_paper:
                authors.append(a.author.name)
            tmp['authors'] = authors
            venue = Venue.objects.get(vid=paper.venue_id)
            tmp['venue'] = venue.display_name
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
        response = {}
        response['msg'] = "cancel collect failed"
        response['state'] = 0
        print(E)
        return JsonResponse(response)