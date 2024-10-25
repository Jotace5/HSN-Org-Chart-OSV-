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
from django.http import JsonResponse # For Get_chart_data function (NOT WORKING YET)
import logging
import re
import sqlite3
import tempfile

logger = logging.getLogger(__name__) 

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

#-----------------------------------------------------------------------------------------------------------------
# Data Extraction and Normalization
# Dictionary to normalize hierarchy terms
hierarchy_dict = {
    "honorable": "honorable",
    "presidencia": "presidencia",
    "prosecretaria": "prosecretaria",
    "prosec.": "prosecretaria",
    "secretaría": "secretaría",
    "dirección general": "dirección general",
    "observatorio": "observatorio",
    "coord.": "coordinación",
    "subdirección general": "subdirección general",
    "subirección general": "subdirección general",
    "subdirección": "subdirección",
    "dirección": "dirección",
    "cuerpo": "cuerpo",
    "oficina": "oficina",
    "coordinación general": "coordinación general",
    "coordinación": "coordinación",
    "subdireccion": "subdirección",
    "subdir.": "subdirección",
    "subcoord. general": "subcoordinación general",
    "subdireción": "subdirección",
    "departamento": "departamento",
    "unidad": "unidad",
    "dpto.": "departamento",
    "depto.": "departamento",
    "depto": "departamento",
    "división": "división",
    "division": "división"
}

# Function to determine the type of hierarchy based on the first words
def get_hierarchy_type(text):
    if pd.isna(text):
        return None

    # Convert text to lowercase if it is a string
    if isinstance(text, str):
        words = text.lower().split()
    else:
        return None

    if len(words) == 0:
        return None

    # Extract either the first word or the first two words if it's "general" or "gral"
    if len(words) > 1 and (words[1] == "general" or words[1] == "gral"):
        hierarchy_type = f"{words[0]} {words[1]}"
    else:
        hierarchy_type = words[0]

    # Normalize using the hierarchy dictionary to handle similar terms or typos
    return hierarchy_dict.get(hierarchy_type, hierarchy_type)

# Function to count the number of hierarchies by type
def count_hierarchies(data):
    counts = {}
    for value in data:
        # Use get_hierarchy_type() to get the standardized hierarchy type
        hierarchy_type = get_hierarchy_type(value)
        if hierarchy_type:
            if hierarchy_type in counts:
                counts[hierarchy_type] += 1
            else:
                counts[hierarchy_type] = 1
    return counts

#----------------------------------------------------------------------------
# Define the checker_file function
def checker_file(uploaded_file):
    check_messages = []

    # Step 1: Determine the file extension
    _, file_extension = os.path.splitext(uploaded_file.name)
    if file_extension not in ['.xls', '.xlsx']:
        return None, "Error: Unsupported file type. Please upload an .xls or .xlsx file."

    # Step 2: Load the Excel file
    try:
        if file_extension == '.xls':
            df_data_to_check = pd.read_excel(uploaded_file, engine='xlrd')
        elif file_extension == '.xlsx':
            df_data_to_check = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        return None, f"Error: Could not load the file. Format differences: {str(e)}"

    # Step 3: Check if there is data in the database
    existing_data = dataOffice.objects.exists()
#---------------------------------------------------------ADD STEP
# Luego de normalizar los datos (usando el diccionario de jerarquias)
# Chequear si las primera palabra y la segunda (si 2da=General) corresponde a cada columna en el dataset
# B= Presidencia, Secretaria, Prosecretaria, etc
# C= Direccion general
# D= Subdireccion general
# E= Direccion
# F= Subdireccion
# G= Departamento
# H= Division 
# Si no coinciden mostrar la primera palabra contrastada con la que deberia ser para que el usaurio cargue los datos
#---------------------------------------------------------
    if existing_data:
        return df_data_to_check, "Comparison required"
    else:
        return df_data_to_check, "Direct upload"
    
    

def extract_database_statistics():
    try:
        # Extract only the relevant fields (excluding 'id' and 'parentId')
        data = list(dataOffice.objects.values_list('officename', 'hierarchies', 'currentRegulations'))

        # Flatten the list and filter out None values
        data = [item for sublist in data for item in sublist if item is not None]
        
        # Process each value to extract the hierarchy type (first word or first two words)
        hierarchy_types = [get_hierarchy_type(value) for value in data]

        # Count the occurrences of each hierarchy type
        db_counts = count_hierarchies(hierarchy_types)

        # Count the total number of rows in the database with valid data
        total_db_rows_with_data = dataOffice.objects.exclude(officename__isnull=True).count()
        
        return db_counts, total_db_rows_with_data

    except Exception as e:
        print(f"Error extracting database statistics: {str(e)}")
        return {}, 0

