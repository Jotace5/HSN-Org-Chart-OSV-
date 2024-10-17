from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.files.storage import default_storage
import os
import pandas as pd
from django.http import JsonResponse
from .models import models, DataUploadLog, dataOffice, dataOfficial
from django.utils import timezone
import pyexcel as p  

# Create your views here.
def home(request):
    # Print out the messages for debugging
    #print(list(messages.get_messages(request)))
    return render(request,'hsn_users/home.html')

# Users roles & permissions
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_viewer(user):
    return user.groups.filter(name='Viewer').exists()

@login_required
@user_passes_test(is_admin)
def admin_view(request):
    # Use admin_dashboard.html for Admin users
    return render(request, 'admin_dashboard.html')

@login_required
@user_passes_test(is_viewer)
def viewer_view(request):
    # Use viewer_dashboard.html for Viewer users
    return render(request, 'viewer_dashboard.html')

@login_required
def dashboard(request):
    if request.user.groups.filter(name='Admin').exists():
        # Admin users can see everything
        return render(request, 'hsn_users/admin_dashboard.html')
    elif request.user.groups.filter(name='Viewer').exists():
        # Viewers get read-only information
        return render(request, 'hsn_users/viewer_dashboard.html')
    else:
        return HttpResponseForbidden("You do not have permission to access this page.")

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
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('dashboard')  # Redirect to dashboard after login
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'hsn_users/login.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_view(request):
    # This view is restricted to Admin users only
    return render(request, 'admin_page.html')

@login_required
@user_passes_test(is_viewer)
def viewer_view(request):
    # This view is restricted to Viewer users only
    return render(request, 'viewer_page.html')

# Uploading Database 
@login_required
@user_passes_test(is_admin)
def upload_excel(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_path = default_storage.save(f'uploads/{uploaded_file.name}', uploaded_file)
            rows_processed = 0
            status = 'SUCCESS'
            error_message = None

            try:
                # Determine the file extension
                _, file_extension = os.path.splitext(uploaded_file.name)

                # Use the appropriate method for reading the Excel file
                if file_extension == '.xls':
                    # Load .xls file using pyexcel
                    df = pd.read_excel(file_path, engine='xlrd')
                elif file_extension == '.xlsx':
                    # Load .xlsx file using Pandas with openpyxl
                    df = pd.read_excel(file_path, engine='openpyxl')
                else:
                    raise ValueError("Unsupported file type. Please upload an .xls or .xlsx file.")

                # Define ID counter and parentId logic
                id_counter = 100  # Start ID from 100
                last_id_per_column = {}  # Dictionary to store the last used ID for each column index
                last_column_index = -1  # Initialize with a value less than any valid column index

                # Iterate over each row, adapting the CSV logic to save to the database
                for row_index in range(len(df)):
                    parentId = None  # Reset parentId for each row

                    # Go column by column, from H (last column) to A (first column)
                    for col_index in range(7, -1, -1):  # 7 = column H, 0 = column A
                        value = df.iloc[row_index, col_index]

                        if pd.notna(value):  # If there's a value in the current cell
                            officename = value.replace('"', '').replace(',', ' ')  # Clean the officename
                            official = df.iloc[row_index, 8] if pd.notna(df.iloc[row_index, 8]) else None  # Column I
                            currentRegulations = df.iloc[row_index, 9] if pd.notna(df.iloc[row_index, 9]) else None  # Column J

                            # Determine parentId based on column index comparison
                            if col_index > last_column_index:
                                parentId = last_id_per_column.get(last_column_index, None)
                            
                            elif col_index == last_column_index:
                                # If column index is equal, search for parentId from a previous column
                                for check_index in range(col_index - 1, -1, -1):
                                    if check_index in last_id_per_column:
                                        parentId = last_id_per_column[check_index]
                                        break
                            elif col_index < last_column_index:
                                # If column index is smaller, look backward for a column index that is smaller
                                for check_index in range(col_index - 1, -1, -1):
                                    if check_index in last_id_per_column:
                                        parentId = last_id_per_column[check_index]
                                        break

                            # Save the data directly to the database
                            office, created = dataOffice.objects.update_or_create(
                                id=id_counter,
                                defaults={
                                    'parentId': parentId,
                                    'hierarchies': chr(col_index + 65),  # Convert column index to corresponding letter (A, B, C, ...)
                                    'officename': officename,
                                    'currentRegulations': currentRegulations
                                }
                            )

                            # Insert data into dataOfficial table if necessary
                            if official:
                                dataOfficial.objects.update_or_create(
                                    office=office,
                                    defaults={
                                        'name': official
                                    }
                                )

                            # Update the last ID used for this column
                            last_id_per_column[col_index] = id_counter

                            # Update last_column_index to the current column index
                            last_column_index = col_index

                            # Increment the ID counter
                            id_counter += 1
                            rows_processed += 1

                            # Break after processing the deepest level
                            break

            except Exception as e:
                status = 'FAILED'
                error_message = str(e)

            # Create a log entry for the upload
            DataUploadLog.objects.create(
                user=request.user,
                upload_time=timezone.now(),
                file_name=uploaded_file.name,
                rows_processed=rows_processed,
                status=status,
                error_message=error_message
            )

            # Add success message
            if status == 'SUCCESS':
                messages.success(request, f'Successfully uploaded {rows_processed} rows from {uploaded_file.name}')
            else:
                messages.error(request, f'Failed to upload {uploaded_file.name}: {error_message}')

            # Redirect to the admin dashboard after processing
            return redirect('dashboard')

    return render(request, 'hsn_users/admin_dashboard.html')

