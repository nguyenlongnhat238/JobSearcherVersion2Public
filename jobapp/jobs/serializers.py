
import hashlib
import uuid
from rest_framework import serializers
from .models import Apply, Comment, Company, Education, Experience, Post, Rating, SavedPost, Token, User, UserProfile, UserRole, Major, Category
from django.db.models import Avg
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['id', 'name', 'description', 'category']


class CategorySerializer(serializers.ModelSerializer):
    majors = MajorSerializer(read_only=True, many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'majors']


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'desciption']


class ExperienceProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class EducationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    educations = EducationProfileSerializer(read_only=True, many=True)
    experiences = ExperienceProfileSerializer(read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'description',
                  'nick_name', 'educations', 'experiences']


class UserProfileBasic(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'description',
                  'nick_name']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['user', 'token']


class UserSerializer(serializers.ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')
    # profile_detail = serializers.SerializerMethodField()
    profile = UserProfileBasic(read_only=True)

    # def get_profile_detail(self, obj):
    #     request = self.context['request']
    #     profile = UserProfile.objects.filter(user=obj.id).first()
    #     return UserProfileBasic(profile, context={'request': request}).data

    def get_avatar_path(self, obj):
        request = self.context['request']
        if obj.avatar and not obj.avatar.name.startswith("/static"):
            path = '/static/%s' % obj.avatar.name

            return request.build_absolute_uri(path)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'password', 'email',
                  'avatar', 'avatar_path',
                  'user_role',  'is_active', 'profile']
        extra_kwargs = {
            'password': {
                'write_only': True
            }, 'avatar_path': {
                'read_only': True
            }, 'avatar': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        for attr, value in validated_data.items():
            print(value)
            if attr == 'avatar':
                if value:
                    print(value.name)
        user = User(**data)
        user.set_password(user.password)
        user.is_active = False
        user.user_role_id = 2
        user.save()
        salt = uuid.uuid4().hex
        hash_object = hashlib.sha256(salt.encode() + str(user.id).encode())
        token = hash_object.hexdigest() + ':' + salt

        token_serializer = TokenSerializer(
            data={'user': user.id, 'token': token})
        if token_serializer.is_valid(raise_exception=False):
            token_serializer.save()

            fullName = f'{user.first_name} {user.last_name}'
            html_message = render_to_string(
                'confirm-email.html', {'fullName': fullName, 'token': token})
            content = strip_tags(html_message)
            send_mail('CONFIRM EMAIL USER',
                      content,
                      settings.EMAIL_HOST_USER,
                      [user.email],
                      html_message=html_message,
                      fail_silently=False)
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class CompanySerializer(serializers.ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')
    rateAvg = serializers.SerializerMethodField(read_only=True)

    def get_rateAvg(self, obj):
        requests = self.context['request']
        a = Rating.objects.filter(company_id=obj.id).aggregate(Avg('rate'))
        if a:
            return a['rate__avg']
        return 0

    def get_avatar_path(self, obj):
        request = self.context['request']
        if obj.avatar and not obj.avatar.name.startswith("/static"):
            path = '/static/%s' % obj.avatar.name

            return request.build_absolute_uri(path)

    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'avatar_path': {
                'read_only': True
            }, 'avatar': {
                'write_only': True
            }
        }


class CompanyAuthSerializer(CompanySerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, company):
        request = self.context.get('request')
        if request:
            r = Rating.objects.filter(company=company).filter(
                creator=request.user).first()
            if r:
                return r.rate

    class Meta:
        model = Company
        fields = CompanySerializer.Meta.fields


class PostSerializer(serializers.ModelSerializer):
    avatar_company = serializers.SerializerMethodField()
    major_name = serializers.SerializerMethodField()
    company_detail = serializers.SerializerMethodField()

    def get_company_detail(self, obj):
        request = self.context['request']
        company = Company.objects.get(pk=obj.company_id)
        return CompanySerializer(company, context={'request': request}).data

    def get_major_name(self, obj):
        requests = self.context['request']
        return obj.major.name

    def get_avatar_company(self, obj):
        request = self.context['request']
        path = '/static/%s' % obj.company.avatar
        return request.build_absolute_uri(path)

    class Meta:
        model = Post
        fields = ['id', 'title', 'company', 'location', 'from_salary', 'to_salary', 'gender',
                  'quantity', 'description', 'type', 'time_work', 'due', 'description', 'major',
                  'major_name', 'avatar_company', 'company_detail']
        extra_kwargs = {
            'avatar_company': {
                'read_only': True
            },
            'major_name': {
                'read_only': True
            },
            'company_detail': {
                'read_only': True
            }
        }


class ApplySerializer(serializers.ModelSerializer):
    CV_path = serializers.SerializerMethodField(source='CV')
    avatar_user = serializers.SerializerMethodField()
    post_detail = serializers.SerializerMethodField()

    def get_post_detail(self, obj):
        request = self.context['request']
        post = Post.objects.get(pk=obj.post_id)
        return PostSerializer(post, context={'request': request}).data

    def get_avatar_user(self, obj):
        request = self.context['request']
        path = '/static/%s' % obj.user.avatar
        return request.build_absolute_uri(path)

    def get_CV_path(self, obj):
        request = self.context['request']

        if obj.CV and not obj.CV.name.startswith("/static"):
            path = '/static/%s' % obj.CV.name
            return request.build_absolute_uri(path)

    class Meta:
        model = Apply
        fields = ['id', 'description', 'CV', 'post',
                  'user', 'CV_path', 'avatar_user', 'post_detail']
        extra_kwargs = {
            'CV_path': {
                'read_only': True
            }, 'CV': {
                'write_only': True
            }, 'avatar_user': {
                'read_only': True
            },
            'post_detail': {
                'read_only': True
            }
        }


class CommentSerializer(serializers.ModelSerializer):
    avatar_user = serializers.SerializerMethodField()
    name_user = serializers.SerializerMethodField()

    def get_name_user(self, obj):
        request = self.context['request']
        name = obj.creator.first_name + " " + obj.creator.last_name
        return name

    def get_avatar_user(self, obj):
        request = self.context['request']
        path = '/static/%s' % obj.creator.avatar
        return request.build_absolute_uri(path)

    class Meta:
        model = Comment
        fields = ['id', 'creator', 'company',
                  'content', 'avatar_user', 'name_user']
        extra_kwargs = {
            'avatar_user': {
                'read_only': True
            },
            'name_user': {
                'read_only': True
            }
        }


class SavedPostSerializer(serializers.ModelSerializer):
    post_detail = serializers.SerializerMethodField()

    def get_post_detail(self, obj):
        p = Post.objects.get(id=obj.post.id)
        return PostSerializer(p, context={'request': self.context['request']}).data

    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'user', 'post_detail']
        extra_kwargs = {'user': {'required': False}}