def extract_file_statistics(df_data_to_check):
    data_from_file = df_data_to_check.iloc[:, :8].values.flatten()
    data_from_file = [item for item in data_from_file if pd.notna(item)]
    file_counts = count_hierarchies(data_from_file)
    total_file_rows = df_data_to_check.dropna(how='all').shape[0]
    return file_counts, total_file_rows  
  
#----------------------------------------------------------------------------------------------------
class TreeNode:
    def __init__(self, name, level, official=None, current_regulations=None):
        self.name = name
        self.level = level  # Represents the column level (A, B, C, etc.)
        self.children = []
        self.parent = None
        self.official = official
        self.currentRegulations = current_regulations
        self.id = None  # To be assigned when saving to the database

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

def build_tree(df_data_to_check):
    # Initialize root node once
    root = TreeNode(name="Honorable Senado de la Nacion", level='A')
    node_map = {'A': root}  # Dictionary to keep track of nodes per level

    # Iterate over each row of the DataFrame
    for row_index in range(len(df_data_to_check)):
        for col_index in range(8):  # Columns A to H (0-7)
            value = df_data_to_check.iloc[row_index, col_index]

            if pd.notna(value):
                # Skip creating a new node for the root node again
                if col_index == 0 and value == "Honorable Senado de la Nacion":
                    continue  # Root node is already created

                # Clean and prepare the data
                node_name = value.replace('"', '').replace(',', ' ')
                official = df_data_to_check.iloc[row_index, 8] if pd.notna(df_data_to_check.iloc[row_index, 8]) else None
                current_regulations = df_data_to_check.iloc[row_index, 9] if pd.notna(df_data_to_check.iloc[row_index, 9]) else None

                # Create the new node for the current value
                new_node = TreeNode(name=node_name, level=chr(col_index + 65), official=official, current_regulations=current_regulations)

                # Determine the appropriate parent
                if col_index == 0:
                    # If it's column A, it's the root and has no parent
                    parent_node = None
                else:
                    # Check previous columns for the appropriate parent
                    parent_node = None
                    for prev_col in range(col_index - 1, -1, -1):
                        if chr(prev_col + 65) in node_map:
                            parent_node = node_map[chr(prev_col + 65)]
                            break

                # If we found a parent, add the new node as a child of that parent
                if parent_node:
                    parent_node.add_child(new_node)
                else:
                    # If no valid parent found, add as a child of the root
                    root.add_child(new_node)

                # Update the node_map with the new node for the current level
                node_map[chr(col_index + 65)] = new_node

    return root

def save_tree_to_db(root):
    id_counter = 100  # Initial ID for nodes
    rows_processed = 0  # Counter to track rows processed

    def save_node(node, parent_id=None):
        nonlocal id_counter, rows_processed

        # Save the node to the database
        office, created = dataOffice.objects.update_or_create(
            id=id_counter,
            defaults={
                'parentId': parent_id,
                'hierarchies': node.level,
                'officename': node.name,
                'currentRegulations': node.currentRegulations
            }
        )

        # Save the official if available
        if node.official:
            dataOfficial.objects.update_or_create(
                office=office,
                defaults={'name': node.official}
            )

        # Log node details for debugging
        print(f"Node saved: ID={id_counter}, Name={node.name}, ParentID={parent_id}, Level={node.level}")

        # Assign the current ID to the node and increment the counter
        node.id = id_counter
        id_counter += 1
        rows_processed += 1

        # Recursively save all children
        for child in node.children:
            save_node(child, parent_id=node.id)

    # Start saving from the root
    save_node(root)

    # Return the number of rows processed to log it later
    return rows_processed

