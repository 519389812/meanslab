from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from user.models import User, EmailVerifyRecord, Feedback, District
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login as login_admin
from django.contrib.auth import logout as logout_admin
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDictKeyError
import re
from django.utils import timezone
import datetime
from django.core.mail import send_mail
from meanslab.settings import EMAIL_HOST_USER
import random
from user_agents import parse
import json
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# from django.utils import timezone
from django.http import JsonResponse


def check_datetime_opened(close_timezone, now_timezone):
    return True if close_timezone > now_timezone else False


def check_authority(func):
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated:
            return redirect("/login/?next=%s" % args[0].path)
        return func(*args, **kwargs)
    return wrapper


def check_bot(func):
    def wrapper(*args, **kwargs):
        user_agent = parse(args[0].META.get('HTTP_USER_AGENT'))
        if user_agent.is_bot:
            return render(args[0], "error_500.html")
        return func(*args, **kwargs)
    return wrapper


def check_frequent(model_object):
    def func_wrapper(func):
        def args_wrapper(*args, **kwargs):
            if args[0].META.get('HTTP_X_FORWARDED_FOR'):
                ip = args[0].META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
            else:
                ip = args[0].META.get('REMOTE_ADDR').split(',')[0]
            last_ip_object = model_object.objects.filter(ip=ip).last()
            last_user_object = model_object.objects.filter(user=args[0].user).last()
            if not (last_ip_object is None or check_datetime_valid(timezone.localtime(last_ip_object.create_datetime), timezone.localtime(timezone.now()))) and not (last_user_object is None or check_datetime_valid(timezone.localtime(last_user_object.create_datetime), timezone.localtime(timezone.now()))):
                return render(args[0], "error_too_frequent.html")
            return func(*args, **kwargs)
        return args_wrapper
    return func_wrapper


def check_unique(model_object):
    def func_wrapper(func):
        def args_wrapper(*args, **kwargs):
            exist_count = model_object.objects.filter(user=args[0].user).count()
            if exist_count > 0:
                return render(args[0], "error_same_operation.html")
            return func(*args, **kwargs)
        return args_wrapper
    return func_wrapper


def check_is_touch_capable(func):
    def wrapper(*args, **kwargs):
        user_agent = parse(args[0].META.get('HTTP_USER_AGENT'))
        if not user_agent.is_touch_capable:
            if args[0].META.get("HTTP_REFERER"):
                return redirect(args[0].META.get("HTTP_REFERER")+"???????????????????????????")
            else:
                return redirect("/")
        return func(*args, **kwargs)
    return wrapper


# ???????????????????????????????????????requests,??????????????????object_id????????????
def check_accessible(model_object):
    def func_wrapper(func):
        def args_wrapper(*args, **kwargs):
            try:
                obj = model_object.objects.get(id=args[1])
            except:
                return redirect('/error_404')
            if args[0].user.is_superuser:
                return func(*args, **kwargs)
            accessible_team_id = list(obj.team.all().values_list("id", flat=True))
            if len(accessible_team_id) == 0:
                return func(*args, **kwargs)
            else:
                if not args[0].user.team:
                    return render(args[0], "user_setting.html", {'msg': '????????????????????????????????????????????????'})
                else:
                    for team_id in accessible_team_id:
                        if team_id in json.loads(args[0].user.team.related_parent):
                            return func(*args, **kwargs)
            return redirect('/error_not_accessible')
        return args_wrapper
    return func_wrapper


def check_grouping(func):
    def wrapper(*args, **kwargs):
        if not args[0].user.team:
            return render(args[0], "user_setting.html", {'msg': '????????????????????????????????????????????????'})
        return func(*args, **kwargs)
    return wrapper


@check_authority
def user_setting(request):
    return render(request, "user_setting.html")


