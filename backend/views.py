# Create your views here.
import decimal

from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from numpy import unicode

from backend import interface
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .forms import *
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q, Sum
from django.views.generic.base import View
from django.shortcuts import render
from .email_send import *
from .course_crawler import *
from .verify_student import *
from .grades_crawler import *
import requests
import urllib.request
import json
import datetime
from datetime import date

import os
import time

from django.utils.http import urlquote

from backend import notification

url = 'https://ids.ynu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.ynu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.ynu.edu.cn%2Fnew%2Findex.html'
path = 'D:\\只狼\\chromedriver.exe'

def page404(request):
    return


# return HttpResponse(u"page not found: 404")

def home(request):
    return render(request, 'index.html')


# def course(request):
#     return render(request, 'course.html')


# def contact(request):
#     return render(request, 'contact.html')


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


# Register Interface
# REQUIRES: the ajax datatype must be json and the data should be like {'name': value,...}
# MODIFIES: create a new user in database, update tables(mainly auth_user and backend_userprofile)
# EFFECTS: if register success, return a json data {'error': 0};
#          else return a json data {'error': error}, error is a list of error
# URL: /sign/register/
@csrf_exempt
def userRegister(request):
    try:
        if request.method == 'POST':
            data = json.dumps(request.POST)
            data = json.loads(data)
            username = str(data.get('username'))
            password1 = str(data.get('password1'))
            password2 = str(data.get('password2'))
            email = str(data.get('email'))
            gender = str(data.get('gender'))
            nickname = str(data.get('nickname'))
            intro = str(data.get('intro'))
            registerForm = RegisterForm(
                {'username': username, 'password1': password1, 'password2': password2, 'email': email, 'gender': gender,
                 'nickname': nickname, 'intro': intro})
            # print('email: ', email)
            if not registerForm.is_valid():
                return HttpResponse(json.dumps({'error': 201}, cls=ComplexEncoder))

            user = User()
            user.username = username
            user.set_password(password1)
            user.email = email
            # user.is_active = False
            user.save()
            # 用户扩展信息 profile
            profile = UserProfile()
            profile.user_id = user.id  # user_id
            profile.gender = gender
            profile.nickname = nickname
            profile.intro = intro
            profile.college_id = 1
            profile.save()
            # # print(1)
            # 注册成功以后自动进行登录，登录前需要先验证，去掉注释后需要修改your url，HttpResponseRedirect进行页面重定向
            # newUser=auth.authenticate(username=username,password=password1)
            # if newUser is not None:
            #     auth.login(request, newUser)
            #     return HttpResponseRedirect("127.0.0.1:8000")


    # # print('finish send email')
    except Exception as e:
        return HttpResponse(json.dumps({'error': 202}))
    # 发送验证邮件
    # send_register_email(email, "register")
    return HttpResponse(json.dumps({'error': 0}))


# modified by xdt 2017.11.8
# the Interface of search course list by college id
# REQUIRES: the ajax data should be json data {'college_id': class_id}
# MODIFIES: None
# EFFECTS: return json data {'course_info_list': course_info_list}, course_info_list is a list
# URL: /course/college_course/
@csrf_exempt
def course_by_college(request):
    if request.method == "POST":
        data = json.dumps(request.POST)
        data = json.loads(data)
        college_id = int(data.get('college_id'))
        course_info_list = interface.college_course_list(college_id)
        return HttpResponse(json.dumps({'course_info_list': course_info_list}, cls=ComplexEncoder))


# modified by xdt 2017.11.8
# the Interface of search course list by class id
# REQUIRES: the ajax data should be json data {'class_id': class_id}
# MODIFIES: None
# EFFECTS: return json data {'course_info_list': course_info_list}, course_info_list is a list
# URL: /course/classification_course/
@csrf_exempt
def course_by_class(request):
    if request.method == "POST":
        data = json.dumps(request.POST)
        data = json.loads(data)
        class_id = int(data.get('class_id'))
        course_info_list = interface.classification_course_list(class_id)
        return HttpResponse(json.dumps({'course_info_list': course_info_list}, cls=ComplexEncoder))


# Course Information Interface
# REQUIRES: the ajax data should be json data {'course_id': class_id}
# MODIFIES: None
# EFFECTS: return json data {'course_info': course_info}, course_info is a dict
# URL: /course/course_info/
@csrf_exempt
def course_information(request):
    if (request.method == "POST"):
        data = json.dumps(request.POST)
        data = json.loads(data)
        a = request.user.id
        course_id = int(data.get('course_id'))
        course_info = interface.course_information(course_id)
        return HttpResponse(json.dumps({'course_info': course_info}, cls=ComplexEncoder))


# Visit Course Interface
# REQUIRES: the ajax data should be json data {'post_id': post_id}
# MODIFIES: Post.click_count
# EFFECTS: return json data {'click_count': click_count}, click_count is a integer
# URL: /course/click_count/
@csrf_exempt
def refresh_click_post_count(request):
    def refresh(now_time, post_id):
        post = Post.objects.get(id=post_id)
        post.click_count += 1
        post.save()
        request.session.modified = True
        request.session['last_post_click'][post_id] = str(now_time)
        return HttpResponse(json.dumps({'click_count': post.click_count}))

    if (request.method == "POST"):
        data = json.dumps(request.POST)
        data = json.loads(data)
        post_id = int(data.get('post_id'))

        last_post_click_dict = request.session.get('last_post_click')
        now_time = datetime.datetime.now()
        if (last_post_click_dict == None):  # have not clicked any posts
            request.session['last_post_click'] = {}
            return refresh(now_time, post_id)
        else:
            # # print('last_post: ', last_post_click_dict)
            last_post_click = last_post_click_dict.get(str(post_id))
            if (last_post_click != None):  # has clicked the post
                last_click_time = datetime.datetime.strptime(last_post_click[:-7], "%Y-%m-%d %H:%M:%S")
                if (now_time >= last_click_time + datetime.timedelta(hours=24)):
                    return refresh(now_time, post_id)
            else:  # have not clicked the post
                return refresh(now_time, post_id)
        return HttpResponse(json.dumps({'click_count': Post.objects.get(id=post_id).click_count}))


'''
def course_visit_count(request):
    if(request.method == "POST"):
        data = json.dumps(request.POST)
        data = json.loads(data)
        course_id = int(data.get('course_id','0'))
'''


# Visit Course Interface
# REQUIRES: the ajax data should be json data {'course_id': course_id}
# MODIFIES: Course.visit_count
# EFFECTS: return json data {'visit_count': visit_count}, visit_count is a integer
# URL: /course/visit_count/
@csrf_exempt
def refresh_visit_course_count(request):
    def refresh(now_time, course_id):
        course = Course.objects.get(id=course_id)
        course.visit_count += 1
        course.save()
        request.session.modified = True
        request.session['last_view'][course_id] = str(now_time)
        return HttpResponse(json.dumps({'visit_count': course.visit_count}))

    if (request.method == "POST"):
        data = json.dumps(request.POST)
        data = json.loads(data)
        course_id = int(data.get('course_id'))

        last_view_dict = request.session.get('last_view')
        now_time = datetime.datetime.now()
        if (last_view_dict == None):  # have not visited any courses
            request.session['last_view'] = {}
            return refresh(now_time, course_id)
        else:
            # # print(last_view_dict)
            last_view = last_view_dict.get(str(course_id))
            if (last_view != None):  # has visited the course
                last_visit_time = datetime.datetime.strptime(last_view[:-7], "%Y-%m-%d %H:%M:%S")
                if (now_time >= last_visit_time + datetime.timedelta(hours=24)):
                    return refresh(now_time, course_id)
            else:  # have not visited the course
                return refresh(now_time, course_id)
        return HttpResponse(json.dumps({'visit_count': Course.objects.get(id=course_id).visit_count}))


# Resource Download Count Interface
# REQUIRES: the ajax data should be json data {'resource_id': resource_id}
# MODIFIES: Resource.download_id
# EFFECTS: return json data {'download_count': download_count}, download_count is a integer
# URL: /course/course_info/
@csrf_exempt
def refresh_download_resource_count(request):
    def refresh(now_time, resource_id):
        resource = Resource.objects.get(id=resource_id)
        resource.download_count += 1
        resource.save()
        request.session.modified = True
        request.session['last_download'][resource_id] = str(now_time)
        return HttpResponse(json.dumps({'download_count': resource.download_count}))

    if (request.method == "POST"):
        data = json.dumps(request.POST)
        data = json.loads(data)
        resource_id = int(data.get('download_count'))

        last_download_dict = request.session.get('last_download')
        now_time = datetime.datetime.now()
        if (last_download_dict == None):  # have not visited any courses
            request.session['last_download'] = {}
            return refresh(now_time, resource_id)
        else:
            # # print(last_download_dict)
            last_download = last_download_dict.get(str(resource_id))
            if (last_download != None):  # has visited the course
                last_download_time = datetime.datetime.strptime(last_download[:-7], "%Y-%m-%d %H:%M:%S")
                if (now_time >= last_download_time + datetime.timedelta(hours=24)):
                    return refresh(now_time, resource_id)
            else:  # have not visited the course
                return refresh(now_time, resource_id)
        return HttpResponse(json.dumps({'download_count': Resource.objects.get(id=resource_id).download_count}))


# User Information Interface
# REQUIRES: the ajax data should be json data {'username': username}
# MODIFIES: NONE
# EFFECTS: return json data {'user_info': user_info}, user_info is a dict
@csrf_exempt
def user_information(request):
    if (request.method == "POST"):
        # data = json.dumps(request.POST)
        # data = json.loads(request.POST)
        # data = json.loads(request.body.decode())
        # data = request.POST
        if 'username' in request.POST.keys():
            username = str(request.POST.get('username'))
            user_info = interface.user_information_by_username(username)
        elif 'id' in request.POST.keys():
            user_id = str(request.POST.get('id'))
            user_info = interface.user_information_by_id(user_id)
        else:
            return HttpResponse(json.dumps({}))
        # # print("******************")
        # # print(user_info)
        # # print("******************")
        return HttpResponse(json.dumps({'user_info': user_info}, cls=ComplexEncoder))


@csrf_exempt
def get_username(request):
    if (request.method == "POST"):
        user_id = str(request.POST.get('id'))


# Resource Information Interface
# REQUIRES: the ajax data should be json data {'resource_id': resource_id}
# MODIFIES: None
# EFFECTS: return json data {'resource_info': resource_info}, resource_info is a dict
# URL:
@csrf_exempt
def resource_information(request):
    if (request.method == "POST"):
        # data = json.loads(request.POST)
        # data = json.loads(request.body.decode())
        resource_id = int(request.POST.get('resource_id'))
        resource_info = interface.resource_information(resource_id)
        return HttpResponse(json.dumps({'resource_info': resource_info}, cls=ComplexEncoder))


