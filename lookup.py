import sqlite3
import json
import xml.etree.ElementTree as ET

try:
    conn = sqlite3.connect("HyperionDev.db")
except sqlite3.Error:
    print("Please store your database as HyperionDev.db")
    quit()

cur = conn.cursor()  
    
with open('create_database.sql','r') as file:
    sql_lines = file.read()
sqlCommands = sql_lines.split(';')

# Execute every command from the input file
for command in sqlCommands:
    # This will skip and report errors
    # For example, if the tables do not yet exist, this will skip over
    # the DROP TABLE commands
    try:
        cur.execute(command)
    except FileNotFoundError:
        print("Command skipped: ")
conn.commit()



def usage_is_incorrect(input, num_args):
    if len(input) != num_args + 1:
        print(f"The {input[0]} command requires {num_args} arguments.")
        return True
    return False

def store_data_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file = json.dump(data, file, sort_keys=True, indent=4)
    print("Data stored as JSON file in: ", filename)
    return False

def store_data_as_xml(data, filename):
    root = ET.Element("Data")

    # Iterate through the list and create sub-elements
    for item in data:
        sub_element = ET.SubElement(root, "item")
        sub_element.text = item

    # Create the XML tree
    tree = ET.ElementTree(root)

    # Write the XML tree to a file
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print("Data stored as XML file in: ", filename)
    return False


def offer_to_store(data):
    while True:
        print("Would you like to store this result?")
        choice = input("Y/[N]? : ").strip().lower()

        if choice == "y":
            filename = input("Specify filename. Must end in .xml or .json: ")
            ext = filename.split(".")[-1]
            if ext == 'xml':
                store_data_as_xml(data, filename)
                
            elif ext == 'json':
                store_data_as_json(data, filename)
            else:
                print("Invalid file extension. Please use .xml or .json")

        elif choice == 'n':
            break

        else:
            print("Invalid choice")

usage = '''
What would you like to do?

d - demo
vs <student_id>            - view subjects taken by a student
la <firstname> <surname>   - lookup address for a given firstname and surname
lr <student_id>            - list reviews for a given student_id
lc <teacher_id>            - list all courses taken by teacher_id
lnc                        - list all students who haven't completed their course
lf                         - list all students who have completed their course and achieved 30 or below
e                          - exit this program

Type your option here: '''

print("Welcome to the data querying app!")

while True:
    # Get input from user
    user_input = input(usage).split(" ")
    print("Your input has been processed.")

    # Parse user input into command and args
    command = user_input[0]
    if len(user_input) > 1:
        args = user_input[1:]

    if command == 'd': # demo - a nice bit of code from me to you - this prints all student names and surnames :)
        data = cur.execute('''SELECT * FROM Student''')
        for _, firstname, surname, _, _ in data:
            print(f"{firstname} {surname}")
        
    elif command == 'vs': # view subjects by student_id
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        data = cur.execute('''SELECT Course.course_name FROM Course INNER JOIN StudentCourse
                            ON Course.course_code = StudentCourse.course_code
                            WHERE StudentCourse.student_id=?''', (student_id,))
        print(f'For student ID:{student_id}')
        for course_name in data:
            print(f"Subjects taken: {course_name}")
            
        data  = list(data) 
        offer_to_store(data)
        

    elif command == 'la':# list address by name and surname
        if usage_is_incorrect(user_input, 2):
            continue
        firstname, surname = args[0], args[1]
        data = cur.execute('''SELECT Address.street, Address.city
                            FROM Address INNER JOIN Student
                            ON Address.address_id = Student.address_id
                            WHERE Student.first_name = ? and Student.last_name = ?''', (firstname, surname))

        for street, city in data:
            print(f"Address: {street}, {city}")

        data  = list(data)
        offer_to_store(data)

    elif command == 'lr':# list reviews by student_id
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        data = cur.execute('''SELECT *
                            FROM Review INNER JOIN Student
                            ON Review.student_id = Student.student_id
                            WHERE Student.student_id = ?''', (student_id,))
        for _, *review_text, completeness, efficiency, style, documentation, _, _ in data:
            print(f''' 
                    Completeness: {completeness}
                    Efficiency : {efficiency}
                    Style: {style}
                    Documentation : {documentation}
                    Review: {review_text[0]}''')
        
        data  = list(data)
        offer_to_store(data)
    
    elif command == 'lnc':# list all students who haven't completed their course
        incomplete = 0
        data =cur.execute('''SELECT Student.first_name, Student.last_name,
                            Student.email, Course.course_name
                            FROM Student INNER JOIN StudentCourse
                            ON Student.student_id = StudentCourse.student_id
                            INNER JOIN Course
                            ON StudentCourse.course_code = Course.course_code
                            WHERE StudentCourse.is_complete = ?''', (incomplete,))
        print('Information on Students with complete courses: ')
        for row in data:
            print(f"{row}")

        data  = list(data)
        offer_to_store(data)

    
    elif command == 'lf':# list all students who have completed their course and got a mark <= 30
        complete = 1
        mark = 30
        data = cur.execute('''SELECT Student.first_name, Student.last_name,
                            Student.email, Course.course_name, StudentCourse.mark
                            FROM Student INNER JOIN StudentCourse
                            ON Student.student_id = StudentCourse.student_id
                            INNER JOIN Course
                            ON StudentCourse.course_code = Course.course_code
                            WHERE StudentCourse.is_complete = ? AND StudentCourse.mark <= ?''', (complete, mark))
        print('Students that have completed their course and have a mark <= 30: ')
        for row in data:
            print(f'{row}')
            
        data  = list(data)
        offer_to_store(data)
        
    elif command == 'lc': # list courses given by teacher
        if usage_is_incorrect(user_input, 1):
            continue
        teacher_id = args[0]
        data = cur.execute('''SELECT Course.course_name
                        FROM Course INNER JOIN Teacher
                        ON Course.teacher_id = Teacher.teacher_id''')
        
        print("Courses taught by specified teacher: ")
        for row in data:
            print(f"{row}")
        
        data  = list(data)
        offer_to_store(data)
    
    elif command == 'e':# list address by name and surname
        print("Programme exited successfully!")
        break
    
    else:
        print(f"Incorrect command: '{command}'")
    

    