def register(request):
    if request.method == "POST":
        if not check_post_valudate(request, check_username_validate, check_password_validate, check_email_validate):
            return render(request, "register.html", {"msg": "????????????????????????????????????"})
        username = request.POST.get("username")
        password = request.POST.get("password")
        email_address = request.POST.get("email_address")
        try:
            User.objects.create(username=username, password=make_password(password), email=email_address)
            return render(request, "register.html", {"msg": "??????????????????????????????????????????"})
        except:
            return render(request, "register.html", {"msg": "?????????????????????????????????????????????????????????"})
    else:
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, "register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login_admin(request, user)
            next_url = request.GET.get('next', '')
            if next_url != "":
                return redirect(next_url)
            else:
                return redirect('/')
        else:
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    if user.is_active:
                        return render(request, "login.html", {"msg": "??????????????????????????????"})
                    else:
                        return render(request, "login.html", {"msg": "?????????????????????????????????????????????"})
                else:
                    return render(request, "login.html", {"msg": "???????????????????????????"})
            except:
                return render(request, "login.html", {"msg": "???????????????????????????"})
    else:
        if request.user.is_authenticated:
            return redirect('/')
        else:
            next_url = request.GET.get('next', '')
            return render(request, "login.html", {'next': next_url})


def check_datetime_valid(create_timezone, now_timezone, std_seconds=30):
    return True if (now_timezone - create_timezone).seconds > std_seconds else False


@check_authority
@check_bot
@check_frequent(Feedback)
def feedback(request):
    if request.method == "POST":
        content = request.POST.get('content', '')
        if content == "":
            return render(request, "error_500.html")
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR').split(',')[0]
        Feedback.objects.create(user=request.user, content=content, ip=ip)
        return render(request, "feedback.html", {"msg": "????????????"})
    else:
        return render(request, "feedback.html")


def random_str(str_length=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    for i in range(str_length):
        str += chars[random.randint(0, length)]
    return str


@check_authority
def set_question_verify(request):
    return render(request, "set_question_verify.html")


@check_authority
def set_email_verify(request):
    return render(request, "set_email_verify.html")


@check_authority
def send_set_user_verify_email(request):
    if request.method == "POST":
        email_address = request.POST.get("email_address", "")
        if not check_post_valudate(request, check_email_validate):
            return render(request, "set_email_verify.html", {"msg": "??????????????????????????????!"})
        code = random_str(16)
        EmailVerifyRecord.objects.create(user=request.user, email=email_address, code=code, type="register", close_datetime=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=5))
        email_title = "???????????? - ??????????????????"
        email_body = "?????????????????????????????????????????????????????????5??????: http://%s/check_set_user_verify_email/%s" % (request.get_host(), code)
        send_status = send_mail(email_title, email_body, EMAIL_HOST_USER, [email_address])
        if send_status:
            return render(request, "set_email_verify.html", {"msg": "???????????????????????????????????????"})
        else:
            return render(request, "set_email_verify.html", {"msg": "????????????????????????????????????????????????????????????????????????"})
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def check_set_user_verify_email(request, code):
    records = EmailVerifyRecord.objects.filter(code=code)
    if len(records) > 0:
        for record in records:
            if check_datetime_opened(timezone.localtime(record.close_datetime), timezone.localtime(timezone.now())):
                user = User.objects.get(id=record.user.id)
                user.email = record.email
                user.save()
                return render(request, 'user_setting.html', {"msg": "??????????????????"})
        return render(request, 'set_email_verify.html', {"msg": "??????????????????"})
    else:
        return render(request, 'set_email_verify.html', {"msg": "??????????????????????????????"})


def pre_reset_password(request):
    return render(request, "pre_reset_password.html")


def pre_reset_password_by_email(request):
    return render(request, "pre_reset_password_by_email.html")


