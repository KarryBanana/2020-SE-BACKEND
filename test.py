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


@transaction.atomic
def main(i):
    i = int(i)
    alist = Author.objects.all()[i:i + 100]
    for a in alist:
        try:
            link = AuthorOfPaper.objects.filter(author=a)[0]
            a.field = link.paper.field
            a.save()
        except Exception as E:
            op = 1


# 改到70000
start = 0
while start < 254000:
    main(start)
    print(start)
    start += 100
