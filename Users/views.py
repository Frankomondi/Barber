from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from validate_email import validate_email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import django
from django.utils.encoding import force_str
django.utils.encoding.force_text = force_str
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError,force_text
from .utils import generate_token
from django.core.mail import EmailMessage,send_mail
from django.conf import settings
import threading
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.views import View
from django.contrib.auth.models import User


# To MAKE EASIER FOR EMAILING A USER
class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


#RESET PASSWORD 
class RequestPasswordReset(View):
    def get(self,request):
        return render(request,'users/password_reset.html')


    def post(self,request):
        email=request.POST['email']

        context ={
        'values':request.POST
        }

        if not validate_email(email):
            messages.error(request,'please supply validate email')
            return render(request,'users/password_reset.html',context)

        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        if user.exists():
            email_contents = { 
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }

            link = reverse('reset-user-password',kwargs={
                'uidb64':email_contents['uid'],'token':email_contents['token']
                })

            email_subject = 'Password reset instruction'

            reset_url='http://'+current_site.domain+link

            email= EmailMessage(
                email_subject,
                'Hi there,Please use the link below to reset your password \n' + reset_url,
                'noreply@semycolon.com',
                [email],
            )
            EmailThread(email).start()
        messages.success(request,'We have sent you an email to reset your password')
        return render(request,'users/password_reset.html')
         

class CompletePasswordReset(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id=force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.info(request,'password link is invalid,please request a new one') 
                return render(request,'users/password_reset.html')       
        except Exception as identifer:
            pass
        return render(request,'users/new-password.html',context)


    def post(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password = request.POST['password']
        password2 = request.POST['password2']
        if password != password2:
            messages.warning(request,'password do not match')
            return render(request,'users/new-password.html',context)
        if len(password) < 6:
            messages.warning(request,'password too short')
            return render(request,'users/new-password.html',context)
        try:
            user_id=force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset successfully,you can login now with new Password')
            return redirect('login') 
        except Exception as identifer:
            messages.info(request,'Something went wrong ,try again')
            return render(request,'users/new-password.html',context)