def process_and_upload_data(request, df_data_to_check, file_name):
    try:
        # Step 1: Build the tree from the DataFrame
        print("Building the tree structure from the data...")
        root = build_tree(df_data_to_check)

        # Step 2: Save the tree to the database
        print("Saving the tree structure to the database...")
        rows_processed = save_tree_to_db(root)

        # If everything goes well
        status = 'SUCCESS'
        error_message = ''

    except Exception as e:
        # Handle exceptions during processing
        status = 'FAILED'
        error_message = str(e)
        print(f"Error during upload process: {error_message}")
        rows_processed = 0

    # Log the upload status
    DataUploadLog.objects.create(
        user=request.user,
        upload_time=timezone.now(),
        file_name=file_name,
        rows_processed=rows_processed,
        status=status,
        error_message=error_message
    )

    # Send success or failure message to the user
    if status == 'SUCCESS':
        print(f"Upload completed successfully: {rows_processed} nodes processed.")
        messages.success(request, f'Successfully uploaded {rows_processed} nodes from {file_name}')

        # Cleanup temporary file after successful upload
        temp_file_path = request.session.get('temp_file_path')
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Temporary file '{temp_file_path}' has been removed.")
    
    else:
        print(f"Upload failed: {error_message}")
        messages.error(request, f'Failed to upload {file_name}: {error_message}')

    return redirect('dashboard')


  
#-------------------------------------------------------------------------------------------------------------
@login_required
@user_passes_test(is_admin)
def upload_excel(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            df_data_to_check, status = checker_file(uploaded_file)

            if status.startswith("Error"):
                messages.error(request, status)
                return redirect('dashboard')

            if status == "Comparison required":
                # Comparison flow stays the same
                db_counts, total_db_rows = extract_database_statistics()
                file_counts, total_file_rows = extract_file_statistics(df_data_to_check)
                
                # Render comparison page
                context = {
                    'db_counts': db_counts,
                    'total_db_rows': total_db_rows,
                    'file_counts': file_counts,
                    'total_file_rows': total_file_rows,
                    'uploaded_file_name': uploaded_file.name,
                }
                
                # Save the uploaded file to a temporary location for later use
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(temp_file_path, 'wb') as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                
                request.session['temp_file_path'] = temp_file_path
                request.session['file_name'] = uploaded_file.name
                request.session['file_extension'] = os.path.splitext(uploaded_file.name)[1]

                return render(request, 'hsn_users/confirm_upload.html', context)

            elif status == "Direct upload":
                # Proceed with the tree construction and data upload
                return process_and_upload_data(request, df_data_to_check, uploaded_file.name)

    return render(request, 'hsn_users/admin_dashboard.html')


@login_required
@user_passes_test(is_admin)
def confirm_upload(request):
     if request.method == 'POST':
        # Retrieve the temporary file path, file extension, and file name from the session
        temp_file_path = request.session.get('temp_file_path')
        file_name = request.session.get('file_name')
        file_extension = request.session.get('file_extension')

        if not temp_file_path or not file_name or not os.path.exists(temp_file_path):
            messages.error(request, 'No uploaded file found or file is missing. Please try again.')
            return redirect('dashboard')

        # Load the file from the temporary location into a DataFrame using the correct engine
        try:
            if file_extension == '.xls':
                # Load the file using xlrd engine
                df_data_to_check = pd.read_excel(temp_file_path, engine='xlrd')
            elif file_extension == '.xlsx':
                # Load the file using openpyxl engine
                df_data_to_check = pd.read_excel(temp_file_path, engine='openpyxl')
            else:
                messages.error(request, 'Unsupported file type. Please upload a valid Excel file.')
                return redirect('dashboard')

            # Proceed to upload
            return process_and_upload_data(request, df_data_to_check, file_name)

        except Exception as e:
            messages.error(request, f'Error reading file: {str(e)}')
            return redirect('dashboard')

     return redirect('dashboard')
 

#------------------------------------------------------------------------------------------------------------------------------------------------
@login_required
@user_passes_test(is_admin)
def approve_update(request):
    # For now, let's just simulate approval by adding a message
    if request.method == 'GET':
        # Add a success message to confirm that changes were approved
        messages.success(request, "Changes have been approved and successfully applied.")
    
    # Redirect to the admin dashboard after approval
    return redirect('dashboard')

def get_chart_data(request):
    # Example data structure for the organizational chart
    data = {
        "nodes": [
            {"id": 1, "name": "Department A", "parentId": None},
            {"id": 2, "name": "Department B", "parentId": 1},
            {"id": 3, "name": "Department C", "parentId": 1},
            {"id": 4, "name": "Department D", "parentId": 2},
        ]
    }
    
    return JsonResponse(data)