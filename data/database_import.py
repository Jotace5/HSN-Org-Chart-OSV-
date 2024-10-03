import csv
import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('hsn_dosa_database.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Office (
        id INTEGER PRIMARY KEY,
        parentId INTEGER,
        hierarchies TEXT NOT NULL,
        officename TEXT NOT NULL,
        currentRegulations TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Official (
        id INTEGER PRIMARY KEY,
        office_id INTEGER REFERENCES Office(id),
        name TEXT NOT NULL
    )
''')

# Open and read the CSV file
with open('hsn-org-est(9-24).csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)
    
    for row in csvreader:
        # Insert data into Office table
        cursor.execute('''
            INSERT INTO Office (id, parentId, hierarchies, officename, currentRegulations)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['id'], row['parentId'], row['hierarchies'], row['officename'], row['currentRegulations']))
        
        # Insert data into Official table if necessary (assuming official name is in CSV)
        if row['official']:
            cursor.execute('''
                INSERT INTO Official (office_id, name)
                VALUES (?, ?)
            ''', (row['id'], row['official']))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data inserted successfully into the database!")