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

                if user.user_type != 'General' and user.is_locked: #politician
                    messages.error(request, 'Your Account has been locked out.An email has been sent to you to verify your account details')
                    request.session.set_test_cookie()
                    return HttpResponseRedirect(reverse('kyl:homepage'))
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
                messages.error(request, 'Your Account has been locked out.An email has been sent to you to verify your account details')
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


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('kyl:homepage'))



from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context

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