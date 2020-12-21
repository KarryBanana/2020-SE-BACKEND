import json
import os
import re

from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robin.settings")
import django

django.setup()
from app01.models import Paper, Author, KeyWords, Venue, PaperURL, FieldOfStudy
import os
import random


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


@transaction.atomic
def main():
    file = open("D:/aminerv2/aminer_venues/aminer_venues.txt")
    num = 0
    while True:
        text = file.readline()  # 只读取一行内容
        if not text:
            break
        venue = json.loads(text)
        V = Venue()
        if 'id' in venue:
            V.vid = venue['id']
        if 'DisplayName' in venue:
            V.display_name = venue['DisplayName']
        if 'NormalizedName' in venue:
            V.normalized_name = venue['NormalizedName']
        if len(V.normalized_name) > 500 or len(V.display_name) > 500:
            continue
        V.save()
        num += 1
        print(num)

    file.close()
    print(num)


main()
