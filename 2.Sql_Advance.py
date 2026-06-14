import sqlite3
import pandas as pd

conn = sqlite3.connect('College_Advanced.db')
cursor = conn.cursor()

# Students Table
cursor.execute('''
               CREATE TABLE IF NOT EXISTS Students
               (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   age INTEGER,
                   branch TEXT,
                   cgpa REAL,
                   city TEXT,
                   year INTEGER,
                   gender TEXT
               )
               ''')

# Courses Table
cursor.execute('''
               CREATE TABLE IF NOT EXISTS Courses
               (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   course_name TEXT NOT NULL,
                   branch TEXT,
                   credits INTEGER,
                   semester INTEGER
               )
               ''')

# Grades Table (links students and courses)
cursor.execute('''
               CREATE TABLE IF NOT EXISTS Grades
               (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   student_id INTEGER,
                   course_id INTEGER,
                   marks REAL,
                   grade TEXT,
                   FOREIGN KEY (student_id) REFERENCES Students(id),
                   FOREIGN KEY (course_id) REFERENCES Courses(id)
               )
               ''')

# Placements Table
cursor.execute('''
               CREATE TABLE IF NOT EXISTS Placements
               (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   student_id INTEGER UNIQUE,
                   company TEXT,
                   package_lpa REAL,
                   year INTEGER,
                   FOREIGN KEY (student_id) REFERENCES Students(id)
               )
               ''')

conn.commit()
print('\n\n Tables Created!')


# Insert Data
students = [
    ('Anay Duggal',    19, 'CSE', 8.9, 'Delhi',     2, 'M'),
    ('Priya Sharma',   20, 'ECE', 7.5, 'Mumbai',    3, 'F'),
    ('Rahul Kumar',    21, 'ME',  6.8, 'Chennai',   4, 'M'),
    ('Sneha Patel',    19, 'CSE', 9.2, 'Pune',      2, 'F'),
    ('Arjun Singh',    22, 'CE',  7.1, 'Kolkata',   4, 'M'),
    ('Divya Nair',     20, 'CSE', 8.5, 'Bangalore', 3, 'F'),
    ('Karan Mehta',    21, 'ECE', 6.9, 'Hyderabad', 4, 'M'),
    ('Pooja Reddy',    21, 'ME',  8.0, 'Delhi',     4, 'F'),
    ('Vikram Joshi',   22, 'CSE', 9.5, 'Mumbai',    4, 'M'),
    ('Aarti Gupta',    20, 'CE',  7.8, 'Chennai',   3, 'F'),
    ('Rohan Verma',    21, 'CSE', 7.2, 'Delhi',     4, 'M'),
    ('Meera Iyer',     19, 'ECE', 8.8, 'Bangalore', 2, 'F'),
]

cursor.executemany('''
                   INSERT INTO Students(
                       name,age,branch,cgpa,city,year,gender
                   )
                   VALUES (?,?,?,?,?,?,?)
                   ''', students)


courses = [
    ('Data Structures', 'CSE', 4, 3),
    ('Algorithms',      'CSE', 4, 4),
    ('DBMS',            'CSE', 4, 5),
    ('Machine Learning','CSE', 3, 6),
    ('Digital Electronics', 'ECE', 3, 3),
    ('Thermodynamics',  'ME',  4, 3),
]

cursor.executemany('''
                   INSERT INTO Courses(
                       course_name,branch,credits,semester
                   )
                   VALUES (?,?,?,?)
                   ''', courses)

grades_data = [
    (1,1,85,'A'), (1,2,78,'B'), (1,3,92,'A'),
    (2,5,74,'B'), (2,5,68,'C'),
    (3,6,71,'B'),
    (4,1,95,'A'), (4,2,88,'A'), (4,3,91,'A'),
    (5,1,65,'C'),
    (6,1,87,'A'), (6,2,82,'A'),
    (7,5,70,'B'),
    (8,6,78,'B'),
    (9,1,98,'A'), (9,2,95,'A'), (9,3,97,'A'),
    (10,1,80,'A'),
    (11,1,72,'B'), (11,2,68,'C'),
    (12,5,90,'A'),
]

cursor.executemany('''
                   INSERT INTO Grades(
                       student_id, course_id,marks,grade
                   )
                   VALUES (?,?,?,?)
                   ''', grades_data)


placements = [
    (3,  'TCS',       5.5,  2024),
    (5,  'Infosys',   6.0,  2024),
    (7,  'Wipro',     4.5,  2024),
    (8,  'L&T',       7.0,  2024),
    (9,  'Google',    45.0, 2024),
    (11, 'Cognizant', 4.8,  2024),
]

cursor.executemany('''
                   INSERT INTO Placements(
                       student_id,company,package_lpa,year
                   )
                   VALUES (?,?,?,?)
                   ''', placements)

conn.commit()
print('Data Inserted!')

# JOIN Queries

print("\n" + "="*55)
print("JOIN QUERIES")
print("="*55)

