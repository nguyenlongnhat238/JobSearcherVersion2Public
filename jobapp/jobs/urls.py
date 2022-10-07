from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(prefix='categories',
                viewset=views.CategoryViewSet, basename='category')

router.register(prefix='majors', viewset=views.MajorViewSet, basename='major')

router.register(prefix='users', viewset=views.UserViewSet, basename='user')

router.register(prefix="user-profile",
                viewset=views.UserProfileViewSet, basename='user-profile')

router.register(prefix='education-profile',
                viewset=views.EducationProfileViewSet, basename='education-profile')

router.register(prefix='experience-profile',
                viewset=views.ExperienceProfileViewSet, basename='experience')

router.register(prefix='company',
                viewset=views.CompanyViewSet, basename='company')

router.register(prefix='posts', viewset=views.PostViewSet, basename='post')

router.register(prefix='applies', viewset=views.ApplyViewSet, basename='apply')

router.register(prefix='my-saved-posts',
                viewset=views.MySavedPostViewSet, basename='my-saved-posts')


urlpatterns = [
    path('', include(router.urls)),
    path('confirm-user/<str:pk>', views.ConfirmUserViewSet.as_view()),
]
