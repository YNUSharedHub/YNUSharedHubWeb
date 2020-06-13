from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import College, Teacher, UserProfile, Course, Resource, Report,Course_Table


class ProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False


class UserProfileAdmin(UserAdmin):
    inlines = [ProfileInline, ]


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name','teacher','lessonsAddress', 'average_grade', 'credit', 'college_id', 'class_id')
    # 过滤器：进行筛选
    list_filter = ['college_id']
    # 搜素
    search_fields = ['name','teacher']


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name','upload_user_id', 'size', 'link', 'upload_time', 'download_count')

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ['name']

class CollegeAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ['name']

class ReportAdmin(admin.ModelAdmin):
    list_display = ('be_reported_resource_id', 'report_user_id', 'report_time', 'already_handle')


admin.site.unregister(User)
admin.site.site_header = "YNUCourseHub"
admin.site.site_title = "YNUCourseHub"
admin.site.register(User, UserProfileAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Teacher,TeacherAdmin)
admin.site.register(College,CollegeAdmin)

# admin.site.register(Course_Table)
