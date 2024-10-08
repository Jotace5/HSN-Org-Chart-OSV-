from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'hsn_users/home.html')

@login_required
def dashboard(request):
    return render(request, 'hsn_users/dashboard.html')