# Course Contribution List Interface
# REQUIRES: the ajax data should be json data {'course_id', course_id}
# MODIFIES: None
# EFFECTS: return data {'contrib_list': contrib_list}
#          contrib_list is a list whose element is tuples like (user_id, total scores),
#          the list is ordered by total scores
# URL:
@csrf_exempt
def course_contrib_list(request):
    if (request.method == "POST"):
        data = json.loads(request.POST)
        # data = json.loads(request.body.decode())
        course_id = int(data.get('course_id'))
        contrib_list = interface.resource_contribution_list(course_id)
        return HttpResponse(json.dumps({'contrib_list': contrib_list}, cls=ComplexEncoder))


# Check User Status Interface
# REQUIRES: POST method
# MODIFIES: None
# EFFECTS: return json data {'is_login': is_login}
#          is_login is True if request.user.is_authenticated(), else False
# URL: /sign/get_user/
@csrf_exempt
def get_user(request):
    if (request.method == "POST"):
        is_login = request.user.is_authenticated
        return HttpResponse(json.dumps({'  in': is_login}, cls=ComplexEncoder))


# rewrite the authenticate method
class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # try authenticate the username or the emial
            user = User.objects.get(
                Q(username=username) | Q(email=username))  # Q offers a '&' operation between two objects
            if (user.check_password(password)):
                return user  # if success, return the user object
        except Exception as e:
            return None  # return None if failed


# Email Check Interface
# URL: /sign/emailcheck/
@csrf_exempt
def email_check(request):
    if (request.method == "POST"):
        user_id = request.user.id
        # print("User:", user_id)
        user = User.objects.get(id=user_id)
        if user is None:
            return HttpResponse(json.dumps({'error': 1}))
        if user.is_superuser:
            return HttpResponse(json.dumps({'error': 2}))
        send_register_email(user.email, "register")
        return HttpResponse(json.dumps({'error': 0}))


# Login Interface
# REQUIRES: the ajax data should be json data {'username':username, 'passward':passward
# MODIFIES: request.user.is_authenticated() == True
# EFFECTS: return json data {'error': error}, if login success, error=0,
#          else error is the error list
# URL: /sign/login/
@csrf_exempt
def userLogin(request):
    if (request.method == "POST"):
        data = json.dumps(request.POST)
        data = json.loads(data)
        # data = json.loads(requset.body.decode())
        username = str(data.get('username'))
        password = str(data.get('password'))

        loginForm = LoginForm({'username': username, 'password': password})

        if loginForm.is_valid():
            cb = CustomBackend()
            # 重写了authenticate方法
            user = cb.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                request.session['username'] = username  # store in session
                # print(json.dumps({'error': 0, 'username': user.username}))
                return HttpResponse(json.dumps({'error': 0, 'username': user.username}))
            else:
                return HttpResponse(json.dumps({'error': 101}))  # username not exists
        else:
            return HttpResponse(json.dumps({'error': 102}, cls=ComplexEncoder))  # password error


# Logout Interface
# REQUIRES: POST method
# MODIFIES: request.user.is_authenticated() == False
# EFFECTS: return json data {'error': error}, if logout success, error=0,
#          else error is the error list
# URL: /sign/login/
@csrf_exempt
def userLogout(request):
    if (request.method == "POST"):
        # error = []
        try:
            ## # print(request.user)
            ## # print(request.user.is_authenticated())
            auth.logout(request)
            # del request.session['username']
            ## # print(request.user)
            ## # print(request.user.is_authenticated())
            return HttpResponse(json.dumps({'error': 0}))
        except Exception as e:
            # error.append(str(e))
            ## # print(error)
            return HttpResponse(json.dumps({'error': 301}))


# use session
@csrf_exempt
def isLoggedIn(request):
    if request.method == "POST":
        # # print(request.environ)
        # # print(request.body)
        user_session = request.session.get('username', default=None)
        # print(request.session.items())
        if user_session is None:
            return HttpResponse(json.dumps(None))

        username = interface.get_username(user_session)
        # # print(username)
        id = User.objects.get(username=username['username']).id
        is_ynu = UserProfile.objects.get(user_id=id).is_ynu
        if(is_ynu=='0'):
            reis_ynu = False
        else:
            reis_ynu = True
        # print(json.dumps({'username': username, 'userid': id, 'is_ynu': reis_ynu}))
        return HttpResponse(json.dumps({'username': username['username'], 'userid': id, 'is_ynu': reis_ynu}))


def http_get(url):
    response = urllib.request.urlopen(url)
    return response.read()


# Course Search Interface(by ohazyi)
# REQUIRES: the ajax data should be json data {'query': query}
# MODIFIES: NONE
# EFFECTS: return data {'query_list': query_list}
#          query_list is a list whose element is dicts like (user_id, total scores),
#          such as {'college_id': 10, 'class_id': 55, 'name': '安卓', 'credit': 5, 'id': 9, 'hours': 10}
#          the list is ordered by id temporaily (can be modified to revelance)
@csrf_exempt
def course_query(request):
    if request.method == "POST":
        data = json.dumps(request.POST)  # new
        data = json.loads(data)
        # data = json.loads(request.body.decode())
        query = str(data.get('keyword'))
        # # print ('query: ' + query)
        # # print(query)
        ans = []
        name_query = Course.objects.filter(Q(name__contains=query))
        if len(name_query)!=0:
            for course in name_query:
                course_info = {}
                course_info['course_name'] = course.name
                course_info['course_id'] = course.id
                course_info['course_academy'] = course.college_id
                course_info['course_hours'] = str(course.hours)
                course_info['course_credit'] = str(course.credit)
                course_info['course_class'] = course.teacher
                ans.append(course_info)
        else:
            code_query = Course.objects.filter(course_code__contains=query)
            if len(name_query) != 0:
                for course in code_query:
                    course_info = {}
                    course_info['course_name'] = course.name
                    course_info['course_id'] = course.id
                    course_info['course_academy'] = course.college_id
                    course_info['course_hours'] = str(course.hours)
                    course_info['course_credit'] = str(course.credit)
                    course_info['course_class'] = course.teacher
                    ans.append(course_info)
            else:
                ans = []
        # print(ans)
        return HttpResponse(json.dumps({'query_list':ans}))
        ## # print(json.dumps({'query_list': query_list}))
        ## # print(json.dumps({'query_list': ans}))


# Course id list(by ohazyi)
# REQUIRES: the ajax data should be json data {'query': query}
# MODIFIES: NONE
# EFFECTS: return data {'resource_id_list': query_list}
#          query_list is a list whose course_id = request.get('id') is dicts like (1, 2, 3, 4, 6)...
# retrun like: {"resource_id_list": [1, 2, 3, 4, 6]}
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
         if isinstance(obj, decimal.Decimal):
            return float(obj)
         return super(DecimalEncoder, self).default(obj)


'{"key1": "string", "key2": 10, "key3": 1.45}'
@csrf_exempt
def resource_id_list(request):
    if (request.method == "POST"):
        data = json.dumps(request.POST)  # new
        data = json.loads(data)
        # data = json.loads(request.body.decode())
        course_id = str(data.get('course_id'))
        # # # print ('course_id: ' + course_id)
        res = interface.resource_courseid_list(course_id)
        return HttpResponse(json.dumps({'resource_id_list': res}, cls=ComplexEncoder))


