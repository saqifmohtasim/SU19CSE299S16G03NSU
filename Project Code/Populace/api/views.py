from django.shortcuts import render,redirect
from piazza_api import Piazza
from .forms import piazzaLoginForm,googleLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
import re
import queue
#google Classroom
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
#Registration
from .forms import RegistrationForm



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
    form = RegistrationForm()
    return render(request,'api/index.html',{'form':form})

def user_logout(request):
    logout(request)
    return redirect('home')



def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():

            form.save()
    else:
        form = RegistrationForm()
    return render(request,'api/index.html',{'form':form})

def profile(request):
    form_p = piazzaLoginForm()
    return render(request,'api/profile.html', {
    'piazzaform':form_p
    })


# Function for piazza api functionality and login
class_dict = {}
p = Piazza()
def profile_p(request):

    #if this is a POST request we need to process the form data
    if request.method =='POST':
        form_p = piazzaLoginForm(request.POST)
        # form_g = googleLoginForm(request.POST)
        if 'piazza_p' in request.POST:

            print("piazza")
            if form_p.is_valid():
                p_email = form_p.cleaned_data['email']
                p_password = form_p.cleaned_data['password']
                p.user_login(p_email,p_password)
                # print(p.get_user_profile())
                dict = p.get_user_profile()
                # class_names = queue.Queue(maxsize=20)
                class_names = []
                class_code = []


                for i in dict['all_classes']:
                    test = dict['all_classes'][i]['num']
                    class_names.append(test)
                    class_code.append(i)
                    class_dict[test] = i

                return render(request,'api/piazza.html',{'class':class_names})

    else:
        # if a GET (or any other method) we'll create a blank form
        form_p = piazzaLoginForm()
        # form_g = googleLoginForm()
        return render(request,'api/profile.html',{
        'piazzaform':form_p
        })

def piazza_posts(request,pk = None):
    content_p = []
    po = []
    sub = []
    date = []
    if pk:
        for key, value in class_dict.items():
            if pk == key:
                networks = p.network(value)
                content_p = networks.iter_all_posts()
                print(value)
                for posts in content_p:
                    sub.append(posts['history'][0]['subject'])
                    date.append(posts['history'][0]['created'])
                    cleanr = re.compile('<.*?>')
                    cleantext = re.sub(cleanr, '', posts['history'][0]['content'])
                    po.append(cleantext)
    final = zip(sub,date,po)
    return render(request,'api/piazza_post.html',{'allposts':final})


# Function for piazza api functionality and login ends here
def profile_g(request):
    if request.method =='POST':
        if 'credentials' not in request.session:

            SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']
            API_SERVICE_NAME = 'classroom'
            API_VERSION = 'v1'

            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json', scopes=SCOPES)

            flow.redirect_uri = 'http://127.0.0.1:8000/profile/'

            authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true')

        # service = build(API_SERVICE_NAME,API_VERSION, credentials=credentials)
        #
        #             # Call the Classroom API
        # results = service.courses().list(pageSize=10).execute()
        # courses = results.get('courses', [])
        #
        # if not courses:
        #     print('No courses found.')
        # else:
        #     print('Courses:')
        #     for course in courses:
        #         print(course['name'])
            request.session['state'] = state
            return render(request,'api/google-class.html', {'authorize':authorization_url})
    else:
        return render(request,'api/profile.html')        # form_g = googleLoginForm()
