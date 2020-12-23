import json
import os
import re
import random

from django.db import transaction
from django.db.models import Q, F

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robin.settings")
import django

django.setup()
from app01.models import *


@transaction.atomic #文章年份
def main(i):
    i = int(i)
    plist = Paper.objects.all()[i:i + 100]
    for p in plist:
        try:
            p.year = 2010 + random.randint(1, 8)
            p.save()
        except Exception as E:
            op = 1
# @transaction.atomic  # 发表数计数
# def main(i):
#     i = int(i)
#     alist = Author.objects.all()[i:i + 100]
#     for a in alist:
#         length = len(AuthorOfPaper.objects.filter(author=a))
#         a.n_pubs = length
#         a.save()
#
#
start = 0
while start < 37000:
    main(start)
    print(start)
    start += 100
