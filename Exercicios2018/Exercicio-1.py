from datetime import datetime

from chat.forms import ChatForm
from django.shortcuts import render
import json, requests, random, re
from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from MaxSAC import settings
from django.template import loader
from django.template.defaultfilters import pprint
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Chat, Cliente, Conversa

PAGE_ACCESS_TOKEN = settings.PAGE_ACCESS_TOKEN

VERIFY_TOKEN = settings.VERIFY_TOKEN


# 1) Nome da API - Facebook Messenger API
# 2) Utilidade - Capturar mensagens enviadas via FB Messenger
# 3) Link ou endpoint
# 4) Possíveis recursos. - Mensagens
# 5) Métodos suportados - GET/POST/DELETE
# 6) Exemplo(s) em python do método get
# 7) Exemplo(s) em python do pétodo post

# Helper function
def post_on_facebook(sender_id, message):
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient": {"id": sender_id}, "message": {"text": message}})
    requests.post(url, headers={"Content-Type": "application/json"}, data=response_msg)


def Login(request):
    next = request.GET.get('next', '/home/')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(next)
            else:
                return HttpResponse("Account is not active at the moment.")
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
    return render(request, "chat/login.html", {'next': next})


def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


def Home(request):
    conversas = Conversa.objects.all()
    template = "chat/home.html"
    context = {
        'home': 'active',
        'conversas': conversas,
    }
    return render(request, template, context)


def Post(request):
    if request.method == "POST":
        form = ChatForm()
        msg = request.POST.get('mensagem', None)
        if msg != '':
            conversa = Conversa.objects.get(room=request.POST.get('conversas'))
            sender_id = conversa.mensagens.first().user.sender_id
            me = Cliente.objects.get_or_create(sender_id=1859623857660142)[0]
            mensagem = Chat.objects.create(user=me, conversa=conversa, message=msg, created=datetime.now())
            conversa.mensagens.add(mensagem)
            conversa.save()
            post_on_facebook(sender_id, msg)

        return HttpResponseRedirect('/')
    else:
        return HttpResponse('Request must be POST.')


class ChatBot(generic.View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):

        fbMessenger = json.loads(self.request.body.decode('utf-8'))

        for fb_conversa in fbMessenger['entry']:
            for fb_message in fb_conversa['messaging']:
                if 'message' in fb_message:
                    url = "https://graph.facebook.com/v2.6/%s" % fb_message['sender']['id']
                    params = {'fields': 'first_name,last_name,profile_pic', 'access_token': PAGE_ACCESS_TOKEN}
                    user_details = requests.get(url, params).json()

                    cliente = Cliente.objects.get_or_create(sender_id=fb_message['sender']['id'],
                                                            first_name=user_details["first_name"],
                                                            last_name=user_details["last_name"],
                                                            picture=user_details["profile_pic"])[0]
                    chat = Chat.objects.create(user=cliente,
                                               message=fb_message['message']['text'],
                                               created=datetime.fromtimestamp(fb_message['timestamp'] / 1000))
                    conversa = Conversa.objects.get_or_create(room=cliente.sender_id)[0]
                    conversa.mensagens.add(chat)

        return HttpResponse()
