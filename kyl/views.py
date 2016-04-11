from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render #,get_object_or_404
from django.core.urlresolvers import reverse
#from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
#from django.views.decorators.cache import cache_page #, never_cache
#from django.template.response import TemplateResponse
from django.contrib.auth import authenticate, login , logout
import requests
from politics.settings import GOOGLESECRET_KEY,GOOGLECAPTCHA_URL
from django.contrib import messages
from kyl.forms import UserRegisterForm
from django.utils.crypto import get_random_string

from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
from kyl.models import User


def homepage(request):
    if request.method == 'GET':
        return render(request,"index.html")


def rssfeed(request):
    if request.method == "GET":
        dictr = {}
        includess = request.GET.get('includess', False)
        excludess = request.GET.get('excludess', False)
        if includess:
            dictr['includess'] = includess
        if excludess:
            dictr['excludess'] = excludess
        return render(request,'rss.html',dictr)

def verify_email(request,key):
    print key
    if request.method == 'GET' or request.method == "HEAD":
        try:
            usr = User.objects.get(token=key)
            usr.verified_email = True
            usr.save()
            messages.success(request, "Email Verification Successfull.")
            return HttpResponseRedirect(reverse('kyl:login'))
        except User.DoesNotExist:
            messages.error(request,"Invalid URL")
            return HttpResponseRedirect(reverse('kyl:login'))
    else:
        return HttpResponse("BAD REQUEST",status=400)

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('kyl:homepage'))
    
    if request.method=='GET':
        return render(request,"users/signup_form.html",{'form' : UserRegisterForm})

    elif request.method=='POST':
        form = UserRegisterForm(data=request.POST.copy())
        captcha = request.POST.get('g-recaptcha-response',None)

        dicr = {}
        dicr['secret']=GOOGLESECRET_KEY
        dicr['response']=captcha
        result = requests.post(GOOGLECAPTCHA_URL, data=dicr)
        captcha_bool = False
        context = {}
        if result.json()["success"]:
            captcha_bool=True
        else:
            context['Captcha_Error']="Please Verify the Captcha Properly"

        if form.is_valid() and captcha_bool:
            fname = form.cleaned_data['first_name']
            lname = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            content = "http://localhost:8000/users/verify_email/"
            email_hash = get_random_string(length=128)
            content = content + email_hash
            user = form.save(commit=False)
            user.token = email_hash
            user.verify_email = False
            
            template = get_template('users/email_verify.txt')
            context = Context({
                              'fname' : fname,
                              'lname' : lname,
                              'username' : username,
                              'message' : content,
                              'email' : form.cleaned_data['email'],
                              })
            content = template.render(context)
            email = EmailMessage("KYL Email Verification",content,"KYL Email Verify",
                                 [form.cleaned_data['email'], ],
                                 headers = { 'Reply-To' : "ashish.sareen95@gmail.com" }
                                 )
            email.send()
            user.save()
            messages.success(request, "Successfully Registered. Please Verify your email.")
            return HttpResponseRedirect(reverse("kyl:login"))
        
        context['form'] = form #UserRegisterForm(initial=form.cleaned_data)
        return render(request,"users/signup_form.html",context)


    else:
        return HttpResponse("BAD REQUEST",status=400)


#@sensitive_post_parameters()
def user_login(request):
    if request.method == 'GET':
        next = request.GET.get('next',None)
        if request.user.is_authenticated():
            if next:
                messages.info(request,"Already Logged in.")
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('kyl:homepage'))
        else:
            request.session.set_test_cookie()
            return render(request, "login.html")

    elif request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            messages.error(request,"Please enable cookies and try again.")
            request.session.set_test_cookie()
            return render(request, "login.html")
        #Hard-coded HTML FORM , not a django generated one
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        user = authenticate(username=username, password=password)

        if user is not None:

            if user.is_active:

                if user.verified_email == False:
                    messages.error(request, 'Your Email hasn\'t been verified yet. Please Verify your email id.')
                    request.session.set_test_cookie()
                    return HttpResponseRedirect(reverse('kyl:login'))

                elif user.user_type != 'General' and user.is_locked: #politician
                    messages.error(request, 'Your Account has been locked out. Your Details aren\'t verified yet')
                    request.session.set_test_cookie()
                    return HttpResponseRedirect(reverse('kyl:login'))
                else:
                    #if is_safe_url only then else redirect
                    login(request, user)
                    response = HttpResponseRedirect(reverse('kyl:homepage'))
                    #response.set_cookie("user",user)
                    #print "NOW"
                    #for i in request.COOKIES:
                    #    print request.COOKIES[i]
                    return response
            else:
                # An inactive account was used - no logging in!
                messages.error(request, 'Your Account has been locked out.Please Contact the Site Admin.')
                request.session.set_test_cookie()
                return render(request, "login.html")
        else:
            # Invalid login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            messages.error(request, 'Invalid Username/Password combination.')
            request.session.set_test_cookie()
            return render(request, "login.html")
    else:
        return HttpResponse("BAD REQUEST",status=400)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('kyl:homepage'))




def contact(request):
    if request.method=='GET':
        return render(request,"contact.html",)    

    elif request.method=='POST':
        captcha = request.POST.get('g-recaptcha-response',None)
        dicr = {}
        dicr['secret']=GOOGLESECRET_KEY
        dicr['response']=captcha
        result = requests.post(GOOGLECAPTCHA_URL, data=dicr)
        captcha_bool = True
        
        if result.json()["success"]:
            captcha_bool=True
        else:
            context = {}
            context['Error']="Please Verify the Captcha Properly"
            return render(request,"contact.html",context)

        if captcha_bool:
            name = request.POST.get('name','None')
            email = request.POST.get('email','None')
            phone = request.POST.get('phone','None')
            message = request.POST.get('textdata','None')
            template = get_template('contact_template.txt')
            context = Context({
                              'name' : name,
                              'email' : email,
                              'phone' : phone,
                              'message' : message,
                              })
            content = template.render(context)
            email = EmailMessage("New form contact submission",content,"KYL Contact Query" ,
                                  ['ashish.sareen95@gmail.com'],
                                  headers = { 'Reply-To' : email }
                                 )
            email.send()
            messages.success(request, "Thank you for contacting us.We will get back to you within 48 hours. Have a Nice Day :D")
            return HttpResponseRedirect(reverse('kyl:contact'))

        else:
            context = {} 
            context['Error']="Please refill in the required details correctly and Verify Captcha"
            form = ContactForm(initial=new_data)
            context['form'] = form
            return render(request,"contact.html",context)
    else:
        return HttpResponse("BAD REQUEST",status=400)



def leadership_modi(request):
    if request.method == 'GET':
        return render(request,"leadership_modi.html")

def leadership_obama(request):
    if request.method == 'GET':
        return render(request,"leadership_obama.html")