import json
import os
import re
import randooom

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
        # field = random.randint(0, 8)
        if 'software' in paper.title.lower() or 'network' in paper.title.lower()\
                or 'computer' in paper.title.lower() or 'algorithm' in paper.title.lower()\
                or 'data mining' in paper.title.lower():
            paper.field = "Computer Science"
            paper.save()
            continue
        elif 'material' in paper.title.lower():
            paper.field = "Material Science"
            paper.save()
            continue
        elif 'biolo' in paper.title.lower() or 'disease' in paper.title.lower() \
                or 'germ' in paper.title.lower() or 'gene' in paper.title.lower():
            paper.field = "Biology"
            paper.save()
            continue
        elif 'physic' in paper.title.lower():
            paper.field = "Physics"
            paper.save()
            continue
        elif 'chemi' in paper.title.lower():
            paper.field = "Chemistry"
            paper.save()
            continue
        elif 'engineer' in paper.title.lower()  or 'automat' in paper.title.lower() \
                or 'factory' in paper.title.lower() or 'design' in paper.title.lower():
            paper.field = "Engineering"
            paper.save()
            continue
        elif 'market' in paper.title.lower() or 'city' in paper.title.lower() or 'global' in paper.title.lower() \
            or 'country' in paper.title.lower() or 'education' in paper.title.lower():
            paper.field = "Political science"
            paper.save()
            continue

start = 0
while start < 37000:
    main(start)
    print(start)
    start += 100
