import pandas as pd
import re

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
# The first word and the second word will be considered if it is "General" or "gral"
def get_hierarchy_type(text):
    if pd.isna(text):
        return None
    
    # Convert text to lowercase and split into words
    words = text.lower().split()
    
    if len(words) == 0:
        return None
    
    # Determine the type of hierarchy
    if len(words) > 1 and (words[1] == "general" or words[1] == "gral"):
        hierarchy_type = f"{words[0]} {words[1]}"
    else:
        hierarchy_type = words[0]
    
    # Normalize using the hierarchy dictionary
    return hierarchy_dict.get(hierarchy_type, hierarchy_type)

# Function to count the number of hierarchies by type
def count_hierarchies(df):
    counts = {}
    for col in df.columns[:8]:  # Iterate over columns A to H (first 8 columns)
        for value in df[col]:
            hierarchy_type = get_hierarchy_type(value)
            if hierarchy_type:
                if hierarchy_type in counts:
                    counts[hierarchy_type] += 1
                else:
                    counts[hierarchy_type] = 1
    return counts

# Load the Excel file
current_file = "../../data/test_xls_fulldata.xls"
df_current = pd.read_excel(current_file)

# Count the hierarchies in the current file
current_counts = count_hierarchies(df_current)

# Count the total number of rows with any data
total_rows_with_data = df_current.dropna(how='all').shape[0]

# Display statistics of the current file
print("\nStatistics of the current file:")
for hierarchy_type, count in current_counts.items():
    print(f"- {hierarchy_type}: {count}")
print(f"- Total data in the file: {total_rows_with_data}")





#archivo_actual = "../../data/test_xls_fulldata.xls"
#archivo_previo = "../../data/test_xls_11cols.xls"

@login_required
@user_passes_test(is_admin)
def upload_excel(request):
    if request.method == 'POST':
        # Start the upload process
        print("Upload process started")

        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            print(f"File received: {uploaded_file.name}, size: {uploaded_file.size} bytes")
            
            # Step 1: Call the checker_file function and check the file status
            print("Calling to verify file...")
            df_data_to_check, status = checker_file(uploaded_file)

            # Initialize error_message to an empty string
            error_message = ''
            
            if status.startswith("Error"):
                # Print the error message from the checker_file function
                print(f"Error during file check: {status}")
                messages.error(request, status)
                return redirect('dashboard')

            # Step 2: Direct upload or comparison logic
            print(f"File check status: {status}")
            if status == "Direct upload":
                try:
                    print("Starting direct upload process...")
                    
#-----------------------------------------------------------------------------------------------
                    # Add some variables for debugging
                    id_counter = 100
                    rows_processed = 0  # Initialize row counter
                    last_id_per_column = {}
                    last_column_index = -1

                    # Iterate over each row
                    for row_index in range(len(df_data_to_check)):
                        parentId = None
                        print(f"Processing row {row_index}...")

                        # Process the columns from H to A
                        for col_index in range(7, -1, -1):
                            value = df_data_to_check.iloc[row_index, col_index]
                            print(f"Row {row_index}, Column {col_index}: Value = {value}")

                            if pd.notna(value):
                                officename = value.replace('"', '').replace(',', ' ')
                                official = df_data_to_check.iloc[row_index, 8] if pd.notna(df_data_to_check.iloc[row_index, 8]) else None
                                currentRegulations = df_data_to_check.iloc[row_index, 9] if pd.notna(df_data_to_check.iloc[row_index, 9]) else None

                                # Print values being processed
                                print(f"Processing: officename={officename}, official={official}, currentRegulations={currentRegulations}")

                                # Determine the parentId
                                if col_index > last_column_index:
                                    parentId = last_id_per_column.get(last_column_index, None)
                                elif col_index == last_column_index:
                                    for check_index in range(col_index - 1, -1, -1):
                                        if check_index in last_id_per_column:
                                            parentId = last_id_per_column[check_index]
                                            break

                                print(f"Determined parentId: {parentId}")

                                # Save the data to the database
                                office, created = dataOffice.objects.update_or_create(
                                    id=id_counter,
                                    defaults={
                                        'parentId': parentId,
                                        'hierarchies': chr(col_index + 65),  # A, B, C...
                                        'officename': officename,
                                        'currentRegulations': currentRegulations
                                    }
                                )

                                if official:
                                    dataOfficial.objects.update_or_create(
                                        office=office,
                                        defaults={
                                            'name': official
                                        }
                                    )

                                last_id_per_column[col_index] = id_counter
                                last_column_index = col_index
                                id_counter += 1
                                rows_processed += 1
                                print(f"Row processed successfully: {rows_processed} rows processed so far.")
                                break
#------------------------------------------------------------------------------------------------------
                    # Set success status
                    status = 'SUCCESS'
                    error_message = ''
                except Exception as e:
                    # Catch any exceptions and print the error message
                    status = 'FAILED'
                    error_message = str(e)
                    print(f"Error during upload process: {error_message}")

                # Log the upload status
                DataUploadLog.objects.create(
                    user=request.user,
                    upload_time=timezone.now(),
                    file_name=uploaded_file.name,
                    rows_processed=rows_processed,
                    status=status,
                    error_message=error_message
                )

            # Add success or error message for frontend
            if status == 'SUCCESS':
                print(f"Upload completed successfully: {rows_processed} rows processed.")
                messages.success(request, f'Successfully uploaded {rows_processed} rows from {uploaded_file.name}')
            else:
                print(f"Upload failed: {error_message}")
                messages.error(request, f'Failed to upload {uploaded_file.name}: {error_message}')

            return redirect('dashboard')

    return render(request, 'hsn_users/admin_dashboard.html')