# Handle the uploaded resource
def handle_upload_resource(f, path):
    t = path.split("/")
    file_name = t[-1]
    t.remove(t[-1])
    t.remove(t[0])
    path = "/".join(t)
    try:
        if (not os.path.exists(path)):
            os.makedirs(path)
        file_name = path + "/" + file_name
        # # print(file_name)
        destination = open(file_name, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
            destination.close()
    except Exception as e:
        print(e)
    return file_name


# Resource Upload Interface
# REQUIRES: request.POST['course_code'] != None && request.POST['only_url'] == True/False && request.FILES['file'] != None ,the uploaded should less than 10MB
# MODIFIES: store the uploaded file to iCourse/media/uploads/%Y/%m && insert a record to backend_resource table in database
# EFFECTS: return json data {'error':error}, if upload success, error = 0, else error = 1
@csrf_exempt
def resourceUpload(request):
    if request.method == 'POST':
        errors = []
        if not request.user.is_authenticated:  # if the user is not authenticated
            return HttpResponse(json.dumps({'error': 1}))
        upload_user_id = request.user.id
        # # print(request.user.id)
        data = request.POST
        intro = str(data.get('intro'))
        # course_id = int(data.get('course_id'))
        course_code = str(data.get('course_code'))
        only_url = str(data.get('only_url'))  # only_url = True 表示只上传了一个链接,该链接应当保存在resource的url字段,link字段应该为None
        if (only_url == 'True' or only_url == 'true'):
            only_url = True
        elif (only_url == 'False' or only_url == 'false'):
            only_url = False
        else:
            return HttpResponse(json.dumps({'error': 1}))
        if (only_url):
            url = str(data.get('url'))
            name = str(data.get('name'))
            size = 0
            RUForm = ResourceUploadForm(
                {'name': name, 'size': size, 'upload_user_id': upload_user_id, 'course_code': course_code})
            if RUForm.is_valid():
                resource_up = Resource()
                resource_up.only_url = True
                resource_up.name = name
                resource_up.size = size  # bytes
                resource_up.intro = intro
                resource_up.url = url
                resource_up.course_code = course_code
                resource_up.upload_user_id = upload_user_id
                resource_up.save()
                return HttpResponse(json.dumps({'error': 0}))
            else:
                errors.extend(RUForm.errors.values())
                return HttpResponse(json.dumps({'error': 1}))
        else:
            name = str(request.FILES['file'].name)
            size = int(request.FILES['file'].size)
            RUForm = ResourceUploadForm(
                {'name': name, 'size': size, 'upload_user_id': upload_user_id, 'course_id': course_code})
            if RUForm.is_valid():
                resource_up = Resource()
                resource_up.only_url = False
                resource_up.name = name
                resource_up.link = request.FILES['file']
                resource_up.size = size
                resource_up.intro = intro
                resource_up.course_code = course_code
                resource_up.upload_user_id = upload_user_id
                resource_up.save()
                handle_upload_resource(request.FILES['file'], resource_up.link.url)
                return HttpResponse(json.dumps({'error': 0}))
            else:
                errors.extend(RUForm.errors.values())
                return HttpResponse(json.dumps({'error': 1}))


# Download Interface
# REQUIRES: GET method
# MODIFIES: None
# EFFECTS: return a StreamingHttpResponse if success
# URL: /download/(\d+)/, (\d+) is resource_id
def download(request, resource_id):  # 2 parameters
    if (request.method == "GET"):
        # alpha阶段暂时不实现下载表的写入
        '''
        user_id = request.user.id
        resource_id = int(data.get('resource_id'))
        download_record = R_Resource_User_Download.objects.create(user_id=user_id, resource_id=resource_id)
        download_record.save()
        '''
        resource = Resource.objects.get(id=resource_id)
        resource.download_count += 1  # 下载量+1
        resource.save()
        if (resource.only_url):  # 若仅保存了一个链接
            return HttpResponse(resource.url)
        link = resource.link.url
        real_name = resource.name
        t = link.split("/")
        file_name = t[-1]
        t.remove(t[-1])
        t.remove(t[0])
        file_path = "/".join(t)

        def file_iterator(file_name, file_path, chunk_size=512):
            path = file_path + "/" + file_name
            with open(path, 'rb') as f:  # must use 'rb'
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        try:
            response = StreamingHttpResponse(file_iterator(file_name, file_path))
            response['Content-Type'] = 'application/octet-stream'
            flag = False
            for ch in real_name:
                if (ord(ch) > 127):
                    flag = True
            if (flag):
                response['Content-Disposition'] = 'attachment;filename="{0}"'.format(urlquote(real_name))
            else:
                response['Content-Disposition'] = 'attachment;filename="{0}"'.format(
                    real_name)  # display the real_name of the file when user download it
            ## # print(response)
        except Exception as e:
            ## # print(e)
            return HttpResponse("未找到该文件")
        return response


# Latest Resource Information list
@csrf_exempt
def latest_resource_info(request):
    if (request.method == 'POST'):
        # data = json.loads(request.POST)
        course_id = int(request.POST.get('course_id'))
        number = int(request.POST.get('number'))
        result = interface.resource_information_list(course_id, number)
        return HttpResponse(json.dumps({'result': result}))


# Repost Interface
# REQUIRES: POST method, only anthenticated user can report, need {'be_reported_resource_id': be_reported_resource_id}
# MODIFIES: insert a record in backend_report table in database
# EFFECTS: if success, return {'error': 0}, else return {'error': 1}
# URL: 暂时未定
@csrf_exempt
def user_report(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({'error': 1}))
        be_reported_resource_id = request.POST.get('be_reported_resource_id')
        report_user_id = request.user.id
        report_content = request.POST.get('report_content', "用户未填写举报理由")
        report = Report.objects.create(report_user_id=report_user_id, be_reported_resource_id=be_reported_resource_id,
                                       report_content=report_content)
        report.save()
        return HttpResponse(json.dumps({'error': 0}))


# User Information Modify Interface
# REQUIRES: need {'nickname':nickname, 'gender':gender, 'intro':intro, 'college_id':college_id}
# MODIFIES: modify user information in backend_userprofile
# EFFECTS: if success, return {'error': 0}, else return {'error': 1}
# URL:/user/modify/info/
@csrf_exempt
def user_modify_info(request):
    errors = []
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({'error': 1}))
        # # print(request.POST)
        nickname = str(request.POST.get('nickname'))
        gender = str(request.POST.get('gender'))
        intro = str(request.POST.get('intro'))
        college_id = request.POST.get('college_id')
        UIMForm = UserInfoModifyForm({'nickname': nickname, 'gender': gender, 'intro': intro, 'college_id': college_id})

        if UIMForm.is_valid():
            userprofile = UserProfile.objects.get(user_id=request.user.id)
            userprofile.nickname = nickname
            userprofile.gender = gender
            userprofile.intro = intro
            userprofile.college_id = college_id
            userprofile.save()
            # # print('Modify Success')
            return HttpResponse(json.dumps({'error': 0}))
        else:
            errors.extend(UIMForm.errors.values())
            # # print(errors)     
            return HttpResponse(json.dumps({'error': 1}))


@csrf_exempt
def ip_record(request):
    if (request.method == 'POST'):
        if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
            # # print('ip:', ip)
        interface.refresh_ip_visit_info(str(ip))
        # print(ip)
        return HttpResponse(json.dumps({'result': 0}))


# Publish Post Interface
# URL: /post/posting/publish/
@csrf_exempt
def posting_publish(request):
    errors = []
    if (request.method == 'POST'):
        data = request.POST
        course_id = int(data.get('course_id'))
        category = int(data.get('category'))
        title = str(data.get('title'))
        content = str(data.get('content'))
        user_id = request.user.id
        editor = int(data.get('editor'))
        intro = str(data.get('intro'))
        post_form = PostForm({'title': title, 'course_id': course_id, 'category': category})
        if (post_form.is_valid()):
            post = Post()
            post.title = title
            post.course_id = course_id
            post.category = category
            post.main_follow_id = -1;
            post.intro = intro;
            # # print("intro", intro)
            post.save()
        else:
            errors.extend(post_form.errors.values())
            # # print(errors)
            return HttpResponse(json.dumps({'error': 1}))
        follow_form = FollowForm({'post_id': post.id, 'user_id': user_id, 'content': content, 'editor': editor})
        # # print(post.id,user_id,content,editor)
        if (follow_form.is_valid()):
            follow = Follow()
            follow.post_id = post.id
            follow.user_id = user_id
            follow.content = content
            follow.editor = editor
            follow.is_main = True
            follow.save()
            post.main_follow_id = follow.id  # renew post.main_follow_id
            post.save()
        else:
            errors.extend(follow_form.errors.values())
            # # print(errors)
            post.delete()
            return HttpResponse(json.dumps({'error': 1}))
        return HttpResponse(json.dumps({'error': 0}))


# Publish Follow Interface
# URL: /post/follow/publish/
@csrf_exempt
def follow_publish(request):
    if (request.method == 'POST'):
        data = request.POST
        post_id = int(data.get('post_id'))
        content = str(data.get('content'))
        user_id = request.user.id
        editor = int(data.get('editor'))
        # published?
        follow_form = FollowForm({'post_id': post_id, 'user_id': user_id, 'content': content, 'editor': editor})
        if (follow_form.is_valid()):
            result = Follow.objects.filter(post_id=post_id, user_id=user_id)
            if (result.count() > 0):  # if(len(result) > 0):
                return HttpResponse(json.dumps({'error': 2}))
            follow = Follow()
            follow.post_id = post_id
            follow.user_id = user_id
            follow.content = content
            follow.editor = editor
            follow.is_main = False
            follow.save()
            post = Post.objects.get(id=post_id)  # renew post.follow_count
            post.follow_count += 1
            post.update_time = datetime.datetime.now()
            post.save()
        else:
            return HttpResponse(json.dumps({'error': 1}))
        return HttpResponse(json.dumps({'error': 0}))


# Edit Follow Interface
# URL: /post/follow/edit/
@csrf_exempt
def follow_edit(request):
    if (request.method == 'POST'):
        data = request.POST
        post_id = int(data.get('post_id'))
        content = str(data.get('content'))
        user_id = request.user.id
        follow = Follow.objects.get(post_id=post_id, user_id=user_id)
        if (follow == None):  # not found
            return HttpResponse(json.dumps({'error': 2}))
        # published?
        follow_form = FollowForm({'post_id': post_id, 'user_id': user_id, 'content': content, 'editor': follow.editor})
        if (follow_form.is_valid()):
            follow.content = content
            follow.edit_time = datetime.datetime.now()
            follow.save()
        else:
            return HttpResponse(json.dumps({'error': 1}))
        return HttpResponse(json.dumps({'error': 0}))


# Publish Comment Interface
# URL: /post/comment/publish/
@csrf_exempt
def comment_publish(request):
    if (request.method == 'POST'):
        data = request.POST
        user_id = request.user.id
        follow_id = int(data.get('follow_id'))
        to_comment_id = int(data.get('to_comment_id'))
        content = str(data.get('content'))
        follow_comment_form = FollowCommentForm({'user_id': user_id, 'follow_id': follow_id, 'content': content})
        if (follow_comment_form.is_valid()):
            follow_comment = Follow_Comment()
            follow_comment.user_id = user_id
            follow_comment.follow_id = follow_id
            follow_comment.to_comment_id = to_comment_id
            follow_comment.content = content
            follow_comment.save()
            follow = Follow.objects.get(id=follow_id)  # renew follow.comment_count
            follow.comment_count += 1
            follow.save()
        else:
            return HttpResponse(json.dumps({'error': 1}))
        return HttpResponse(json.dumps({'error': 0}))


# Follow Evaluate Interface
# URL: /post/follow/evaluate
@csrf_exempt
def follow_evaluate(request):
    if (request.method == 'POST'):
        data = request.POST
        user_id = request.user.id
        follow_id = int(data.get('follow_id'))
        grade = int(data.get('grade'))
        follow_evaluation_form = FollowEvaluationForm({'user_id': user_id, 'follow_id': follow_id, 'grade': grade})
        if (follow_evaluation_form.is_valid()):
            result = Follow_Evaluation.objects.filter(user_id=user_id, follow_id=follow_id)
            if (result.count() > 0):  # if the user has evaluated the follow #if(len(result) > 0):
                return HttpResponse(json.dumps({'error': 1}))
            else:
                follow_evaluation = Follow_Evaluation()
                follow_evaluation.user_id = user_id
                follow_evaluation.follow_id = follow_id
                follow_evaluation.grade = grade
                follow_evaluation.save()
                follow = Follow.objects.get(id=follow_id)  # renew follow pos_eva_count or neg_eav_count
                if (grade == 1):
                    follow.pos_eva_count += 1
                else:  # grade == -1
                    follow.neg_eva_count += 1
                follow.save()
        else:
            return HttpResponse(json.dumps({'error': 1}))
        return HttpResponse(json.dumps({'error': 0}))


# Get Post Id List Interface
# URL: /post/id/list/
@csrf_exempt
def post_id_list(request):
    if (request.method == 'POST'):
        course_id = int(request.POST.get('course_id'))
        id_list = list(Post.objects.filter(course_id=course_id).order_by('-update_time').values_list('id', flat=True))
        return HttpResponse(json.dumps({'id_list': id_list}))


