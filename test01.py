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
# p = Paper.objects.get(pid="53e99785b7602d9701f408c0")
# print(p.venue_id)
k = Venue.objects.get(vid="54509bf0dabfaed2f6e76ba1")



