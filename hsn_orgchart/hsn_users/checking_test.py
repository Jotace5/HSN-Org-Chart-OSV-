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

