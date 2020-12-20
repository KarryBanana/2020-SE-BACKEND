import json
import os
import re

from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robin.settings")
import django

django.setup()
from app01.models import *
import os
import random

num = 0


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


paths = [
    "D:/aminerv2/aminer_papers_0/aminer_papers_0.txt",
    # "D:/aminerv2/aminer_papers_0/aminer_papers_1.txt",
    # "D:/aminerv2/aminer_papers_0/aminer_papers_2.txt",
    # "D:/aminerv2/aminer_papers_0/aminer_papers_3.txt",
    # "D:/aminerv2/aminer_papers_1/aminer_papers_4.txt",
    # "D:/aminerv2/aminer_papers_1/aminer_papers_5.txt",
    # "D:/aminerv2/aminer_papers_1/aminer_papers_6.txt",
    # "D:/aminerv2/aminer_papers_1/aminer_papers_7.txt",
    # "D:/aminerv2/aminer_papers_2/aminer_papers_8.txt",
    # "D:/aminerv2/aminer_papers_2/aminer_papers_9.txt",
    # "D:/aminerv2/aminer_papers_2/aminer_papers_10.txt",
    # "D:/aminerv2/aminer_papers_2/aminer_papers_11.txt",
    # "D:/aminerv2/aminer_papers_3/aminer_papers_12.txt",
    # "D:/aminerv2/aminer_papers_3/aminer_papers_13.txt",
    # "D:/aminerv2/aminer_papers_3/aminer_papers_14.txt",
]


def main(path, num=num):
    file = open(path)
    while True:
        text = file.readline()  # 只读取一行内容
        if not text:
            break
        paper = json.loads(text)
        if 'n_citation' not in paper:
            continue
        p = Paper()
        if 'id' in paper:
            p.pid = paper['id']
        if 'title' in paper and len(paper['title']) <= 200:
            p.title = paper['title']
        else:
            continue

        if 'year' in paper:
            p.year = paper['year']
        p.n_citation = paper['n_citation']
        if 'page_start' in paper and paper['page_start'].isdigit():
            p.page_start = paper['page_start']
        if 'page_end' in paper and paper['page_end'].isdigit():
            p.page_end = paper['page_end']
        if 'page_end' in paper and re.match("^\d+\+\d+$", paper['page_end']):
            p.page_end = eval(paper['page_end'])
        if 'doc_type' in paper:
            p.doc_type = paper['doc_type']
        if 'lang' in paper:
            p.lan = paper['lang']
        if 'publisher' in paper and len(paper['publisher']) <= 50:
            p.publisher = paper['publisher']
        if 'volume' in paper and paper['volume'].isdigit():
            p.volume = paper['volume']
        if 'issue' in paper and len(paper['issue']) <= 50:
            p.issue = paper['issue']
        if 'issn' in paper and len(paper['issn']) <= 50:
            p.issn = paper['issn']
        if 'isbn' in paper and len(paper['isbn']) <= 50:
            p.isbn = paper['isbn']
        if 'doi' in paper and len(paper['doi']) <= 50:
            p.doi = paper['doi']
        if 'pdf' in paper and len(paper['pdf']) <= 50:
            p.pdfURL = paper['pdf']
        if 'abstract' in paper:
            p.abstract = paper['abstract']
        p.save()
        if 'authors' in paper:
            rank = 0
            for author in paper['authors']:
                a = Author()
                if 'name' in author and len(author['name']) < 50:
                    a.name = author['name']
                if 'id' in author:
                    a.aid = author['id']
                else:
                    continue
                if Author.objects.filter(aid=author['id']) is not None:
                    continue
                a.save()
                ap = AuthorOfPaper()
                ap.author = a
                ap.paper = p
                ap.rank = rank
                ap.save()
                rank += 1
        if 'keywords' in paper:
            for keyword in paper['keywords']:
                if len(keyword) <= 100:
                    k = KeyWords()
                    k.paper = p
                    k.keyword = keyword
                    k.save()
        if 'url' in paper:
            for url in paper['url']:
                if len(url) > 100:
                    continue;
                paperURL = PaperURL()
                paperURL.paper = p
                paperURL.url = url
                paperURL.save()
        if 'fos' in paper:
            for field in paper['keywords']:
                FOS = FieldOfStudy()
                FOS.paper = p
                FOS.fos = field
                FOS.save()
        if 'references' in paper:
            reference_pid_list = paper['references']
            for pid in reference_pid_list:
                if Paper.objects.filter(pid=pid) is None:
                    np = Paper()
                    np.pid = pid
                    np.save()
        if 'venue' in paper:
            if 'id' in paper['venue']:
                try:
                    v = Venue.objects.get(vid=paper['venue']['id'])
                    p.venue = v
                    p.venue_name = v.display_name
                    p.save()
                except Exception as E:
                    op = 1
        num += 1
        print(num)
        if num == 1000:
            break
    file.close()
    print(num)


for path in paths:
    main(path, num)
