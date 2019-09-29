from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/account/login')
def chat(request):
    return render(request, 'chat/chat.html')