def send_reset_password_email(request):
    if request.method == "POST":
        if not check_post_valudate(request, check_email_validate):
            return render(request, "reset_password_email.html", {"msg": "?????????????????????????????????!"})
        username = request.POST.get("username", "")
        try:
            user = User.objects.get(username=username)
        except:
            return render(request, "pre_reset_password_by_email.html", {"msg": "??????????????????"})
        email_address = request.POST.get("email_address", "")
        if not user.email == email_address:
            return render(request, "pre_reset_password_by_email.html", {"msg": "???????????????"})
        code = random_str(16)
        EmailVerifyRecord.objects.create(user=user, code=code, type="reset", close_datetime=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=5))
        email_title = "???????????? - ????????????"
        email_body = "?????????????????????????????????????????????????????????5??????: https://%s/reset_password/%s" % (request.get_host(), code)
        send_status = send_mail(email_title, email_body, EMAIL_HOST_USER, [email_address])
        if send_status:
            return render(request, "reset_password_by_email.html", {"msg": "???????????????????????????????????????"})
        else:
            return render(request, "pre_reset_password_by_email.html", {"msg": "????????????????????????????????????????????????????????????????????????"})
    else:
        return render(request, "error_400.html", status=400)


def reset_password_by_email(request, code):
    records = EmailVerifyRecord.objects.filter(code=code)
    if len(records) > 0:
        for record in records:
            if check_datetime_opened(timezone.localtime(record.close_datetime), timezone.localtime(timezone.now())):
                if request.method == "GET":
                    record.close_datetime = timezone.localtime(timezone.now()) + datetime.timedelta(minutes=5)
                    record.save()
                    return render(request, 'reset_password_by_email.html', {"msg": "?????????????????????5?????????????????????", "code": code})
                else:
                    if not check_post_valudate(request, check_passwords_validate):
                        return render(request, "reset_password_by_email.html", {"msg": "?????????????????????????????????!"})
                    password = request.POST.get("password", "")
                    password_repeat = request.POST.get("password_repeat", "")
                    if password == "" or password_repeat == "":
                        return render(request, 'reset_password_by_email.html', {"msg": "????????????", "code": code})
                    if password != password_repeat:
                        return render(request, 'reset_password_by_email.html', {"msg": "??????????????????????????????", "code": code})
                    user = User.objects.get(id=record.user.id)
                    user.password = make_password(password)
                    user.save()
                    return render(request, 'login.html', {"msg": "??????????????????"})
        return render(request, 'reset_password_by_email.html', {"msg": "??????????????????"})
    else:
        return render(request, 'reset_password_by_email.html', {"msg": "????????????????????????????????????"})


@check_authority
def change_password(request):
    if request.method == "GET":
        return render(request, 'change_password.html')
    else:
        if not check_post_valudate(request, check_passwords_validate):
            return render(request, "change_password.html", {"msg": "?????????????????????????????????!"})
        old_password = request.POST.get("old_password", "")
        if check_password(old_password, request.user.password):
            password = request.POST.get("password", "")
            password_repeat = request.POST.get("password_repeat", "")
            if password == "" or password_repeat == "":
                return render(request, 'change_password.html', {"msg": "????????????"})
            if password != password_repeat:
                return render(request, 'change_password.html', {"msg": "??????????????????????????????"})
            user = User.objects.get(id=request.user.id)
            user.password = make_password(password)
            user.save()
            return render(request, 'login.html', {"msg": "????????????????????????????????????"})
        else:
            return render(request, "change_password.html", {"msg": "??????????????????!"})


def logout(request):
    logout_admin(request)
    return redirect(reverse("home"))


def check_username_validate(request):
    try:
        username = request.GET["username"]
    except MultiValueDictKeyError:
        username = request.POST.get("username")
    if username == "":
        return HttpResponse('?????????????????????')
    if len(username) < 4 or len(username) > 16:
        return HttpResponse('?????????????????????4??????????????????16?????????')
    if not re.search(r'^[_a-zA-Z0-9]+$', username):
        return HttpResponse("???????????????????????????(!,@,#,$,%...)")
    if User.objects.filter(username=username).count() != 0:
        return HttpResponse('??????????????????')
    return HttpResponse('')


def check_password_validate(request):
    try:
        password = request.GET["password"]
    except MultiValueDictKeyError:
        password = request.POST.get("password")
    if password == "":
        return HttpResponse('??????????????????')
    if len(password) < 6 or len(password) > 16:
        return HttpResponse('??????????????????6??????????????????16?????????')
    if not re.search(r'^\S+$', password):
        return HttpResponse("????????????????????????(??? ???)")
    return HttpResponse('')


