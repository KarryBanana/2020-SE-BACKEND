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
    aall = Author.objects.all()[i:i + 100]
    for author in aall:
        list = AuthorOfPaper.objects.filter(author=author)
        author.n_pubs = len(list)
        author.save()


# 改到70000
start = 0
while start < 254000:
    main(start)
    print(start)
    start += 100
