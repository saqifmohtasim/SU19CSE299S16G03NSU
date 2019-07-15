from django.shortcuts import render,redirect
from piazza_api import Piazza
from .forms import piazzaLoginForm
from django.contrib.auth import authenticate, login


# Create your views here.
def home(request):
    if (request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('profile')
        else:
            return redirect('home')
    return render(request,'api/index.html')

def signup(request):
    return render(request,'api/signup.html')

def profile(request):
    p = Piazza()
    #if this is a POST request we need to process the form data
    if request.method =='POST':
        form = piazzaLoginForm(request.POST)
        if form.is_valid():
            p_email = form.cleaned_data['email']
            p_password = form.cleaned_data['password']
            p.user_login(p_email,p_password)
            # print(p.get_user_profile())
            dict = p.get_user_profile()
            class_names = []
            for i in dict['all_classes']:
                class_names.append(dict['all_classes'][i]['num'])
                print(class_names)

            return render(request,'api/piazza.html',{'class':class_names})
    else:
        # if a GET (or any other method) we'll create a blank form
        form = piazzaLoginForm()
    return render(request,'api/profile.html',{'piazzaform':form})
