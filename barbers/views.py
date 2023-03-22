from django.http import HttpResponse
## from django.contrib import messages
from django.shortcuts import render,redirect,reverse,get_object_or_404
from barbers.models import Appointment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
#Login Requirements
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required(login_url='login') 
def index(request):
    return render(request, "barbers/index.html")


def login_view(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.add_message(request, messages.WARNING,
                                 'Invalid credentials, try again')
            return render(request, 'users/login.html', context,)

        login(request, user)

        messages.add_message(request, messages.SUCCESS,
                             f'Welcome  {user.username} ')

        return redirect(reverse('appointment'))

    return render(request, 'users/login.html')
# ============================ REGISTER ==========================================

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        if not username or not password or not first_name or not last_name or not email:
            messages.error(request, 'All fields must be completed.')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        login(request, user)
        messages.success(request, 'You have registered  successfully.Login Now!!')
        return redirect('login')
    else:
        return render(request, 'barbers/register.html')


#it render the user to login page
@login_required(login_url='login')    
def appointment(request):
      # POST
  if request.method == 'POST':
      # Save order data to the database
    add = Appointment(
              fname=request.POST.get('fname'),
              lname=request.POST.get('lname'),
              phone=request.POST.get('phone'),
              email=request.POST.get('email'),
              contact=request.POST.get('contact'),
              barber=request.POST.get('barber'),
              date=request.POST.get('myDate'),
              time=request.POST.get('time'),
              comment=request.POST.get('comment'),
            )

    add.save()

    if add is not None:
     context = {
      "client": Appointment.objects.last(),
     }
     return render(request, "barbers/dashboard.html", context)
    else:
      return HttpResponse('{"success": false, "message": "Invalid input"}')
     # GET
  else:
    return render(request, "barbers/appointment.html")

 #nav functions
def services(request):
  return render(request,"barbers/services.html")
def team(request):
  return render(request,"barbers/team.html")
def dashboard(request):
  return render(request,"barbers/dashboard.html")
def home(request):
  return render(request,"barbers/index.html")
#Logout
def logout(request):
    return redirect('/')