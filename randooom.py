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
    plist = Paper.objects.all()[i:i+100]
    for paper in plist:
        field = random.randint(0, 8)
        if field == 0:
            paper.field = "Computer Science"
            paper.save()
            continue
        elif field == 1:
            paper.field = "Material Science"
            paper.save()
            continue
        elif field == 2:
            paper.field = "Biology"
            paper.save()
            continue
        elif field == 3:
            paper.field = "Physics"
            paper.save()
            continue
        elif field == 4:
            paper.field = "Chemistry"
            paper.save()
            continue
        elif field == 5:
            paper.field = "Engineering"
            paper.save()
            continue
        elif field == 6:
            paper.field = "Medicine"
            paper.save()
            continue
        elif field == 7:
            paper.field = "Mathematics"
            paper.save()
            continue
        elif field == 8:
            paper.field = "Political science"
            paper.save()
            continue


# 改到70000
start = 0
while start < 37000:
    main(start)
    print(start)
    start += 100
