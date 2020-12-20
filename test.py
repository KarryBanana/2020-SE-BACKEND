import json
import os
import re

from django.db import transaction
from django.db.models import Q, F

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robin.settings")
import django

# up = {
#     'title':{
#         'way':'and',
#         'keys':[]
#     }
# }
django.setup()
from app01.models import *


@transaction.atomic
def main(i):
    i = int(i)
    pall = Paper.objects.all()[i:i + 100]
    for paper in pall:
        str = ""
        links = AuthorOfPaper.objects.filter(paper=paper)
        for link in links:
            str += link.author.name
        paper.authornamestr = str
        paper.save()
        print(str)


start = 0
while start < 37000:
    main(start)
    start += 100
