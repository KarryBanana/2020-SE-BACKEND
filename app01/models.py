from django.db import models


class Venue(models.Model):
    vid = models.CharField(max_length=50, primary_key=True)
    display_name = models.CharField(max_length=500)
    normalized_name = models.CharField(max_length=500)


class Author(models.Model):
    aid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    normalized_name = models.CharField(max_length=50)
    org = models.CharField(max_length=50)
    n_citation = models.IntegerField(default=0)
    position = models.CharField(max_length=50)
    n_pubs = models.IntegerField(default=0)
    h_index = models.IntegerField(default=0)
    is_recorded = models.IntegerField(default=-1)
    field = models.CharField(default="", max_length=200)

    class Meta:
        indexes = [
            models.Index(
                fields=['aid'],
                name='aid',
            ),
            models.Index(
                fields=['is_recorded'],
                name='is_recorded',
            ),
            models.Index(
                fields=['field'],
                name='field',
            ),
            models.Index(
                fields=['h_index'],
                name='h_index',
            ),
        ]


class Paper(models.Model):
    pid = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=200, default="")
    venue_name = models.CharField(max_length=50, default="")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, blank=True, null=True)
    year = models.IntegerField(default=2000)
    n_citation = models.IntegerField(default=0)
    page_start = models.IntegerField(default=0)
    page_end = models.IntegerField(default=0)
    doc_type = models.CharField(max_length=50, default="")
    lan = models.CharField(max_length=50, default="")
    publisher = models.CharField(max_length=50, default="")
    volume = models.IntegerField(default=0)
    issue = models.CharField(max_length=50, default="")
    issn = models.CharField(max_length=50, default="")
    isbn = models.CharField(max_length=50, default="")
    doi = models.CharField(max_length=50, default="")
    pdfURL = models.CharField(max_length=500, default="")
    abstract = models.TextField(max_length=5000, default="")
    keywordstr = models.TextField(max_length=20000, default="")
    authornamestr = models.TextField(max_length=20000, default="")
    field = models.CharField(default="", max_length=200, db_index=False)

    class Meta:
        indexes = [
            models.Index(
                fields=['pid'],
                name='pid',
            ),
            models.Index(
                fields=['title'],
                name='title',
            ),
        ]


class AuthorOfPaper(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    rank = models.IntegerField(blank=False, null=False)

    class Meta:
        indexes = [
            models.Index(
                fields=['paper_id'],
                name='paper_id',
            ),
            models.Index(
                fields=['author_id'],
                name='author_id',
            ),
        ]


class Interests(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    field = models.CharField(max_length=50)
    weight = models.IntegerField(blank=False, null=False)


class PaperURL(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    url = models.CharField(max_length=100)


class Reference(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='paper')
    referenced_paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='referenced_paper')


class KeyWords(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)


class FieldOfStudy(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    fos = models.CharField(max_length=100)


class AuthorOrg(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    org = models.CharField(max_length=100)


class User(models.Model):
    uid = models.AutoField(primary_key=True)
    aid = models.IntegerField(default=-1)
    password = models.CharField(max_length=50, null=False, blank=False, default="a12345678")
    name = models.CharField(max_length=50)
    email = models.EmailField(blank=False, null=False)
    intro = models.CharField(default="", max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,null=True,blank=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followed_author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)


class Manager(models.Model):
    manager_name = models.CharField(max_length=50, primary_key=True)
    manager_password = models.CharField(max_length=50)


class SystemMessage(models.Model):
    content = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type_node = models.IntegerField(default=-1)


class UserToken(models.Model):
    user = models.OneToOneField(to='User', on_delete=models.CASCADE)
    token = models.CharField(max_length=64)


class BrowerHistory(models.Model):
    BHid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    browertime = models.DateTimeField(auto_now=True)
