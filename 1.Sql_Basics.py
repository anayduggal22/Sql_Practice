import sqlite3
import pandas as pd

# Connect to database (creates it if doesn't exist)
conn = sqlite3.connect('college_data.db')
cursor = conn.cursor()

# Create students table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        age         INTEGER,
        branch      TEXT,
        cgpa        REAL,
        city        TEXT,
        year        INTEGER
    )
''')

# Create courses table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        branch      TEXT,
        credits     INTEGER,
        semester    INTEGER
    )
''')

conn.commit()
print("✅ Tables created!")

# Insert student records
students = [
    ('Anay Duggal',    19, 'CSE', 8.9, 'Delhi',     2),
    ('Priya Sharma',   20, 'ECE', 7.5, 'Mumbai',    3),
    ('Rahul Kumar',    21, 'ME',  6.8, 'Chennai',   4),
    ('Sneha Patel',    19, 'CSE', 9.2, 'Pune',      2),
    ('Arjun Singh',    22, 'CE',  7.1, 'Kolkata',   4),
    ('Divya Nair',     20, 'CSE', 8.5, 'Bangalore', 3),
    ('Karan Mehta',    21, 'ECE', 6.9, 'Hyderabad', 4),
    ('Pooja Reddy',    19, 'ME',  8.0, 'Delhi',     2),
    ('Vikram Joshi',   22, 'CSE', 9.5, 'Mumbai',    4),
    ('Aarti Gupta',    20, 'CE',  7.8, 'Chennai',   3),
]

cursor.executemany('''
    INSERT INTO students (name, age, branch, cgpa, city, year)
    VALUES (?, ?, ?, ?, ?, ?)
''', students)

# Insert course records
courses = [
    ('Data Structures',      'CSE', 4, 3),
    ('Algorithms',           'CSE', 4, 4),
    ('Digital Electronics',  'ECE', 3, 3),
    ('Thermodynamics',       'ME',  4, 3),
    ('Machine Learning',     'CSE', 3, 6),
    ('DBMS',                 'CSE', 4, 5),
    ('Signals & Systems',    'ECE', 4, 4),
    ('Fluid Mechanics',      'ME',  3, 4),
]

cursor.executemany('''
    INSERT INTO courses (course_name, branch, credits, semester)
    VALUES (?, ?, ?, ?)
''', courses)

conn.commit()
print("✅ Data inserted!")


print("\n" + "="*50)
print("SELECT QUERIES")
print("="*50)

# SELECT all
print("\n1. All students:")
cursor.execute("SELECT * FROM students")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row}")

# SELECT specific columns
print("\n2. Name and CGPA only:")
cursor.execute('''SELECT name, cgpa 
                FROM students''')

for row in cursor.fetchall():
    print(f"  {row}")

# SELECT with WHERE
print("\n3. CSE students only:")
cursor.execute('''SELECT name, cgpa 
                FROM students 
                WHERE branch = 'CSE'
                ''')
                
for row in cursor.fetchall():
    print(f"  {row}")

# Multiple conditions
print("\n4. CSE students with CGPA > 8.5:")

cursor.execute("""
                    SELECT name, cgpa 
                    FROM students
                    WHERE branch = 'CSE' AND cgpa > 8.5
                    """)
                    
for row in cursor.fetchall():   
    print(f"  {row}")

# ORDER BY
print("\n5. All students sorted by CGPA (highest first):")
cursor.execute('''SELECT name, branch, cgpa 
                FROM students 
                ORDER BY cgpa DESC''')
                
for row in cursor.fetchall():
    print(f"  {row}")

# LIMIT
print("\n6. Top 3 students by CGPA:")
cursor.execute('''SELECT name, cgpa 
                FROM students 
                ORDER BY cgpa DESC 
                LIMIT 3''')
                
for row in cursor.fetchall():
    print(f"  {row}")
    

print("\n" + "="*50)
print("AGGREGATE FUNCTIONS")
print("="*50)

# COUNT
cursor.execute("SELECT COUNT(*) FROM students")
print(f"\n1. Total students: {cursor.fetchone()[0]}")

# AVG
cursor.execute("SELECT AVG(cgpa) FROM students")
print(f"2. Average CGPA: {cursor.fetchone()[0]:.2f}")

# MAX, MIN
cursor.execute("SELECT MAX(cgpa), MIN(cgpa) FROM students")
row = cursor.fetchone()
print(f"3. Max CGPA: {row[0]}, Min CGPA: {row[1]}")

# SUM
cursor.execute("SELECT SUM(credits) FROM courses")
print(f"4. Total course credits: {cursor.fetchone()[0]}")

# GROUP BY
print("\n5. Average CGPA by branch:")
cursor.execute("""
    SELECT branch, AVG(cgpa) as avg_cgpa, COUNT(*) as count
    FROM students
    GROUP BY branch
    ORDER BY avg_cgpa DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0]:5s}: avg={row[1]:.2f}, count={row[2]}")

# HAVING (filter after GROUP BY)
print("\n6. Branches with average CGPA > 7.5:")
cursor.execute("""
    SELECT branch, AVG(cgpa) as avg_cgpa
    FROM students
    GROUP BY branch
    HAVING AVG(cgpa) > 7.5
    ORDER BY avg_cgpa DESC
""")
for row in cursor.fetchall():
    print(f"  {row}")
    

print("\n" + "="*50)
print("SQL + PANDAS INTEGRATION")
print("="*50)

# Load entire table into DataFrame
df = pd.read_sql("SELECT * FROM students", conn)
print("\nLoaded from SQL to pandas:")
print(df.head())
print(df.info())

# Run SQL query and get result as DataFrame
df_cse = pd.read_sql("""
    SELECT name, cgpa, city
    FROM students
    WHERE branch = 'CSE'
    ORDER BY cgpa DESC
""", conn)
print("\nCSE students from SQL:")
print(df_cse)

# Analyse with pandas after SQL query
print(f"\nCSE average CGPA: {df_cse['cgpa'].mean():.2f}")
print(f"CSE top city: {df_cse['city'].mode()[0]}")

# Save DataFrame back to SQL
df_top = df[df['cgpa'] >= 8.5].copy()
df_top.to_sql('top_students', conn, if_exists='replace', index=False)
print(f"\n✅ Saved {len(df_top)} top students to SQL table")

conn.close()
print("\n✅ Done! Database saved as college_data.db")