# Post Information List Interface
# URL: /post/information/list/
@csrf_exempt
def post_infor_list(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        id_list = data.get('id_list')
        ## # print(id_list)
        if (',' in id_list):
            id_list = id_list[1:-1].split(',')
        else:
            id_list = [id_list[1:-1]]
        ## # print(id_list)
        get_content = str(data.get('get_content'))
        get_grade = str(data.get('get_grade'))
        get_follow_count = str(data.get('get_follow_count'))
        if (get_content == 'True' or get_content == 'true'):
            get_content = True
        elif (get_content == 'False' or get_content == 'false'):
            get_content = False
        else:
            return HttpResponse(json.dumps({'error': 1}))
        if (get_grade == 'True' or get_grade == 'true'):
            get_grade = True
        elif (get_grade == 'False' or get_grade == 'false'):
            get_grade = False
        else:
            return HttpResponse(json.dumps({'error': 1}))
        if (get_follow_count == 'True' or get_follow_count == 'true'):
            get_follow_count = True
        elif (get_follow_count == 'False' or get_follow_count == 'false'):
            get_follow_count = False
        else:
            return HttpResponse(json.dumps({'error': 1}))
        info_list = []
        for item in id_list:
            item = int(item)
            result = Post.objects.filter(id=item)
            if (result.count() != 1):  # if(len(result) != 1):
                # error
                continue
            post = result.values('course_id', 'title', 'category', 'click_count', 'update_time', 'follow_count',
                                 'main_follow_id', 'intro')[0]
            post['grade_sum'] = Follow.objects.filter(post_id=item).aggregate(grade_sum=Sum('pos_eva_count'))[
                'grade_sum']
            main_follow = Follow.objects.get(id=post['main_follow_id'])
            post['user_id'] = main_follow.user_id
            post['content'] = main_follow.content
            # # # print(main_follow.content)
            post['user_name'] = User.objects.get(id=post['user_id']).username
            post['course_name'] = Course.objects.get(id=post['course_id']).name
            # post['update_time'] = '2017-11-18'
            info_list.append(post)
        return HttpResponse(json.dumps({'info_list': info_list}, cls=ComplexEncoder))


# Get Follow Id List Interface
# URL: /follow/id/list/
@csrf_exempt
def follow_id_list(request):
    if (request.method == 'POST'):
        post_id = int(request.POST.get('post_id'))
        # # print(post_id)
        result = Post.objects.filter(id=post_id)
        if (result.count() != 1):  # if(len(result) != 1):
            return HttpResponse(json.dumps({'main_id': -1, 'id_list': []}))
        main_id = result[0].main_follow_id
        # # print(main_id)
        id_list = list(
            Follow.objects.filter(post_id=post_id).order_by('-pos_eva_count', 'neg_eva_count').values_list('id',
                                                                                                           flat=True))
        id_list.remove(main_id)
        return HttpResponse(json.dumps({'main_id': main_id, 'id_list': id_list}))


# Follow Information List Interface
# URL: /follow/info/list/
@csrf_exempt
def follow_info_list(request):
    if request.method == 'POST':
        data = json.dumps(request.POST)
        data = json.loads(data)
        id_list = data.get('id_list')
        # # print(id_list)
        if (',' in id_list):
            id_list = id_list[1:-1].split(',')
        else:
            id_list = [id_list[1:-1]]
        # # print(id_list)
        cur_user_id = request.user.id
        info_list = []
        for item in id_list:
            item = int(item)
            result = Follow.objects.filter(id=item)
            # print(result[0])
            if (result.count() != 1):  # if(len(result) != 1):
                # error
                continue
            follow = result.values('user_id', 'post_time', 'edit_time', 'content', 'pos_eva_count', 'neg_eva_count')[0]
            follow['username'] = User.objects.get(id=follow['user_id']).username
            follow['self_intro'] = UserProfile.objects.get(user_id=follow['user_id']).intro
            # print(follow)
            if follow['user_id'] == cur_user_id:
                follow['is_poster'] = True
            else:
                follow['is_poster'] = False
            if cur_user_id == None:
                follow['evaluated_grade'] = 0
            else:
                result = Follow_Evaluation.objects.filter(user_id=cur_user_id, follow_id=item).values_list('grade',
                                                                                                           flat=True)
                if result.count() == 0:  # if(len(result) == 0):
                    follow['evaluated_grade'] = 0
                else:
                    follow['evaluated_grade'] = result[0]
            info_list.append(follow)
            # # # print(info_list)
        return HttpResponse(json.dumps({'info_list': info_list}, cls=ComplexEncoder))


# get follow content by user_id and post_id
# URL: /follow/get/userpost/
@csrf_exempt
def userid_postid_get_follow(request):
    if (request.method == 'POST'):
        data = request.POST
        post_id = int(data.get('post_id'))
        user_id = request.user.id
        if (user_id == None):
            # # print("NNNNNNNNNNNNNONE")
            return HttpResponse(json.dumps({'content': '', 'editor': -1}))
        result = Follow.objects.filter(post_id=post_id, user_id=user_id).values('content', 'editor')
        if (result.count() != 1):  # if(len(result) != 1):
            # error
            # # print("NNNNNNNNNNNNNNNOT FOUND")
            return HttpResponse(json.dumps({'content': '', 'editor': -1}))
        # # print("FFFFFFFFFFFFFFFFFFFOUND")
        return HttpResponse(json.dumps({'content': result[0]['content'], 'editor': result[0]['editor']}))


# Get Comment Id List Interface
# URL: /comment/id/list/
@csrf_exempt
def comment_id_list(request):
    if (request.method == 'POST'):
        follow_id = int(request.POST.get('follow_id'))
        id_list = list(
            Follow_Comment.objects.filter(follow_id=follow_id).order_by('-post_time').values_list('id', flat=True))
        return HttpResponse(json.dumps({'id_list': id_list}))


# Comment Information List Interface
# URL: /comment/info/list/
@csrf_exempt
def comment_info_list(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        id_list = data.get('id_list')
        if (',' in id_list):
            id_list = id_list[1:-1].split(',')
        else:
            id_list = [id_list[1:-1]]
        info_list = []
        for item in id_list:
            item = int(item)
            result = Follow_Comment.objects.filter(id=item)
            if (result.count() != 1):  # if(len(result) != 1):
                # error
                continue;
            follow_comment = result.values('user_id', 'to_comment_id', 'post_time', 'content')[0]
            follow_comment['username'] = User.objects.get(id=follow_comment['user_id']).username
            if (follow_comment['to_comment_id'] == -1):
                follow_comment['to_user_id'] = -1
                follow_comment['to_username'] = ''
            else:
                follow_comment['to_user_id'] = Follow_Comment.objects.get(id=follow_comment['to_comment_id']).user_id
                follow_comment['to_username'] = User.objects.get(id=follow_comment['to_user_id']).username
            info_list.append(follow_comment)
        return HttpResponse(json.dumps({'info_list': info_list}, cls=ComplexEncoder))


# get top list_len post id list order by update time
# URL: /post/latest/idlist/
@csrf_exempt
def post_id_list_by_update_time(request):
    if (request.method == 'POST'):
        list_len = int(request.POST.get('list_len'))
        college_id = int(request.POST.get('college_id'))
        if (college_id == -1):
            result = Post.objects.all().order_by('-update_time').values_list('id', flat=True)
            id_list = []
            count = 0
            for i in result:
                id_list.append(i)
                count = count + 1
                if (count == list_len):
                    break
            return HttpResponse(json.dumps({'id_list': id_list}))
        else:
            result = Post.objects.all().order_by('-update_time').values('id', 'course_id')
            course_list = Course.objects.filter(college_id=college_id).values_list('id', flat=True)
            id_list = []
            for item in result:
                if (item['course_id'] in course_list):
                    id_list.append(item['id'])
            return HttpResponse(json.dumps({'id_list': id_list}))


# get top list_len post id list order by click count
# URL: /post/hot/idlist/
@csrf_exempt
def post_id_list_by_click_count(request):
    if (request.method == 'POST'):
        list_len = int(request.POST.get('list_len'))
        college_id = int(request.POST.get('college_id'))
        if (college_id == -1):
            result = Post.objects.all().order_by('-click_count', '-update_time').values_list('id', flat=True)
            id_list = []
            count = 0
            for i in result:
                id_list.append(i)
                count = count + 1
                if (count == list_len):
                    break
            return HttpResponse(json.dumps({'id_list': id_list}))
        else:
            result = Post.objects.all().order_by('-click_count', '-update_time').values('id', 'course_id')
            course_list = Course.objects.filter(college_id=college_id).values_list('id', flat=True)
            id_list = []
            for item in result:
                if (item['course_id'] in course_list):
                    id_list.append(item['id'])
            return HttpResponse(json.dumps({'id_list': id_list}))


# ---------------------------------------------------------------
# 根据用户对资源的打分进行数据更新
# REQUIRES:      变量名|类型|说明
#          resource_id|int|资源id
#              user_id|int|用户id
#                grade|int|评分，0~5
# MODIFIES: None
# EFFECTS: 更新到数据库backend_evualtion
# modified by xindetai 12.8
@csrf_exempt
def resource_evaluate(request):  # resource_id, user_id, grade:
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        resource_id = str(data.get('resource_id'))
        user_id = str(request.user.id)
        grade = int(data.get('grade'))

        # # print ('resource_id: ' + resource_id + 'user_id: '+ user_id + 'grade: ' +str(grade))
        if (grade >= 1 and grade <= 5):  # 评分必须在1-5之间
            eva = Resource_Evaluation()
            eva.resource_id = resource_id
            eva.user_id = user_id
            eva.grade = grade
            eva.save()
            return HttpResponse(json.dumps({'error': 0}))
        return HttpResponse(json.dumps({'error': 1}))


# ---------------------------------------------------------------
# 查看用户对资源的评分情况，返回两个值，一个是查看这个资源的平均评分，一个是用户给这个资源的评分
# REQUIRES:      变量名|类型|说明
#          resource_id|int|资源id
#              user_id|int|用户id
# MODIFIES: None
# EFFECTS: 返回两个值：1、avg_grade即评价平均分，浮点型(float), 没有一个人评价就是-1
#                    2、user_grade，用户给予的评价，int型号，未评价返回-1
# URL:/resource/evaluation/grade/count/
# modified by xdt 12.9
@csrf_exempt
def resource_evaluation_grade_count(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        resource_id = str(data.get('resource_id'))
        user_id = request.user.id
        result = Resource_Evaluation.objects.filter(resource_id=resource_id, user_id=user_id)

        user_grade = -1  # 没有人评价，个人评价值默认为-1
        if (result.count() != 0):  # if (len(result) != 0):
            user_grade = result[0].grade  # 每个人只允许评价一次，即防止刷评价现象，所以只要去除result[0]

        result2 = Resource_Evaluation.objects.filter(resource_id=resource_id)

        tot_grade = 0
        avg_grade = -1  # 没有人评价，平均值默认值为-1
        if (result2.count() != 0):  # if (len(result2) != 0):
            for r in result2:  # for i in range(0, len(result2)):
                tot_grade += r.grade
                avg_grade = float(tot_grade) / float(result2.count())  # len(result2)
        # # print("tot_grade = ",tot_grade,"avg_grade = ", avg_grade)
        return HttpResponse(json.dumps(
            {'avg_grade': avg_grade, 'user_grade': user_grade, 'grade_count': result2.count()}))  # len(result2)


# 求某个资源的评分的平均分
def avg_score(resource_id):
    result2 = Resource_Evaluation.objects.filter(resource_id=resource_id)
    tot_grade = 0
    avg_grade = -1  # 没有人评价，平均值默认值为-1
    if (result2.count() != 0):  # len(result2)
        for r in result2:  # len(result2)
            tot_grade += r.grade
            avg_grade = float(tot_grade) / float(result2.count())  # float(len(result2)
    # # print("tot_grade = ",tot_grade,"avg_grade = ", avg_grade)
    return avg_grade


# ---------------------------------------------------------------
# 获取课程贡献分列表
# REQUIRES:      变量名|类型|说明
#            course_id|int|课程id
#          资源id必须是存在资源的id，否则返回error:1
# MODIFIES: None
# EFFECTS:
#        返回contri_list	list[dict{}]	课程贡献度字典，按照contri从高到低排序
#        字典包括：
#        变量名|类型|说明
#        :-:|:-:|:-:
#        user_id|int|用户id
#        username|str|用户名
#        contri|float|贡献度（保留一位小数）
# 某用户在某一课程下贡献度计算公式：（即同一用户在不同课程下贡献度可能不同）
# 资源贡献度 = 上传资源数∑(下载量*评分平均值/10)
# 论坛贡献度 = 发布帖子数∑(点击量/10) + 发布跟帖数∑((赞同数2) / (赞同数+反对数))
# 总贡献度 = 资源贡献度 + 论坛贡献度
# url: /course/contri/
# modified by xindetai 12.9
@csrf_exempt
def course_contri_list(request):
    if (request.method == 'POST'):

        #        time1 = time.clock()
        #        # print("@@!##@$E")
        data = json.dumps(request.POST)
        data = json.loads(data)

        course_id = str(data.get('course_id'))

        c = interface.course_information(course_id)
        if (not c):  # 如果c为空，代表不存在这样id的课程
            return HttpResponse(json.dumps({'error': 1}))
        course_code = c["course_code"]

        users = User.objects.filter()
        #        time2 = time.clock()
        #        # print('T2', time2-time1)

        dict = {}
        users_cnt = User.objects.filter().count()
        users_cnt = users[users_cnt - 1].id

        for i in range(1, users_cnt + 1):
            dict[i] = 0

        resources = Resource.objects.filter(course_code=course_code)
        for r in resources:  # 遍历所有资源 #len(resources)
            download_count = r.download_count
            grade = avg_score(r.id)
            if (grade == -1):
                grade = 5  # 没有人评价，评分就设置为5
            contrib_r = float(download_count) * float(grade) / 10.0
            dict[r.upload_user_id] = dict[r.upload_user_id] + contrib_r  # dict[resources[i].upload_user_id] + contrib_r
        posts = Post.objects.filter(course_id=course_id)

        for p in posts:  # 遍历所有帖子 #len(posts)
            click_count = p.click_count
            tmp = Follow.objects.filter(id=p.main_follow_id)

            post_user_id = tmp[0].user_id
            if (not post_user_id in dict):
                dict[post_user_id] = float(click_count / 10.0)
            else:
                dict[post_user_id] = dict[post_user_id] + float(click_count / 10.0)

            posts_follow = Follow.objects.filter(post_id=p.id)
            for f in posts_follow:  # 遍历该帖子下的所有跟帖 #len(posts_follow
                pos_eva_count = f.pos_eva_count
                neg_eav_count = f.neg_eva_count
                if ((pos_eva_count + neg_eav_count) == 0):
                    continue
                if (not f.user_id in dict):
                    dict[f.user_id] = float(pos_eva_count * pos_eva_count / (pos_eva_count + neg_eav_count))
                else:
                    dict[f.user_id] = dict[f.user_id] + float(2.0 * (pos_eva_count) / (pos_eva_count + neg_eav_count))

        ans = sorted(dict.items(), key=lambda item: item[1], reverse=True)
        dict_list = []

        for id, score in ans:
            if (score == 0):
                continue
            dict_tmp = {}
            u_name = ""
            res = User.objects.filter(id=id)

            if (len(res) != 0):
                u_name = res[0].username
            if (not u_name):  # 返回的是”“ 即不存在该用户，跳过
                continue
            dict_tmp["username"] = u_name
            dict_tmp["user_id"] = id
            dict_tmp["contri"] = round(score, 1)

            dict_list.append(dict_tmp)

        # print(dict_list)

        #        time3 = time.clock()
        #        # print('T3', time3-time1)
        return HttpResponse(json.dumps({'contri_list': dict_list}, cls=ComplexEncoder))


# ---------------------------------------------------------------
# 获取某一类别资源
# REQUIRES:      变量名|类型|说明
#            course_id|int|课程id
#          资源id必须是存在资源的id，否则返回error:1
#           type|int|资源类别: ppt、doc(txt)、pdf、pict、other、all
# MODIFIES: None
# EFFECTS: 返回resource\_class\_id\_list|list[int]|该课程下的资源id列表
@csrf_exempt
def resource_class_id_list(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        course_id = str(data.get('course_id'))
        type = str(data.get('type'))

        c = interface.course_information(course_id)
        if (not c):  # 如果c为空，代表不存在这样id的课程
            return HttpResponse(json.dumps({'error': 1}))

        course_code = c["course_code"]

        resources = Resource.objects.filter(course_code=course_code)
        ans = []
        for r in resources:  # len(resources)
            name = r.name
            pos = name.rfind('.')
            if (pos == -1):
                continue
            if (name[pos + 1:len(name)] == type):
                ans.append(r.id)
        return HttpResponse(json.dumps({'resource_class_id_list': ans}, cls=ComplexEncoder))


@csrf_exempt
def resource_other_id_list(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        course_id = str(data.get('course_id'))
        type_list = ['pdf', 'doc', 'docx', 'zip', '7z', 'rar', 'txt', 'ppt', 'pptx']
        c = interface.course_information(course_id)
        if (not c):  # 如果c为空，代表不存在这样id的课程
            return HttpResponse(json.dumps({'error': 1}))

        course_code = c["course_code"]

        resources = Resource.objects.filter(course_code=course_code)
        ans = []
        for r in resources:  # len(resources)
            name = r.name
            pos = name.rfind('.')
            if (pos == -1):
                continue
            is_other = True
            for type in type_list:
                if (name[pos + 1:len(name)] == type):
                    is_other = False
                    break
            if (is_other):
                ans.append(r.id)
        return HttpResponse(json.dumps({'resource_class_id_list': ans}, cls=ComplexEncoder))


# ---------------------------------------------------------------
# 根据课程列别获取课程
# REQUIRES:      变量名|类型|说明
#              type|string|课程类别:'工程基础类','数学与自然科学类','语言类','博雅类','核心通识类','体育类','一般通识类','核心专业类','一般专业类'
#               必须是这9个之一，否则返回error:1
# MODIFIES: None
# EFFECTS: 返回course\_type\_list|list[int]|该类别下的课程的list,其中每个都是一个字典，存着课程的信息
#          query_list is a list whose element is dicts like (user_id, total scores),
#          such as {'credit': Decimal('3.0'), 'class_id': 1, 'teacher': '杨振宇', 'name': '弹性力学*(全汉语)', 'college_id': 5, 'hours': None, 'visit_count': 0, 'id': 1733, 'course_code': 'B3B05314B'}
@csrf_exempt
def course_type_list(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        type = str(data.get('type'))

        dict = {'工程基础类': 1, '数学与自然科学类': 2, '语言类': 3, '博雅类': 4, '核心通识类': 5, '体育类': 6, '一般通识类': 7, '核心专业类': 8, '一般专业类': 9}
        if (not type in dict):
            return HttpResponse(json.dumps({'error': 1}))
        type_id = dict[type]

        courses = Course.objects.filter(class_id=type_id)
        ans = []
        for c in courses:  # len(courses)
            course_info = {}
            course_info["id"] = c.id
            course_info["name"] = c.name
            course_info["college_id"] = c.college_id
            course_info["class_id"] = c.class_id
            course_info["hours"] = c.hours
            course_info["course_code"] = c.course_code
            course_info["visit_count"] = c.visit_count
            course_info["teacher"] = c.teacher
            course_info["credit"] = float(c.credit)
            ans.append(course_info)

        # # print(ans)
        return HttpResponse(json.dumps({'course_type_list': ans}, cls=ComplexEncoder))


# ---------------------------------------------------------------
# 资源收藏
# REQUIRES:      变量名|类型|说明
#          resource_id|int|资源id
#              user_id|int|用户id
# MODIFIES: None
# EFFECTS: error|int|0 1:失败
@csrf_exempt
def resource_like(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        resource_id = str(data.get('resource_id'))
        user_id = str(data.get('user_id'))

        likes = R_Resource_User_Like.objects.filter(resource_id=resource_id,
                                                    user_id=user_id)  # filter相当于SQL中的WHERE，可设置条件过滤结果
        if (likes.count() > 0):  # 之前喜欢过，报错 #len(likes)
            return HttpResponse(json.dumps({'error': 1}))

        like = R_Resource_User_Like()
        like.user_id = user_id
        like.resource_id = resource_id
        like.save()
        return HttpResponse(json.dumps({'error': 0}))


# ---------------------------------------------------------------
# 获取资源收藏情况
# REQUIRES:         变量名|类型|说明
#             resource_id|int|资源id
#                 user_id|int|用户id
# MODIFIES: None
# EFFECTS:  like_resource|int|收藏数
#                    like|int|0:未收藏 1:已收藏
@csrf_exempt
def resource_like_count(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        resource_id = str(data.get('resource_id'))
        user_id = str(data.get('user_id'))

        likes = R_Resource_User_Like.objects.filter(resource_id=resource_id)
        ans_likes = likes.count()  # len(likes)
        likes = R_Resource_User_Like.objects.filter(resource_id=resource_id, user_id=user_id)
        user_like = int(likes.count() > 0)  # len(likes)
        return HttpResponse(json.dumps({'like_resource': ans_likes, 'like': user_like}))


# ---------------------------------------------------------------
# 资源收藏
# REQUIRES:      变量名|类型|说明
#                course_id|int|课程id
#                user_id|int|用户id
# MODIFIES: None
# EFFECTS: error|int|0 1:失败
@csrf_exempt
def course_like(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        course_id = str(data.get('course_id'))
        user_id = str(request.user.id)

        likes = R_Course_User_Like.objects.filter(course_id=course_id, user_id=user_id)  # filter相当于SQL中的WHERE，可设置条件过滤结果
        if (likes.count() > 0):  # 之前喜欢过，报错 #len(likes)
            return HttpResponse(json.dumps({'error': 1}))

        like = R_Course_User_Like()
        like.user_id = user_id
        like.course_id = course_id
        like.save()
        return HttpResponse(json.dumps({'error': 0}))


# ---------------------------------------------------------------
# 课程取消收藏
# REQUIRES:         变量名|类型|说明
#               course_id|int|课程id
#                 user_id|int|用户id
# MODIFIES: None
# EFFECTS:          error|int|0 1:失败
@csrf_exempt
def course_cancel_like(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        course_id = str(data.get('course_id'))
        user_id = str(request.user.id)

        likes = R_Course_User_Like.objects.filter(course_id=course_id, user_id=user_id)  # filter相当于SQL中的WHERE，可设置条件过滤结果
        if (likes.count() == 0):  # len(likes)
            return HttpResponse(json.dumps({'error': 1}))

        like = R_Course_User_Like.objects.get(course_id=course_id, user_id=user_id)  # GET获取单个对象
        like.delete()

        return HttpResponse(json.dumps({'error': 0}))

        # ---------------------------------------------------------------
        # 获取课程收藏情况
        # REQUIRES:         变量名|类型|说明
        #               course_id|int|课程id
        #                 user_id|int|用户id
        # MODIFIES: None
        # EFFECTS:     like_count|int|收藏数
        return HttpResponse(json.dumps({'like_count': ans_likes, 'like': user_like}))


#                   liked|int|0:未收藏 1:已收藏
@csrf_exempt
def course_like_count(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        course_id = str(data.get('course_id'))
        user_id = request.user.id

        likes = R_Course_User_Like.objects.filter(course_id=course_id)
        ans_likes = int(likes.count())  # len(likes)
        if (user_id != None):
            likes = R_Course_User_Like.objects.filter(course_id=course_id, user_id=user_id)
            user_like = (likes.count() > 0)  # len(likes)
            # # print("like:", user_like, likes)
        else:
            user_like = 0
            # # print("user:", user_id)

        return HttpResponse(json.dumps({'like_count': ans_likes, 'liked': user_like}))


class ActiveUserView(View):
    def get(self, request, active_code):
        # 用code在数据库中过滤处信息
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                # 通过邮箱查找到对应的用户
                user = User.objects.get(email=email)
                # 激活用户
                user.is_superuser = True
                user.save()
        else:
            return HttpResponse(json.dumps({'error': 104, 'msg': '用户激活失败'}))  # activated fail
        return render(request, 'index.html')


# Upload User Photo Interface
# URL: 
@csrf_exempt
def upload_user_photo(request):
    if (request.method == 'POST'):
        size = request.FILES['user_photo'].size
        user_photo_form = UserPhotoForm({'size': size})
        if (user_photo_form.is_valid()):
            userprofile = UserProfile.objects.get(user_id=request.user.id)
            if (userprofile.user_photo != None):
                link = userprofile.user_photo.url
                t = link.split("/")
                t.remove(t[0])
                file_path = "/".join(t)
                if (os.path.exists(file_path)):
                    os.remove(file_path)
            userprofile.user_photo = request.FILES['user_photo']
            userprofile.save()
            handle_upload_resource(request.FILES['user_photo'], userprofile.user_photo.url)
            return HttpResponse(json.dumps({'error': 0}))
        else:
            return HttpResponse(json.dumps({'error': 1}))


# ---------------------------------------------------------------
# 获取最多下载量的资源id列表
# REQUIRES:         变量名|类型|说明
#                   number|int|资源数量
#               college_id|int|检索范围，即院系代号，-1为全站检索
# MODIFIES: None
# EFFECTS:     result|list[dict{}]|返回资源信息列表
#                   资源信息字典：
#                   变量名|类型|说明
#                   :-:|:-:|:-:
#           resource_id|int|资源id
#              username|str|上传者
#        download_count|int|下载量
#                  name|str|资源名称
@csrf_exempt
def most_download_resource_list(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        number = int(data.get('number'))  # str->int #int(request.GET["number"])

        college_id = int(data.get('college_id'))  # int(request.GET["college_id"])

        #    resources = Resource.objects.filter(~Q(download_count = 0)).order_by('-download_count') #取下载量不等于0的filter,然后按下载量降序排序

        college_id_str = str(college_id)
        if (len(college_id_str) == 1):
            college_id_str = "0" + str(college_id)
        # # print(college_id_str)
        if (college_id == -1):  # 统计全站的资源
            resources = Resource.objects.filter().order_by('-download_count')  # course_code__contains="01"
        else:
            resources = Resource.objects.filter(
                Q(course_code__regex="^." + college_id_str) | Q(course_code__regex="^..." + college_id_str)).order_by(
                '-download_count')  # course_code__contains="01"

        ans = []
        cnt = 0
        i = 0
        for r in resources:
            # while (i < resources.count()): #len(resources)
            dict = {}
            if (cnt == number):
                break
            u_id = r.upload_user_id
            u_i = User.objects.filter(id=u_id)
            if (u_i.count() == 0):  # len(u_i)
                continue
            u_info = User.objects.get(id=u_id)

            dict["username"] = User.objects.get(id=u_id).username
            dict["download_count"] = r.download_count
            dict["resource_id"] = r.id
            dict["name"] = r.name
            # # print(dict)
            ans.append(dict)
            cnt = cnt + 1
        # # print(ans)
        return HttpResponse(json.dumps({'result': ans}))


# get most downloaded resource id list of one course
# URL:/course/resource/download/most/
@csrf_exempt
def most_download_resource_of_course(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        course_id = int(data.get('course_id'))
        number = str(data.get('number'))
        course_code = Course.objects.get(id=course_id).course_code
        result = Resource.objects.filter(course_code=course_code).order_by('-download_count').values_list('id',
                                                                                                          flat=True)
        count = 0
        id_list = []
        for item in result:
            id_list.append(item)
            count += 1
            if (count == number):
                break
    return HttpResponse(json.dumps({'id_list': id_list}))


# get most downloaded resource id list of one course
# URL:/course/resource/download/most/info/
@csrf_exempt
def most_download_resource_of_course_info(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        course_id = int(data.get('course_id'))
        number = int(data.get('number'))
        course_code = Course.objects.get(id=course_id).course_code
        result = Resource.objects.filter(course_code=course_code).order_by('-download_count')
        count = 0
        info_list = []
        for item in result:
            info = {}
            u_id = item.upload_user_id
            u_i = User.objects.filter(id=u_id)
            if (u_i.count() == 0):
                continue
            u_info = User.objects.get(id=u_id)
            info["username"] = u_info.username
            info["download_count"] = item.download_count
            info["resource_id"] = item.id
            info["name"] = item.name
            info_list.append(info)
            count += 1
            if (count == number):
                break
    return HttpResponse(json.dumps({'info_list': info_list}))


# ---------------------------------------------------------------
# 同袍的登录接口，跳转到同袍的登录界面，感觉不需要POST
# "need_phone_number": 1, , "need_identification": 1
@csrf_exempt
def login_tongpao(request):
    url = 'https://tongpao.qinix.com/auths/send_params'
    headers = {'Tongpao-Auth-appid': 'c643da987bdc3ec74efbb0ef7927f7ea',
               'Tongpao-Auth-secret': 'GNcP_Pa0Z3nFjjsQa8sd8VCUmUEiIZBa6Rue682LDsMyUIx7iwPplQ'}
    data = {  # 需要
        # "code":"BElkqvTZCkO924Za-hh8YcWmIDwGCwLXo7n3PrrYXD6lItvlX__b4DbZBgiXaV0ySHZytqlH2swvrbDca4X_MD1v6a2TPw",
        "redirect": "http://buaaicourse.com/passport/entry/",
        # "http://127.0.0.1:8000/tongpao/" #https://questionor.cn/problemsets",

        "need_email": 1,

        "need_school_info": 1,
        "need_personal": 1,
    }
    r = requests.post(url, headers=headers, data=json.dumps(data))

    # # print(r.text)
    json_code = json.loads(r.text)
    # # print(json_code)
    token = str(json_code['token'])
    # # print(token) #返回这个token给前端跳？
    return HttpResponse(json.dumps({'url': "https://tongpao.qinix.com/auths/login?token=" + token}))
    # return HttpResponseRedirect("https://tongpao.qinix.com/auths/login?token="+token) #HttpResponse(json.dumps({'error': 0}))


# ---------------------------------------------------------------
# 获取同袍用户信息的接口，目前是GET，可以post回信息
# 可以获取到的信息例如如下：
# "tongpao_username":"14011100","phone_number":["17801016282"],"email":"291045048@qq.com","real_name":"赵奕","birthday":"1996-10-31","gender":"男","grade":2015,"student_id":"14011100","college":"计算机学院","major":"计算机科学与技术","class_name":"150617","identification":"320982199610312298"}
@csrf_exempt
def tongpao(request):
    # # print("HHHHH")
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        # # print("TONGPAO!!!")

        code = str(data.get('code'))  # code = str(request.GET["code"])
        #        code = str(request.GET["code"])
        # # print("code = ",code)

        url = 'https://tongpao.qinix.com/auths/get_data'
        headers = {'Tongpao-Auth-appid': 'c643da987bdc3ec74efbb0ef7927f7ea',
                   'Tongpao-Auth-secret': 'GNcP_Pa0Z3nFjjsQa8sd8VCUmUEiIZBa6Rue682LDsMyUIx7iwPplQ'}
        data = {
            "code": code,
        }
        # # print(data)
        r = requests.post(url, headers=headers, data=data)
        # # print(r.text)
        json_text = json.loads(r.text)
        profile = json_text["data"]
        # # print(profile)
        # # print(type(profile))
        student_id = str(profile["student_id"])
        # # print(type(student_id))

        students = User.objects.filter(username=student_id)
        if (students.count() > 0):  # 之前已经登录过 #len(students)
            #        test = requests.post("http://127.0.0.1:8000/sign/login/",data={"error":0, "username":student_id,"password":"111111111111111111111111111111"})
            #        # # print(test.text)
            # # print("ENNNDDD")
            # # print("user:", student_id)
            return HttpResponse(json.dumps({"error": 0, "username": student_id}))
        #        request.session['username'] = student_id # store in session
        #        return HttpResponseRedirect("/")

        college_dict = {
            '经济学院': 1,
            '外国语学院': 2,
            '物理与天文学院': 3,
            '软件学院': 4,
            '职业与继续教育学院': 5,
            '历史与档案学院': 6,
            '公共管理学院': 7,
            '工商管理与旅游管理学院': 8,
            '化学科学与工程学院': 9,
            '资源环境与地球科学学院': 10,
            '体育学院': 11,
            '马克思主义学院': 12,
            '新闻学院': 13,
            '民族学与社会学学院': 14,
            '艺术与设计学院': 15,
            '生命科学学院': 16,
            '建筑与规划学院': 17,
            '医学院': 18,
            '生态与环境学院': 19,
            '文学院': 20,
            '法学院': 21,
            '数学与统计学院': 22,
            '信息学院': 23,
            '国际学院': 24,
            '农学院': 25,
            '材料与能源学院': 26,
            '昌新国际艺术学院': 27,
            '大学外语教学部': 28,
            '地球科学学院': 29,
            '政府管理学院': 30,
            '汉语国际教育学院': 31,
            '资源植物研究院': 32
        }

        tongpao_username = profile["tongpao_username"]
        birthday = gender = grade = real_name = identification = class_name = major = grade = ""
        phone_number = 0

        if ("phone_number" in profile):
            phone_number = profile["phone_number"]
            # # print(phone_number)
            phone_number = int(phone_number[0])
            # # print(phone_number)
        if ("email" in profile):
            email = profile["email"]
        if ("real_name" in profile):
            real_name = profile["real_name"]
        if ("birthday" in profile):
            birthday = profile["birthday"]
        if ("gender" in profile):
            gender = profile["gender"]
            # # print("%#!@##",gender)
            gender_dict = {"男": 1, "女": 2}
            gender = gender_dict[gender]
            # # print("@@@@",gender)
        if ("grade" in profile):
            grade = profile["grade"]
        if ("college" in profile):
            college = profile["college"]
        if ("major" in profile):
            major = profile["major"]
        if ("class_name" in profile):
            class_name = profile["class_name"]
        if ("identification" in profile):
            identification = profile["identification"]

        user = User()
        user.username = student_id

        # # print("!!!!username=",student_id)
        user.set_password("111111111111111111111111111111")
        user.is_active = True
        user.is_superuser = True
        user.email = email
        user.first_name = "TongPao"

        user.save()

        user_profile = UserProfile()

        user_profile.user_id = user.id
        user_profile.gender = gender
        user_profile.college_id = 0
        if (college in college_dict):
            user_profile.college_id = college_dict[college]
        user_profile.intro = "同袍用户"

        user_profile.nickname = ""
        user_profile.info = ""

        user_profile.save()

        tp_u = Tongpao_Userprofile()
        tp_u.student_id = student_id
        tp_u.tongpao_username = tongpao_username
        tp_u.phone_number = phone_number
        tp_u.email = email
        tp_u.real_name = real_name
        tp_u.gender = gender
        tp_u.birthday = birthday
        tp_u.grade = grade
        tp_u.college = college
        tp_u.major = major
        tp_u.class_name = class_name
        tp_u.identification = identification

        tp_u.save()

        #    test = requests.post("http://127.0.0.1:8000/sign/login/",data={"username":student_id,"password":"111111111111111111111111111111"})
        #    # # print(test.text)
        # request.session['username'] = student_id # store in session
        # # print("OVVVVVEEERRR")
        #    return HttpResponseRedirect("/")
        return HttpResponse(
            json.dumps({"error": 0, "username": student_id, "password": "111111111111111111111111111111"}))


# return HttpResponseRedirect("/")#http://127.0.0.1:8000/")


# 忘记密码-提交申请-发送邮件
# URL:/user/forget/password/send/
@csrf_exempt
def user_forget_password_send(request):
    if (request.method == 'POST'):
        email = str(request.POST.get('email'))
        send_reset_pswd_email(email, 'reset pswd')


# 忘记密码-重置密码
# URL:/user/forget/password/set/
@csrf_exempt
def user_forget_password_set(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        email = str(data.get('email'))
        code = str(data.get('code'))
        new_pw1 = str(data.get('new_pw1'))
        new_pw2 = str(data.get('new_pw2'))
        if (new_pw1 != new_pw2):
            return HttpResponse(json.dumps({'error': 1}))
        all_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='reset pswd')
        if (all_records.count() < 1):  # len(all_records)
            return HttpResponse(json.dumps({'error': 1}))
        user = User.objects.get(email=email)
        user.set_password(new_pw1)
        user.save()
        return HttpResponse(json.dumps({'error': 0}))


# 修改密码
# URL: /user/modify/password/
@csrf_exempt
def user_modify_password(request):
    if (request.method == 'POST'):
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({'error': 1}))
        data = json.dumps(request.POST)
        data = json.loads(data)
        user_id = request.user.id
        old_pw = str(data.get('old_pw'))
        new_pw1 = str(data.get('new_pw1'))
        new_pw2 = str(data.get('new_pw2'))
        if (new_pw1 != new_pw2):
            return HttpResponse(json.dumps({'error': 1}))
        user = User.objects.get(id=user_id)
        cb = CustomBackend()
        result = cb.authenticate(username=user.username, password=old_pw)
        if (result is not None and result.is_active):
            user.set_password(new_pw1)
            user.save()
            auth.logout(request)
            return HttpResponse(json.dumps({'error': 0}))
        return HttpResponse(json.dumps({'error': 1}))


def get_classification(s):
    if (s[0:3] == "B28"):  # B28D2010
        return s[1:3]
    if (s[0] == 'B'):  # B3I063110
        return (s[3:5])  # F06D3750
    return (s[1:3])


# ---------------------------------------------------------------
# 获取最新上传的资源信息列表
# REQUIRES:         变量名|类型|说明
#                   number|int|资源数量
#                   college_id|int|检索范围，即院系代号，-1为全站检索
# MODIFIES: None
# EFFECTS:     result|list[dict{}]|返回资源信息列表
#                   资源信息字典：
#                   变量名|类型|说明
#                   :-:|:-:|:-:
#              result|list[dict{}]|返回资源信息列表
# 资源信息字典：
#                   变量名|类型|说明
#                     :-:|:-:|:-:
#             resource_id|int|资源id
#                username|str|上传者
#          download_count|int|下载量
#                    name|str|资源名称
@csrf_exempt
def latest_upload_resource_list(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)

        number = int(data.get('number'))  # int(request.GET["number"])
        college_id = int(data.get('college_id'))  # int(request.GET["college_id"])

        t1 = time.clock()

        college_id_str = str(college_id)
        if (len(college_id_str) == 1):
            college_id_str = "0" + str(college_id)
        # # print(college_id_str)
        if (college_id == -1):  # 统计全站的资源
            resources = Resource.objects.filter().order_by('-upload_time')  # course_code__contains="01"
        else:
            resources = Resource.objects.filter(
                Q(course_code__regex="^." + college_id_str) | Q(course_code__regex="^..." + college_id_str)).order_by(
                '-upload_time')  # course_code__contains="01"
        #    resources = Resource.objects.filter(Q(course_code__regex="^.06")|Q(course_code__regex="^...06")).order_by('-upload_time') #course_code__contains="01"

        ans = []
        cnt = 0
        # siz = resources.count() #len(resources)
        # # print("siz = ", siz)
        # while (i < siz):
        for r in resources:
            dict = {}
            if (cnt == number):
                break
            u_id = r.upload_user_id
            u_i = User.objects.filter(id=u_id)
            if (u_i.count() == 0):  # len(u_i)
                continue
            dict["username"] = User.objects.get(id=u_id).username
            dict["download_count"] = r.download_count
            dict["resource_id"] = r.id
            dict["name"] = r.name
            ans.append(dict)
            cnt = cnt + 1
        t2 = time.clock()
        return HttpResponse(json.dumps({'result': ans}))


@csrf_exempt
def user_like_course_namelist(request):
    if (request.method == 'POST'):
        data = json.dumps(request.POST)
        data = json.loads(data)
        user_id = request.user.id
        # user_id = 2
        course_info_list = []
        course_id_list = R_Course_User_Like.objects.filter(user_id=user_id).values_list('course_id', flat=True)
        for course_id in course_id_list:
            course_info_list.append(interface.course_information(int(course_id)))
            # # print("like:", course_info_list)
        return HttpResponse(json.dumps({'info_list': course_info_list}))


# Resource Search Interface(by ohazyi)
# REQUIRES: the ajax data should be json data {'keyword': keyword, course_id|int|课程id，-1表示全局搜索}
# MODIFIES: NONE
# EFFECTS: return data {'query_list': query_list}
#          query_list is a list whose element is dicts like (user_id, total scores),
#          such as {'college_id': 10, 'class_id': 55, 'name': '安卓', 'credit': 5, 'id': 9, 'hours': 10}
#          the list is ordered by id temporaily (can be modified to revelance)
@csrf_exempt
def resource_query(
        request):  # http://localhost:8080/solr/mynode2/select?q=%E6%95%B0%E6%8D%AE%E5%BA%93&fq=course_code%3AB3I08224C&rows=1000&wt=json&indent=true
    #    # print("UUUUUUUUU")
    #    query = request.GET['keyword']
    #    course_id = request.GET['course_id']

    if (request.method == "POST"):
        data = json.dumps(request.POST)  # new
        data = json.loads(data)
        # data = json.loads(request.body.decode())
        query = str(data.get('keyword'))
        course_id = str(data.get('course_id'))

        cs_url = 'http://localhost:8080/solr/mynode2/select?'

        course = Course.objects.get(id=course_id)
        course_code = course.course_code

        fq_str = "course_code:" + course_code
        param = {'q': query, 'fl': 'id,name,score', 'fq': fq_str, 'rows': 2000, 'wt': 'json', 'indent': 'true'}

        r = requests.get(cs_url, params=param)

        query_res = http_get(r.url)

        json_r = json.loads(bytes.decode(query_res))
        query_list = json_r['response']['docs']

        ans = []
        for i in query_list:
            if (i['score'] >= 0):  # 排除掉匹配结果太低的
                ans.append(i['id'])
        return HttpResponse(json.dumps({'query_list': ans}, cls=ComplexEncoder))

# getcoursetable/
@csrf_exempt
def course_table(request):
    if request.method == "POST":
        # data = json.loads(request.body)
        data = json.dumps(request.POST)  # new
        data = json.loads(data)
        user_course = User.objects.get(id=data.get('id')).course_set.all()
        # # print(type(user_course[0]))
        course_list = []
        if user_course:
            for course in user_course:
                course_list.append(eval(objects_to_json(course, Course))[0])
            # print(course_list)
            # return HttpResponse(json.dumps({'course_list': course_list}))
        else:
            user = UserProfile.objects.get(user_id=data.get('id'))
            username = user.studentid
            password = user.studentpassword
            course_list = course_crawler(url, username, password)
            for course in course_list:
                try:
                    one_course = Course.objects.filter(name=course['KCM'], course_code=course['KCID']).first()
                    user = User.objects.get(id=data.get('id'))
                    one_course.student.add(user)
                    user_course = User.objects.get(id=data.get('id')).course_set.all()
                    for course in user_course:
                        course_list.append(eval(objects_to_json(course, Course))[0])
                except:
                    pass
            # print(course_list)

        respondlist=[]
        for i in range(5):
            coursehourlist=[]
            for j in range(7):
                coursehourlist.append({})
            respondlist.append(coursehourlist)
        
        for li in course_list:
            if li['XQ1']:
                try:
                    col = 0
                    coursetimes = li['XQ1'].split(',')
                    for cts in coursetimes:
                        courseitem = {}
                        place = cts.index(' ')
                        coursetime = cts[place:cts.index('-',place+1)]
                        courseitem['id'] = li['id']
                        courseitem['lessonsName'] = li['name']
                        courseitem['lessonsAddress'] = li['lessonsAddress']
                        courseitem['lessonsTeacher'] = li['teacher']
                        courseitem['lessonsRemark'] = cts.split(' ')[0]
                        # print(int(int(coursetime)/2))
                        respondlist[int(int(coursetime)/2)][col]=courseitem
                except:
                    pass
            if li['XQ2']:
                try:
                    col = 1
                    coursetimes = li['XQ2'].split(',')
                    for cts in coursetimes:
                        courseitem = {}
                        place = cts.index(' ')
                        coursetime = cts[place:cts.index('-',place+1)]
                        courseitem['id'] = li['id']
                        courseitem['lessonsName'] = li['name']
                        courseitem['lessonsAddress'] = li['lessonsAddress']
                        courseitem['lessonsTeacher'] = li['teacher']
                        courseitem['lessonsRemark'] = cts.split(' ')[0]
                        # print(int(int(coursetime)/2))
                        respondlist[int(int(coursetime)/2)][col]=courseitem
                except:
                    pass
            if li['XQ3']:
                try:
                    col = 2
                    coursetimes = li['XQ3'].split(',')
                    for cts in coursetimes:
                        courseitem = {}
                        place = cts.index(' ')
                        coursetime = cts[place:cts.index('-',place+1)]
                        courseitem['id'] = li['id']
                        courseitem['lessonsName'] = li['name']
                        courseitem['lessonsAddress'] = li['lessonsAddress']
                        courseitem['lessonsTeacher'] = li['teacher']
                        courseitem['lessonsRemark'] = cts.split(' ')[0]
                        # print(int(int(coursetime)/2))
                        respondlist[int(int(coursetime)/2)][col]=courseitem
                except:
                    pass
            if li['XQ4']:
                try:
                    col = 3
                    coursetimes = li['XQ4'].split(',')
                    # print("coursetimes:"+str(coursetimes))
                    for cts in coursetimes:
                        courseitem = {}
                        place = cts.index(' ')
                        coursetime = cts[place:cts.index('-',place+1)]
                        courseitem['id'] = li['id']
                        courseitem['lessonsName'] = li['name']
                        courseitem['lessonsAddress'] = li['lessonsAddress']
                        courseitem['lessonsTeacher'] = li['teacher']
                        courseitem['lessonsRemark'] = cts.split(' ')[0]
                        # print(int(int(coursetime)/2))
                        respondlist[int(int(coursetime)/2)][col]=courseitem
                except:
                    pass
            if li['XQ5']:
                try:
                    col = 4
                    coursetimes = li['XQ5'].split(',')
                    # print('coursetimes:'+str(coursetimes))
                    for cts in coursetimes:
                        courseitem = {}
                        place = cts.index(' ')
                        coursetime = cts[place:cts.index('-',place+1)]
                        courseitem['id'] = li['id']
                        courseitem['lessonsName'] = li['name']
                        courseitem['lessonsAddress'] = li['lessonsAddress']
                        courseitem['lessonsTeacher'] = li['teacher']
                        courseitem['lessonsRemark'] = cts.split(' ')[0]
                        # print(int(int(coursetime)/2))
                        respondlist[int(int(coursetime)/2)][col]=courseitem
                except:
                    pass
        return HttpResponse(json.dumps({'respondlist': respondlist}))
    else:
        # print(1)
        return 1
        # user.


def objects_to_json(objects, model):
    """
    将 model对象 转化成 json
        example：
            1. objects_to_json(Test.objects.get(test_id=1), EviewsUser)
            2. objects_to_json(Test.objects.all(), EviewsUser)
    :param objects: 已经调用all 或者 get 方法的对象
    :param model: objects的 数据库模型类
    :return:
    """
    from collections import Iterable
    concrete_model = model._meta.concrete_model
    list_data = []

    # 处理不可迭代的 get 方法
    if not isinstance(object, Iterable):
        objects = [objects, ]

    for obj in objects:
        dict_data = {}
        # # print(concrete_model._meta.local_fields)
        for field in concrete_model._meta.local_fields:
            if field.name == 'user_id':
                continue
            value = field.value_from_object(obj)
            dict_data[field.name] = value
        list_data.append(dict_data)

    data = json_encode_list(list_data)
    return data


def json_encode_list(list_data):
    """
    将列表中的字典元素转化为对象
    :param list_data:
    :return:
    """
    json_res = "["
    for item in list_data:
        json_res = json_res + json_encode_dict(item) + ", "
    return json_res[:-2] + "]"


def json_encode_dict(dict_data):
    """
    将字典转化为json序列
    :param dict_data:
    :return:
    """
    json_data = "{"
    for (k, v) in dict_data.items():
        json_data = json_data + json_field(k) + ':' + json_field(v) + ', '
    json_data = json_data[:-2] + "}"
    return json_data


def json_field(field_data):
    """
    将字典的键值转化为对象
    :param field_data:
    :return:
    """
    if isinstance(field_data, str):
        return "\"" + field_data + "\""
    elif isinstance(field_data, bool):
        if field_data == 'False':
            return 'false'
        else:
            return 'true'
    elif isinstance(field_data, unicode):
        return "\"" + field_data.encode('utf-8') + "\""
    elif field_data is None:
        return "\"\""
    else:
        return "\"" + str(field_data) + "\""

# studentnotifications/
@csrf_exempt
def verify_studentid(request):
    if request.method == "POST":

        data = json.dumps(request.POST)  # new
        data = json.loads(data)
        # print(data)



        student_id = data['username']
        student_password = data['password']
        result_bool = verify_student(student_id,student_password)
        if result_bool:
            user = UserProfile.objects.filter(user_id=data['id']).first()
            user.studentid=student_id
            user.studentpassword=student_password
            user.is_ynu = '1'
            user.save()
            return HttpResponse(json.dumps({'result':True}))
        else:
            return HttpResponse(json.dumps({'result':False}))


#/score
@csrf_exempt
def get_user_grades(request):
    if request.method == "POST":
        data = json.dumps(request.POST)  # new
        data = json.loads(data)
        # print(data)
        user_id = data['userid']
        user = UserProfile.objects.get(user_id=user_id)
        all_course = Grades.objects.filter(user_id=str(user_id))
        course_grades = []
        if  all_course:
            for course in all_course:
                all_courses_scores = {}
                course_name = Course.objects.filter(id = course.course_id)[0].name
                course_grade = course.grade
                all_courses_scores['course_name'] = course_name
                all_courses_scores['course_grades'] = course_grade
                course_grades.append(all_courses_scores)
                all_gpa = GPA.objects.filter(user_id=user_id)[0].gpa
                courses_nums = eval(GPA.objects.filter(user_id=user_id)[0].course_numbers)
                gpas = eval(all_gpa)
                # print(gpas)
                all_results = {'gpa': gpas,
                               'studentscore': [{'value': courses_nums[4], 'name': "60分以下"},
                                                {'value': courses_nums[3], 'name': "60~70分"},
                                                {'value': courses_nums[2], 'name': "70~80分"},
                                                {'value': courses_nums[1], 'name': "80~90分"},
                                                {'value': courses_nums[0], 'name': "90分以上"},
                                                ],
                               'coursenum': len(course_grades),
                               }
            return HttpResponse(json.dumps(all_results))
        else:
            test = TestYnutest('D:\\只狼\\chromedriver.exe', user.studentid,user.studentpassword)
            all_information = test.test_ynutest()
            # print(all_information)
            all_courses_scores = all_information['coursescores']
            all_gpa = all_information['gpa_content'] # GPA
            all_course_num = all_information['num_content']
            gpas = [None for _ in range(7)]
            courses_nums = [None for _ in range(5)]
            for index,gpa in enumerate(all_gpa):
                gpas[index] = gpa['GPA']
            for index,course_num in enumerate(all_course_num):
                if course_num['DJSL'] is not None:
                    courses_nums[index] = course_num['DJSL']
                else:
                    index+=1
            GPA.objects.create(gpa=str(gpas),user_id=user_id,course_numbers=str(courses_nums))
            all_results = {'gpa': gpas,
        'studentscore':[{'value': courses_nums[0],'name': "60分以下"},
          {'value': courses_nums[1],'name': "60~70分"},
          {'value': courses_nums[2],'name': "70~80分"},
          {'value': courses_nums[3],'name': "80~90分"},
          {'value': courses_nums[4],'name': "90分以上"},
        ],
        'coursenum':len(all_courses_scores),
        }
            result = {}
            for course in all_courses_scores:
                if Course.objects.filter(name=course['KCM']):
                    Grades.objects.create(grade=course['ZCJ'],
                                          course_id=Course.objects.filter(name=course['KCM']).first().id,
                                          user_id = user_id)
                    course_name = course['KCM']
                    course_grade = course['ZCJ']
                    result['course_name'] = course_name
                    result['course_grades'] = course_grade
                    course_grades.append(result)
                else:
                    # # print(1)
                    continue
            return HttpResponse(json.dumps(all_results))


#/coursescore
@csrf_exempt
def get_coursegrades(request):
    if request.method == "POST":
        data = json.dumps(request.POST)  # new
        data = json.loads(data)
        # print(data)
        course_id = data['courseid']
        all_grades = Grades.objects.filter(course_id=course_id)
        add_grade = 0
        grade1,grade2,grade3,grade4,grade5 = 0,0,0,0,0
        for grade in all_grades:
            if float(grade.grade)<60:
                grade1+=1
            elif float(grade.grade)>=60 and float(grade.grade)<70:
                grade2+=1
            elif float(grade.grade)>=70 and float(grade.grade)<80:
                grade3+=1
            elif float(grade.grade)>=80 and float(grade.grade)<90:
                grade4+=1
            if float(grade.grade)>=90:
                grade5+=1
            add_grade+=float(grade.grade)
        try:
            average_grade =add_grade/len(all_grades)
        except:
            average_grade = 0
        studentscore=[{'value': grade1,'name': "60分以下"},
          {'value': grade2,'name': "60~70分"},
          {'value': grade3,'name': "70~80分"},
          {'value': grade4,'name': "80~90分"},
          {'value': grade5,'name': "90分以上"},
        ]
        result = {'studentscore':studentscore,'studentnum':len(all_grades),'courseaverage':average_grade}
        return HttpResponse(json.dumps(result))
