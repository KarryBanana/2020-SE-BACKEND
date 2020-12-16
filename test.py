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

paths = [  #"D:/aminerv2/aminer_authors_0/aminer_authors_0.txt",#169W
    # "D:/aminerv2/aminer_authors_0/aminer_authors_1.txt",#169W
    # "D:/aminerv2/aminer_authors_0/aminer_authors_2.txt",#169W
    #"D:/aminerv2/aminer_authors_0/aminer_authors_3.txt",#767W
     #"D:/aminerv2/aminer_authors_0/aminer_authors_4.txt",#1223W
    # "D:/aminerv2/aminer_authors_1/aminer_authors_5.txt",#1240W
     #"D:/aminerv2/aminer_authors_1/aminer_authors_6.txt",#1200W
     #"D:/aminerv2/aminer_authors_1/aminer_authors_7.txt",
     "D:/aminerv2/aminer_authors_1/aminer_authors_8.txt",#709W
    # "D:/aminerv2/aminer_authors_1/aminer_authors_9.txt",
    # "D:/aminerv2/aminer_authors_2/aminer_authors_10.txt",
    # "D:/aminerv2/aminer_authors_2/aminer_authors_11.txt",# 很多
    # "D:/aminerv2/aminer_authors_2/aminer_authors_12.txt",# 很多
    # "D:/aminerv2/aminer_authors_2/aminer_authors_13.txt",# 很多
    # "D:/aminerv2/aminer_authors_2/aminer_authors_14.txt",# 很多
    # "D:/aminerv2/aminer_authors_3/aminer_authors_15.txt",# 多//360W
    # "D:/aminerv2/aminer_authors_3/aminer_authors_16.txt",# 多
    #"D:/aminerv2/aminer_authors_3/aminer_authors_17.txt",# 多
     #"D:/aminerv2/aminer_authors_3/aminer_authors_18.txt",# 中
    #"D:/aminerv2/aminer_authors_3/aminer_authors_19.txt",  #
]


def main(path):
    file = open(path)
    num = 0
    while True:
        text = file.readline()  # 只读取一行内容
        if not text:
            break
        author = json.loads(text)

        if author['h_index']>5:
            num += 1
            print(num)

    file.close()
    print(path, num)


def exe():
    for p in paths:
        main(p)


exe()