def check_old_password_validate(request):
    try:
        password = request.GET["old_password"]
    except MultiValueDictKeyError:
        password = request.POST.get("old_password")
    if password == "":
        return HttpResponse('??????????????????')
    if len(password) < 6 or len(password) > 16:
        return HttpResponse('??????????????????6??????????????????16?????????')
    if not re.search(r'^\S+$', password):
        return HttpResponse("????????????????????????(??? ???)")
    return HttpResponse('')


def check_password_repeat_validate(request):
    try:
        password = request.GET["password_repeat"]
    except MultiValueDictKeyError:
        password = request.POST.get("password_repeat")
    if password == "":
        return HttpResponse('??????????????????')
    if len(password) < 6 or len(password) > 16:
        return HttpResponse('??????????????????6??????????????????16?????????')
    if not re.search(r'^\S+$', password):
        return HttpResponse("????????????????????????(??? ???)")
    return HttpResponse('')


def check_passwords_validate(request):
    try:
        params = request.GET.dict()
    except MultiValueDictKeyError:
        params = request.POST.dict()
    for key, value in params.items():
        if "password" in key:
            if key == "":
                return HttpResponse('??????????????????')
            if len(key) < 6 or len(key) > 16:
                return HttpResponse('??????????????????6??????????????????16?????????')
            if not re.search(r'^\S+$', key):
                return HttpResponse("????????????????????????(??? ???)")
    return HttpResponse('')


def check_lastname_validate(request):
    try:
        lastname = request.GET["lastname"]
    except MultiValueDictKeyError:
        lastname = request.POST.get("lastname")
    if lastname == "":
        return HttpResponse('??????????????????')
    if len(lastname) > 50:
        return HttpResponse('??????????????????50?????????')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', lastname):
        return HttpResponse("????????????????????????(!,@,#,$,%...)")
    return HttpResponse('')


def check_firstname_validate(request):
    try:
        firstname = request.GET["firstname"]
    except MultiValueDictKeyError:
        firstname = request.POST.get("firstname")
    if firstname == "":
        return HttpResponse('??????????????????')
    if len(firstname) > 50:
        return HttpResponse('??????????????????50?????????')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', firstname):
        return HttpResponse("????????????????????????(!,@,#,$,%...)")
    return HttpResponse('')


def check_question_validate(request):
    try:
        question = request.GET["question"]
    except MultiValueDictKeyError:
        question = request.POST.get("question")
    if question == "":
        return HttpResponse('????????????????????????')
    if len(question) < 6 or len(question) > 50:
        return HttpResponse('????????????????????????6?????????????????????50?????????')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5\?\uff1f]+$', question):
        return HttpResponse("??????????????????????????????(!,@,#,$,%...)")
    return HttpResponse('')


def check_answer_validate(request):
    try:
        answer = request.GET["answer"]
    except MultiValueDictKeyError:
        answer = request.POST.get("answer")
    if answer == "":
        return HttpResponse('????????????????????????')
    if len(answer) < 2 or len(answer) > 16:
        return HttpResponse('????????????????????????2?????????????????????16?????????')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', answer):
        return HttpResponse("??????????????????????????????(!,@,#,$,%...)")
    return HttpResponse('')


def check_email_validate(request):
    try:
        email_address = request.GET["email_address"]
    except MultiValueDictKeyError:
        email_address = request.POST.get("email_address")
    try:
        validate_email(email_address)
    except ValidationError:
        return HttpResponse("??????????????????????????????")
    return HttpResponse('')


def check_post_valudate(request, *args):
    check_method = args
    for method in check_method:
        if method(request).content != b'':
            return False
    return True


def get_province(request):
    provinces = District.objects.filter(parent__isnull=True).values()
    return JsonResponse({"provinces": provinces})


def get_city(request):
    city_id = request.GET.get('city_id')
    cities = District.objects.filter(parent_id=city_id).values()
    return JsonResponse({"cities": cities})


def get_district(request):
    district_id = request.GET.get('district_id')
    districts = District.objects.filter(parent_id=district_id).values()
    return JsonResponse({'districts': districts})
