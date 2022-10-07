from django import forms
from django.contrib import admin
from django.utils.html import mark_safe, format_html
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Company, Experience, Post, Rating, Token, User, UserRole, UserProfile, Education, Category, Major


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['name', 'created_date']
    list_display = ['id', 'name', 'created_date']


class CompanyInline(admin.StackedInline):
    model = Company
    fk_name: 'user'
    extra: 0


class UserAdmin(admin.ModelAdmin):
    search_fields = ['username']
    readonly_fields = ['image_admin']
    list_display = ['username', 'id', 'user_role', 'is_active']
    list_filter = ['user_role']
    inlines = [CompanyInline, ]

    def image_admin(self, obj):
        if obj:
            return mark_safe(
                '<img src="/static/{url}" width="240" />'.format(
                    url=obj.avatar.name)
            )


class PostForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    form = PostForm
    search_fields = ['title', 'id']
    list_display = ['id', 'title',
                    'company_id', 'company_name']
    list_filter = ['company', 'id']

    @admin.display(empty_value='???')
    def company_name(self, obj):
        return obj.company.company_name


class ExperienceProfileInline(admin.StackedInline):
    model = Experience
    fk_name = 'user'
    extra = 0


class EducationProfileInline(admin.StackedInline):
    model = Education
    fk_name = 'user'
    extra = 0


class UserProfileAdmin(admin.ModelAdmin):
    inlines = [EducationProfileInline, ExperienceProfileInline, ]


class UserComapanyAdmin(admin.ModelAdmin):
    inlines = [CompanyInline, ]


class CompanyAdmin(admin.ModelAdmin):
    pass


notifi = Company.objects.filter(active=False).count()
admin.site.site_header = 'Jobs Searcher Project'
admin.site.index_title = 'Management Area'
admin.site.site_title = 'HTML'


admin.site.register(User, UserAdmin)

admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Experience)

admin.site.register(Company, CompanyAdmin)

admin.site.register(Post, PostAdmin)

admin.site.register(UserRole)

admin.site.register(Education)

admin.site.register(Category, CategoryAdmin)

admin.site.register(Major)

admin.site.register(Rating)

admin.site.register(Token)
