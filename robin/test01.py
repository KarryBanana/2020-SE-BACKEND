import json
import os
import re

from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robin.settings")
import django

django.setup()
from app01.models import *
import os
import randooom

paths = ["D:/aminerv2/aminer_papers_0/aminer_papers_0.txt"
         ]


def main(path):
    file = open(path)
    num = 0
    while True:
        text = file.readline()  # 只读取一行内容
        if not text:
            break
        paper = json.loads(text)

        if 'n_citation' in paper and 'url'in paper and paper['n_citation'] >300:
            num += 1
            print(num)

    file.close()
    print(path, num)


def exe():
    for p in paths:
        main(p)


exe()
