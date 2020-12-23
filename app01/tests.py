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


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[randooom.randint(0, length)]
    return random_str


# 不加这一句写入太慢了 venue 没写
@transaction.atomic
def main():
    p = Paper.objects.get(pid="53e9978db7602d9701f51a56")
    al = AuthorOfPaper.objects.filter(paper=p)
    print(p.venue)
    for item in al:
        print(item.author.name)

main()
