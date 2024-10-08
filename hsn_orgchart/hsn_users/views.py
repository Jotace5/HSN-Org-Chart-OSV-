from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

# Create your views here.
def home(request):
    # Print out the messages for debugging
    #print(list(messages.get_messages(request)))
    return render(request,'hsn_users/home.html')

@login_required
def dashboard(request):
    return render(request, 'hsn_users/dashboard.html')

def logout_view(request):
    # Print out the messages for debugging
    #print(f"Request method: {request.method}") 
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have successfully logged out.')
        return redirect('home')
    return HttpResponse('Logout can only be done via POST.', status=405)

def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect logged-in users away from login page

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('dashboard')  # Redirect to dashboard after login
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'hsn_users/login.html', {'form': form})

