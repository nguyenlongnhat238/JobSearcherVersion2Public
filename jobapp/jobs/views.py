from rest_framework.views import APIView
from datetime import datetime
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError
from .paginators import PostPaginator
from .models import Apply, Comment, Company, Experience, Post, Rating, SavedPost, Token, User, UserProfile, UserRole, Major, Category, Education
from .perms import EduAndExpPerms, OwnerPerms, OwnerPostPerms, PostCreateHirerPerms, RatingPerms
from drf_yasg.utils import swagger_auto_schema

from django.db import DatabaseError, transaction

# Create your views here.
from .serializers import ApplySerializer, CommentSerializer, CompanyAuthSerializer, CompanySerializer, ExperienceProfileSerializer, PostSerializer, SavedPostSerializer, UserProfileSerializer, \
    UserSerializer, CategorySerializer, MajorSerializer, \
    EducationProfileSerializer


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True).select_related()
    serializer_class = CategorySerializer


class MajorViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Major.objects.filter(active=True).select_related()
    serializer_class = MajorSerializer


class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                  generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True).select_related()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['current_user', 'my_profile']:
            return [permissions.IsAuthenticated()]
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @action(methods=['get'], url_path="current-user", detail=False)
    def current_user(self, request):
        return Response(self.serializer_class(request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path="my-profile", detail=False)
    def my_profile(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        return Response(data=(UserProfileSerializer(profile, context={'request': request})).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path="company-profile", detail=True)
    def company_profile(self, request, pk):
        company = Company.objects.get(user_id=pk)
        return Response(data=(UserProfileSerializer(company, context={'request': request})).data,
                        status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_permissions(self):
    #     return [OwnerPerms()]

    def create(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.description = request.data.get(
            'description', profile.description)
        profile.nick_name = request.data.get('nick_name', profile.nick_name)
        try:
            profile.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=UserProfileSerializer(profile, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class EducationProfileViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Education.objects.all()
    serializer_class = EducationProfileSerializer

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return [EduAndExpPerms()]
        return [permissions.IsAuthenticated()]

    def create(self, request):
        user, _ = UserProfile.objects.get_or_create(user=request.user)
        print(user.id)
        print(user)
        degree_name = request.data.get('degree_name')
        university = request.data.get('university_name')
        major_id = request.data.get('major_id')
        start_date = request.data.get('start_date')
        completed = request.data.get('completionDate')
        Cpa = request.data.get('CPA')
        edu = Education(user=user)
        edu.degree_name = degree_name
        edu.university_name = university
        edu.major_id = major_id
        try:

            # start = datetime.strptime(start_date, '%Y-%m-%d')
            edu.start_date = start_date
            # date = datetime.strptime(completed, '%Y-%m-%d')
            edu.completionDate = completed

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        edu.CPA = int(Cpa)
        print(edu)
        try:
            edu.save()
            user.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=EducationProfileSerializer(edu, context={'request': request}).data,
                        status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_200_OK)


class ExperienceProfileViewSet(viewsets.ViewSet,  generics.RetrieveAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Experience.objects.all()
    serializer_class = ExperienceProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return [EduAndExpPerms()]
        return [permissions.IsAuthenticated()]

    def create(self, request):
        user, _ = UserProfile.objects.get_or_create(user=request.user)
        print(user.id)
        print(user)
        title = request.data.get('title')
        company_name = request.data.get('company_name')
        desciption = request.data.get('description')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        exp = Experience(user=user)
        exp.title = title
        exp.company_name = company_name
        exp.description = desciption
        try:
            # start = datetime.strptime(start_date, '%Y-%m-%d')
            exp.start_date = start_date
            # date = datetime.strptime(end_date, '%Y-%m-%d')
            exp.end_date = end_date
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            exp.save()
            user.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=ExperienceProfileSerializer(exp, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class CompanyViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView, generics.UpdateAPIView):
    queryset = Company.objects.filter(active=True).select_related()
    serializer_class = CompanySerializer

    def get_queryset(self):
        com = self.queryset
        keyw = self.request.query_params.get('keyword')
        if keyw:
            com = com.select_related().filter(
                company_name__icontains=keyw)
        return com

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return CompanyAuthSerializer

        return CompanySerializer

    def get_permissions(self):
        if self.action in ['rating', 'create_comment']:
            return [RatingPerms()]
        if self.action in ['update', 'destroy', 'partial_update']:
            return [OwnerPerms()]
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request):
        user = request.user
        company_name = request.data.get('company_name')
        description = request.data.get('description')
        avatar = request.data.get('avatar')
        url = request.data.get('web_url')
        phone = request.data.get('phone')
        email = request.data.get('email')
        com, _ = Company.objects.get_or_create(user=user)
        com.company_name = company_name
        if avatar:
            com.avatar = avatar
        com.description = description
        com.web_url = url
        com.email = email
        com.phone = phone
        try:
            com.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=CompanySerializer(com, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='rating', detail=True)
    def rating(self, request, pk):
        company = self.get_object()
        creator = request.user

        r, _ = Rating.objects.get_or_create(company=company, creator=creator)
        r.rate = request.data.get('rate', 0)
        try:
            r.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=CompanyAuthSerializer(company, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='create-comment', detail=True)
    def create_comment(self, request, pk):
        company = self.get_object()
        creator = request.user
        comment = Comment(creator=creator, company=company)
        content = request.data.get('content')
        if content is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        comment.content = content
        try:
            comment.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data=CommentSerializer(comment, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        company = self.get_object()
        comments = company.comments.select_related(
            'creator').order_by('created_date').reverse()
        if comments is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data=CommentSerializer(comments, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='company-posts', detail=True)
    def company_posts(self, request, pk):
        com = Company.objects.filter(id=pk).first()
        posts = Post.objects.filter(company=com)
        return Response(data=(PostSerializer(posts, many=True, context={'request': request})).data,
                        status=status.HTTP_200_OK)


class PostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                  generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Post.objects.filter(active=True).order_by('created_date')
    serializer_class = PostSerializer
    pagination_class = PostPaginator
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return [OwnerPostPerms()]
        if self.action in ['create', 'my_posts']:
            return [PostCreateHirerPerms()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer_class):
        try:
            company = Company.objects.select_related(
                'user').filter(user=self.request.user).first()
            serializer_class.save(company=company)
        except IntegrityError:
            return Response(data="Post already saved",
                            status=status.HTTP_200_OK)

    def get_queryset(self):
        q = self.queryset

        # tìm kiếm theo title
        keyw = self.request.query_params.get('keyword')
        if keyw:
            q = q.filter(title__icontains=keyw)

        # tìm kiếm theo mã ngành
        majorId = self.request.query_params.get('major_id')
        if majorId:
            q = q.filter(major_id=majorId)

        # tìm kiếm theo địa điểm
        local = self.request.query_params.get('location')
        if local:
            q = q.filter(location__icontains=local)

        fromSala = self.request.query_params.get('from_salary')
        toSala = self.request.query_params.get('to_salary')

        # tìm kiếm theo mức lương lớn hơn fromSala
        if fromSala:
            q = q.filter(from_salary__gt=fromSala)

        # tìm kiếm mức lương bé hơn toSala
        if toSala:
            q = q.filter(to_salary__lt=toSala)

        old = self.request.query_params.get('old')
        if old:
            return q.order_by('created_date')

        return q.order_by('created_date').reverse()

    @swagger_auto_schema(
        operation_description='Get the applies of a job',
        responses={
            status.HTTP_200_OK: ApplySerializer()
        }
    )
    @action(methods=['get'], detail=True, url_path='applies')
    def get_applies(self, request, pk):
        post = self.get_object()
        applies = post.applies.select_related('user').filter(
            active=True).order_by('created_date').reverse()

        kw = request.query_params.get('kw')

        if kw:
            applies = applies.filter(description__icontains=kw)

        return Response(data=ApplySerializer(applies, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='my-posts')
    def my_posts(self, request):
        user = request.user
        com = Company.objects.filter(user=user).first()
        my_posts = Post.objects.filter(company=com)
        return Response(data=PostSerializer(my_posts, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class ApplyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                   generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Apply.objects.all()
    serializer_class = ApplySerializer

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update', 'retrieve', 'my_applies']:
            return [OwnerPerms()]

        return [permissions.IsAuthenticated()]

    # def perform_create(self, serializer_class):
    #     try:
    #         serializer_class.save(user=self.request.user)
    #     except IntegrityError:
    #         return Response(data="You already applied",
    #                         status=status.HTTP_200_OK)
    def create(self, request):
        user = request.user
        description = request.data.get('description')
        CV = request.data.get('CV')
        post = request.data.get('post')
        try:
            apply = Apply(user=user, post_id=post)
            apply.description = description
            if CV:
                apply.CV = CV
            apply.save()
        except:
            return Response(data={'message': "You Already applies"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=ApplySerializer(apply, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='my-applies')
    def my_applies(self, request):
        user = request.user
        my_applies = Apply.objects.select_related('user').filter(user=user)
        return Response(data=ApplySerializer(my_applies, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class MySavedPostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView, generics.CreateAPIView):
    serializer_class = SavedPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SavedPost.objects.select_related('user').filter(user=user)

    def perform_create(self, serializer_class):
        try:
            serializer_class.save(user=self.request.user)
        except IntegrityError:
            return Response(data="Post already saved",
                            status=status.HTTP_200_OK)


class ConfirmUserViewSet(APIView):

    def post(self, request, pk, format=None):
        tokenObj = Token.objects.filter(token=pk).first()

        user = User.objects.filter(id=tokenObj.user.id).first()

        if user:
            user_serializer = UserSerializer(
                user, data={'is_active': True}, partial=True)
            if user_serializer.is_valid(raise_exception=False):
                user_serializer.save()

                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)
