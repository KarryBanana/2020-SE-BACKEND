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
def fix_author_name_str(i):
    i = int(i)
    plist = Paper.objects.all()[i:i + 100]
    for paper in plist:
        str = ""
        links = AuthorOfPaper.objects.filter(paper=paper)
        for link in links:
            str += link.author.name
        paper.authornamestr = str
        paper.save()


names = ["J. M. Ball", "Karl G. Hill", "Donna Bryant", "Y. Van de Peer", "Shelley E. Taylor", "Hai Sook Kim",
         "Robert Morris",
         "M. Niranjan", "Paul D. Thomas", "M. C. SERREZE"]

positions = ["Professor", "Lecturer", "Researcher", "Chair", "Associate professor"]


def fix_h_index(i):
    i = int(i)
    alist = Author.objects.all()[i:i + 100]
    for author in alist:
        if author.h_index == 0:
            author.h_index = random.randint(1, 9)
        if author.name == "":
            author.name = names[random.randint(0, 9)]
        author.name = author.name.upper()
        if author.position == "":
            author.position = positions[random.randint(0, 4)]
        if author.n_citation == 0:
            author.n_citation = random.randint(10, 2439)
        author.normalized_name = author.name.lower()
        author.save()


def toName(name):
    name  = list(name)
    i = 0
    while i < len(name):
        if name[i].isupper() and i != 0 and name[i - 1].isalpha():
            name[i] = name[i].lower()
        i+=1
    return ''.join(name)

@transaction.atomic()
def fix_author_name(i):
    i = int(i)
    alist = Author.objects.all()[i:i + 100]
    for author in alist:
        author.name = toName(author.name)
        author.save()

i=0
while i< 260000:
    fix_author_name(i)
    i+=100
    print(i)
