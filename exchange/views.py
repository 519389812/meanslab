from django.shortcuts import render, reverse, redirect
from django.http import JsonResponse
from user.models import CustomUser
from exchange.models import ExchangeCard, CardHolder
from django.contrib.auth import login as login_admin
from django.contrib.auth import logout as logout_admin
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from nanoid import generate


def check_authority(func):
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated:
            # if "X-Requested_With" in args[0].headers:
            #     return JsonResponse('Login required.', safe=False)
            return redirect('/exchange/login/?next=%s' % args[0].path)
        return func(*args, **kwargs)
    return wrapper


def exchange(request):
    return render(request, "exchange.html")


@check_authority
def card_holder(request):
    if request.method == 'POST':
        to = request.POST.get("to", "")
        content = request.POST.get("content", "")
        signature = request.POST.get("signature", "")
        if not all([to, content]):
            return render(request, "card_holder.html", {"msg": "请填写完整"})
        code = generate('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', 14)
        card_holder = CardHolder.objects.create(to=to, content=content, signature=signature, user=request.user, code=code)
        return render(request, "card.html", {"card_holder_id": card_holder.id})
    else:
        return render(request, "card_holder.html")


@check_authority
def card(request):
    if request.method == 'POST':
        params = request.POST.dict()
        card_holder_id = params['card_holder_id']
        try:
            card_holder = CardHolder.objects.get(id=card_holder_id)
        except:
            return render(request, 'card_holder.html', {'msg': 'Nothing found, you need to create a new paper first.'}, status=403)
        del (params['csrfmiddlewaretoken'])
        del (params['card_holder_id'])
        data = {}
        for param_name, param_value in params.items():
            name, id_ = param_name.split('_')
            if id_ not in data.keys():
                data.setdefault(id_, {})
            data[id_][name] = param_value
        for _, value in data.items():
            code = generate('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', 14)
            ExchangeCard.objects.create(name=value['name'], times=int(value['times']), term=value['term'], card_holder=card_holder, user=request.user, code=code)
        return redirect(reverse("exchange:paper", args=[card_holder.code]))
    else:
        return render(request, "card.html")


def paper(request, code):
    if request.method == "GET":
        if not code:
            return render(request, "card_holder.html", {"msg": "Enter a code first."}, status=403)
        try:
            card_holder = CardHolder.objects.get(code=code)
        except:
            return render(request, 'card_holder.html', {'msg': 'Nothing found, you may to create a new paper first.'}, status=403)
        cards = ExchangeCard.objects.filter(card_holder=card_holder)
        print(cards)
        return render(request, "exchange_paper.html", {"card_holder": card_holder, "cards": cards})
    else:
        return render(request, "card_holder.html")


def show_exchange(request):
    if request.method == "POST":
        code = request.POST.get("code", "")
        if not code:
            return render(request, "exchange.html", {"msg": "Enter a code first."}, status=403)
        try:
            exchange_card = ExchangeCard.objects.get(code=code)
        except:
            return render(request, 'exchange.html', {'msg': 'Nothing found, you may to create a new paper first.'}, status=403)
        if exchange_card.used_times >= exchange_card.times:
            success = False
        else:
            success = True
            exchange_card.used_times += 1
            exchange_card.save()
        return render(request, "show_exchange.html", {"success": success, "exchange_card": exchange_card})
    else:
        return render(request, "exchange.html", {"msg": "Nothing found"})


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        if not all([username, password]):
            return render(request, "exchange_register.html", {"msg": "请填写完整"})
        if CustomUser.objects.filter(username=username).count() > 0:
            return render(request, "exchange_register.html", {"msg": "Username already exists"})
        user = CustomUser.objects.create_user(username=username, password=password)
        login_admin(request, user)
        return render(request, "card_holder.html")
    else:
        return render(request, "exchange_register.html")


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login_admin(request, user)
            next_url = request.GET.get('next', '')
            if next_url != '':
                return redirect(next_url)
            else:
                return redirect(reverse('exchange:exchange'))
        else:
            return render(request, 'exchange_login.html', {'msg': 'Wrong username or password!'})
    else:
        if not request.user.is_anonymous:
            return redirect(reverse('exchange:exchange'))
        else:
            next_url = request.GET.get('next', '')
            return render(request, 'exchange_login.html', {'next': next_url})


def logout(request):
    logout_admin(request)
    return redirect(reverse('exchange:exchange'))
