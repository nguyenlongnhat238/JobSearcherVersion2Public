from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField


# Create your models here.


class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    avatar = models.ImageField(null=True, upload_to='users/%Y/%m')
    user_role = models.ForeignKey(
        UserRole, on_delete=models.CASCADE, related_name='users', null=True)

    def __str__(self):
        return self.username


class ModelBase(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(ModelBase):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Major(ModelBase):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    category = models.ForeignKey(Category, null=True,
                                 related_name='majors',
                                 on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class UserProfile(ModelBase):
    user = models.OneToOneField(User, null=True,
                                on_delete=models.CASCADE, related_name='profile')
    description = models.TextField(null=True, blank=True)
    nick_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Experience(ModelBase):
    user = models.ForeignKey(UserProfile, null=True,
                             on_delete=models.CASCADE, related_name='experiences')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=100, null=False)
    company_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Education(ModelBase):
    user = models.ForeignKey(UserProfile, null=True,
                             on_delete=models.CASCADE, related_name='educations')
    degree_name = models.CharField(max_length=100, null=False)
    university_name = models.CharField(max_length=100, null=False)
    major = models.ForeignKey(Major, related_name='edu', null=True,
                              related_query_name='my_edu',
                              on_delete=models.SET_NULL)
    start_date = models.DateTimeField(auto_now_add=True)
    completionDate = models.DateTimeField(null=True, blank=True)
    CPA = models.FloatField(default=0)

    def __str__(self):
        return self.university_name


class Company(ModelBase):
    active = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, upload_to='companies/%Y/%m')
    company_name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True, blank=True)
    web_url = models.CharField(max_length=100, null=False)
    phone = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    user = models.OneToOneField(User, null=False,
                                on_delete=models.CASCADE, related_name='company')

    def __str__(self):
        return self.company_name


class Post(ModelBase):
    title = models.CharField(max_length=100, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='posts',
                                null=True, related_query_name='my_posts')
    location = models.CharField(max_length=50)
    from_salary = models.FloatField(null=True, blank=True)
    to_salary = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=25, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=50)
    time_work = models.CharField(max_length=50)
    due = models.DateTimeField(null=True, blank=True)
    description = RichTextField()
    major = models.ForeignKey(Major, related_name='posts',
                              related_query_name='major_posts',
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Apply(ModelBase):
    description = models.TextField()
    CV = models.FileField(null=True, upload_to='applies/%Y/%m')
    post = models.ForeignKey(Post,
                             related_name='applies',
                             related_query_name='post_applies',
                             on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'], name='unique_user_post_apply')
        ]

    def __str__(self):
        return self.description


class Rating(ModelBase):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rates',
                                related_query_name='creator_rates')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rates',
                                related_query_name='company_rates')
    rate = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.creator


class Comment(ModelBase):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments',
                                related_query_name='creator_comments')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='comments',
                                related_query_name='company_comments')
    content = models.TextField()

    def __str__(self):
        return self.content


class SavedPost(ModelBase):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'], name='unique_user_post')
        ]


class Token(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='token')
    token = models.CharField(max_length=256, blank=True, null=True)
