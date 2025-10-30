def save_student_data(student_id, name, class_name, subjects, filename="students_data.json"):
    import json
    import os

    # Create a dictionary for the student
    student_record = {
        "id": student_id,
        "name": name,
        "class": class_name,
        "subjects": subjects
    }

    student_data = []  

    student_data.append(student_record)  # Add the student record


    # Load existing data if file exists
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Append new student record
    data.append(student_record)

    # Save back to file
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Student data for {name} saved successfully.")

student_data = [
    {
        "id": 1,
        "name": "Amanda Onipe",
        "age": 16,
        "class": "SS2",
        "course":"science",
        "gender": "Female",
        "guardian": {
            "name": "Mrs. Onipe", 
            "contact": "+233501234567"
        },
        "attendance": [
            {"date": "2025-01-10", "status": "Present"},
            {"date": "2025-01-11", "status": "Present"}
        ],
        "fees": {
            "SS1": {
                "first_term": {"amount_due": 1200, "amount_paid": 1200, "status": "Paid"},
                "second_term": {"amount_due": 1200, "amount_paid": 1200, "status": "Paid"}
            },
            "SS2": {
                "first_term": {"amount_due": 1500, "amount_paid": 1000, "status": "Partial"},
                "second_term": {"amount_due": 1500, "amount_paid": 0, "status": "Unpaid"}
            }
        },
        "results": {
            "SS1": {
                "first_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "A", "score": 90},
                        {"name": "English", "grade": "B", "score": 70}
                    ],
                    "average_score": 80
                },
                "second_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "A", "score": 92},
                        {"name": "English", "grade": "B", "score": 75}
                    ],
                    "average_score": 83.5
                }
            },
            "SS2": {
                "first_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "A", "score": 88},
                        {"name": "English", "grade": "A", "score": 82}
                    ],
                    "average_score": 85
                },
                "second_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "-", "score": None},
                        {"name": "English", "grade": "-", "score": None}
                    ],
                    "average_score": None
                }
            }
        }
    },
    {
        "id": 2,
        "name": "Kwame Asante",
        "age": 17,
        "class": "SS2",
        "course": "science",
        "gender": "Male",
        "guardian": {
            "name": "Mr. Asante",
            "contact": "+233208765432"
        },
        "attendance": [
            {"date": "2025-01-10", "status": "Absent"},
            {"date": "2025-01-11", "status": "Present"}
        ],
        "fees": {
            "SS1": {
                "first_term": {"amount_due": 1200, "amount_paid": 1200, "status": "Paid"},
                "second_term": {"amount_due": 1200, "amount_paid": 1200, "status": "Paid"}
            },
            "SS2": {
                "first_term": {"amount_due": 1500, "amount_paid": 1500, "status": "Paid"},
                "second_term": {"amount_due": 1500, "amount_paid": 0, "status": "Unpaid"}
            }
        },
        "results": {
            "SS1": {
                "first_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "B", "score": 75},
                        {"name": "English", "grade": "A", "score": 85}
                    ],
                    "average_score": 80
                },
                "second_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "A", "score": 90},
                        {"name": "English", "grade": "A", "score": 88}
                    ],
                    "average_score": 89
                }
            },
            "SS2": {
                "first_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "B", "score": 78},
                        {"name": "English", "grade": "A", "score": 84}
                    ],
                    "average_score": 81
                },
                "second_term": {
                    "subjects": [
                        {"name": "Mathematics", "grade": "-", "score": None},
                        {"name": "English", "grade": "-", "score": None}
                    ],
                    "average_score": None
                }
            }
        }
    },
]

def get_students_in_class(class_name):
    """
    Returns a list of student names in a given class.
    """
    students_in_class = [
        student["name"]
        for student in student_data
        if student["class"].lower() == class_name.lower()
    ]
    
    if not students_in_class:
        return f"No students found in {class_name}."
    return students_in_class


def get_student_results(student_id):
    """
    Returns all results (all terms and levels) for a given student ID.
    """
    for student in student_data:
        if student["id"] == student_id:
            return student["results"]
    return f"No student found with ID {student_id}"


def get_student_info(student_id):
    """
    Returns details (age, class, ID, etc ) for one student.
    """
    for student in student_data:
        if student["id"] == student_id:
            return {
                "id": student["id"],
                "name": student["name"],
                "class": student["class"],
                "age": student.get("age", "N/A"),
                "attendance_count": len(student.get("attendance", [])),
                "has_results": "Yes" if "results" in student else "No"
            }
    return f"No student found with ID {student_id}."

courses = { 
    "science" : [ 
        { "core" :"English"},
        { "core" :"Mathematice"},
        { "core" :"Chemistry"},
        { "core" : "Phyiscs"},
        { "core" :"Biology"},
        { "core" :" Technical Drawing"},
    ],
        
    "arts" : [
        { "core" :"English"},
        { "core" :"Mathematice"},
        { "core" :"Literature"},
        { "core" :"Government"},
        { "core" :"History"},
        { "core" :"Fine Art/Music"}
  ],
     
    "commerce" : [
        { "core" :"Commerce" },
        { "core" :"English"},
        { "core" :"Mathematics"},
        { "core" :"Office Practice"},
        { "core" :"Marketing"},
        { "core" :"Economics"}
  ],
}

def get_subjects_for_student(student_id):
    """
    Returns the subjects for the student's course.
    """
    for student in student_data:
        if student["id"] == student_id:
            course = student["course"].lower()
            if course in courses:
                subjects = [s["core"] for s in courses[course]]
                return {
                    "student": student["name"],
                    "course": course.title(),
                    "subjects": subjects
                }
            else:
                return {"message": f"Course '{course}' not found."}
    return {"message": "Student not found."}

def get_subjects_for_course(course_name: str):
    """
    Returns a list of core subjects offered in the specified course
    """
    course_name = course_name.lower()
    if course_name in courses:
        return [s["core"] for s in courses[course_name]]
    return f"No subjects found for course '{course_name}'."