# INNER JOIN - Students with their grades
print('\n1. Students with their course grades:')
cursor.execute('''
               SELECT s.name, c.course_name,g.marks,g.grade
                FROM Students AS s
                INNER JOIN Grades AS g 
                ON s.id = g.student_id
                INNER JOIN Courses AS c
                ON g.course_id = c.id
                ORDER BY s.name, g.marks DESC
               ''')

for row in cursor.fetchall():
    print(f' {row}')

# LEFT JOIN — all students, placement if exists
print("\n2. All students with placement status:")
cursor.execute('''
    SELECT s.name, s.branch, s.cgpa,
           COALESCE(p.company, 'Not Placed') AS company,
           COALESCE(p.package_lpa, 0) AS package
    FROM students s
    LEFT JOIN placements p ON s.id = p.student_id
    ORDER BY p.package_lpa DESC
''')
for row in cursor.fetchall():
    print(f"  {row}")

# Students NOT placed
print("\n3. Students NOT placed yet:")
cursor.execute('''
    SELECT s.name, s.branch, s.cgpa
    FROM students s
    LEFT JOIN placements p ON s.id = p.student_id
    WHERE p.student_id IS NULL
    ORDER BY s.cgpa DESC
''')
for row in cursor.fetchall():
    print(f"  {row}")
    
    
    

# SubQueries

print("\n" + "="*55)
print("SUBQUERIES")
print("="*55)

# Students above average CGPA
print('\n1. Students above average CGPA')
cursor.execute('''
               SELECT name, branch, cgpa
               FROM Students
               WHERE cgpa > (SELECT AVG(cgpa) FROM Students)
               ORDER BY cgpa DESC
               ''')

for row in cursor.fetchall():
    print(f'    {row}')
    
# Highest package in each branch
print("\n2. Top placements:")
cursor.execute('''
    SELECT s.name, s.branch, p.company, p.package_lpa
    FROM students s
    INNER JOIN placements p ON s.id = p.student_id
    WHERE p.package_lpa = (SELECT MAX(package_lpa) FROM placements)
''')
for row in cursor.fetchall():
    print(f"  {row}")

# Students who scored A in ALL their courses
print("\n3. Students with ALL A grades:")
cursor.execute('''
    SELECT s.name, s.cgpa
    FROM students s
    WHERE s.id IN (
        SELECT student_id FROM grades
        GROUP BY student_id
        HAVING MIN(grade) = 'A'
    )
''')
for row in cursor.fetchall():
    print(f"  {row}") 
    
    


print("\n" + "="*55)
print("ADVANCED AGGREGATIONS")
print("="*55)

# Branch-wise statistics
print("\n1. Branch statistics:")
cursor.execute('''
    SELECT
        branch,
        COUNT(*)              AS total,
        ROUND(AVG(cgpa), 2)   AS avg_cgpa,
        MAX(cgpa)             AS top_cgpa,
        MIN(cgpa)             AS lowest_cgpa,
        COUNT(CASE WHEN cgpa >= 8.0 THEN 1 END) AS distinction_count
    FROM students
    GROUP BY branch
    ORDER BY avg_cgpa DESC
''')
for row in cursor.fetchall():
    print(f"  {row}")

# Placement statistics
print("\n2. Placement statistics:")
cursor.execute('''
    SELECT
        COUNT(*) AS placed_count,
        ROUND(AVG(package_lpa), 2) AS avg_package,
        MAX(package_lpa) AS highest_package,
        MIN(package_lpa) AS lowest_package
    FROM placements
''')
print(f"  {cursor.fetchone()}")

# Average marks per course
print("\n3. Course-wise performance:")
cursor.execute('''
    SELECT
        c.course_name,
        COUNT(g.id)            AS students_enrolled,
        ROUND(AVG(g.marks), 2) AS avg_marks,
        MAX(g.marks)           AS highest,
        MIN(g.marks)           AS lowest
    FROM courses c
    LEFT JOIN grades g ON c.id = g.course_id
    GROUP BY c.id, c.course_name
    ORDER BY avg_marks DESC
''')
for row in cursor.fetchall():
    print(f"  {row}")
    
    
    
print("\n" + "="*55)
print("SQL + PANDAS")
print("="*55)

# Full student-placement report
df = pd.read_sql('''
    SELECT
        s.name, s.branch, s.cgpa, s.city,
        COALESCE(p.company, 'Not Placed') AS company,
        COALESCE(p.package_lpa, 0) AS package_lpa
    FROM students s
    LEFT JOIN placements p ON s.id = p.student_id
    ORDER BY s.cgpa DESC
''', conn)

print("\nFull report:")
print(df.to_string(index=False))

# Analyse with pandas
print(f"\nPlacement rate: {(df['package_lpa'] > 0).mean():.1%}")
print(f"Average package (placed only): "
      f"₹{df[df['package_lpa']>0]['package_lpa'].mean():.2f} LPA")
print(f"\nBranch-wise CGPA:")
print(df.groupby('branch')['cgpa'].mean().round(2))

# Save to CSV
df.to_csv('student_report.csv', index=False)
print("\n✅ Report saved!")

conn.close()
    