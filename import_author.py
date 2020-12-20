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

paths = ["D:/aminerv2/aminer_authors_0/aminer_authors_0.txt",
         # "D:/aminerv2/aminer_authors_0/aminer_authors_1.txt",
         # "D:/aminerv2/aminer_authors_0/aminer_authors_2.txt",
         # "D:/aminerv2/aminer_authors_0/aminer_authors_3.txt",
         # "D:/aminerv2/aminer_authors_0/aminer_authors_4.txt",
         # "D:/aminerv2/aminer_authors_1/aminer_authors_5.txt",
         # "D:/aminerv2/aminer_authors_1/aminer_authors_6.txt",
         # "D:/aminerv2/aminer_authors_1/aminer_authors_7.txt",
         # "D:/aminerv2/aminer_authors_1/aminer_authors_8.txt",
         # "D:/aminerv2/aminer_authors_1/aminer_authors_9.txt",
         # "D:/aminerv2/aminer_authors_2/aminer_authors_10.txt",
         # "D:/aminerv2/aminer_authors_2/aminer_authors_11.txt",
         # "D:/aminerv2/aminer_authors_2/aminer_authors_12.txt",
         # "D:/aminerv2/aminer_authors_2/aminer_authors_13.txt",
         # "D:/aminerv2/aminer_authors_2/aminer_authors_14.txt",
         # "D:/aminerv2/aminer_authors_3/aminer_authors_15.txt",
         # "D:/aminerv2/aminer_authors_3/aminer_authors_16.txt",
         # "D:/aminerv2/aminer_authors_3/aminer_authors_17.txt",
         # "D:/aminerv2/aminer_authors_3/aminer_authors_18.txt",
         # "D:/aminerv2/aminer_authors_3/aminer_authors_19.txt",
         ]


@transaction.atomic
def main(path):
    file = open(path)
    num = 0
    while True:
        text = file.readline()  # 只读取一行内容
        if not text:
            break
        author = json.loads(text)
        if 'id' not in author:
            continue
        if 'h_index' not in author:
            continue
        id = author['id']
        try:
            A = Author()
            A.aid = id
            num += 1
            if 'name' in author and len(author['name']) <= 50:
                A.name = author['name']
            if 'normalized_name' in author and len(author['normalized_name']) <= 50:
                A.normalized_name = author['normalized_name']
            if 'org' in author and len(author['org']) <= 50:
                A.org = author['org']
            if 'position' in author and len(author['position']) <= 50:
                A.position = author['position']
            if 'n_citation' in author:
                A.n_citation = author['n_citation']
            if 'n_pubs' in author:
                A.n_pubs = author['n_pubs']
            if 'h_index' in author:
                A.h_index = author['h_index']
            A.save()
            if 'orgs' in author:
                for item in author['orgs']:
                    ao = AuthorOrg()
                    if len(item) > 50:
                        continue
                    ao.author = A
                    ao.org = item
                    ao.save()
            if 'tags' in author:
                for item in author['tags']:
                    if 'w' not in item or 't' not in item:
                        continue
                    if len(item['t']) > 50:
                        continue
                    tag = Interests()
                    tag.author = A
                    tag.field = item['t']
                    tag.weight = item['w']
                    tag.save()
            if 'pubs' in author:
                for item in author['pubs']:
                    paper = Paper()
                    paper.pid = item['i']
                    paper.save()
                    re = AuthorOfPaper()
                    re.paper =paper
                    re.author = A
                    re.rank = item['r']
                    re.save()
        except Exception as E:
            op = 1
        print(num)
        if num ==1000:
            break

    file.close()
    print(num)


for path in paths:
    main(path)
