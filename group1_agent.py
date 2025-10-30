from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv
load_dotenv()

model = init_chat_model(model = "gpt-4o", model_provider = "openai")

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


def get_students_in_class(class_name:str):
    """
    Returns a list of student names in a given class.

    Args:
        class_name (str)
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


def get_student_info(student_id:int):
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
                "has_results": "Yes" if "results" in student else "No",
                "others" : student
            }
    return f"No student found with ID {student_id}."


def add_new_student(name: str , age :int, student_class:str, course:str, gender:str, guardian_name:str, guardian_contact:str):
    """
    Adds a new student to the student_data list with default attendance, fees, and results structure.
    """
    # Generate a new unique ID
    new_id = max(student["id"] for student in student_data) + 1 if student_data else 1

    # Create the new student dictionary matching your existing structure
    new_student = {
        "id": new_id,
        "name": name,
        "age": age,
        "class": student_class,
        "course": course,
        "gender": gender,
        "guardian": {
            "name": guardian_name,
            "contact": guardian_contact
        },
        "attendance": [],
        "fees": {
            student_class: {
                "first_term": {"amount_due": 0, "amount_paid": 0, "status": "Unpaid"},
                "second_term": {"amount_due": 0, "amount_paid": 0, "status": "Unpaid"}
            }
        },
        "results": {
            student_class: {
                "first_term": {"subjects": [], "average_score": None},
                "second_term": {"subjects": [], "average_score": None}
            }
        }
    }

    # Append to the main student_data list
    student_data.append(new_student)

    

    return f"✅ New student added: {name} (Class: {student_class}, Course: {course})"



def update_fee_status(student_id:int, fees_paid:bool):
    """Updates the fee payment status for a student."""
    for student in student_data:
        if student["id"] == student_id:
            student["fees_paid"] = fees_paid
            return f"Updated fee status for {student['name']}."
    return "Student not found."



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


def get_subjects_for_student(student_id:int):
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


model_with_tools = model.bind_tools([get_students_in_class, get_student_results, get_student_info, add_new_student, update_fee_status, get_subjects_for_student, get_subjects_for_course])


def state_node(state):
    msg = state["messages"]

    system_prompt = """You are an AI-powered School Management Assistant.
    You help teachers and administrators retrieve and update
    student information such as attendance, fees, and results.
    - Always confirm before modifying data.
    - If a question cannot be answered, ask for clarification.
    - Be concise and polite.
    """
    messages = [{"role": "system", "content": system_prompt},
                *msg
    ]
    
    res = model_with_tools.invoke(msg)

    return{"messages":res}


system_prompt = """
You are a helpful and knowledgeable academic assistant for a school management system. Your job is to respond to queries about students, their subjects, results, and courses. You must be clear, concise, and polite in your responses.

Always use the data provided in the system to answer questions. If a student ID or class is missing, ask the user to provide it. If the requested information is not available, say so honestly.

Your tone should be professional but friendly. Avoid slang or overly casual language. When listing subjects or results, format them clearly on a straight line with numbers .


You are also a school assistant bot. Your job is to help users manage student records, including:
- Adding new students
- Updating attendance
- Viewing academic results
- Displaying school fees

When asked about fees, retrieve and display the student's fee status for each term, including:
- Amount Due
- Amount Paid
- Payment Status

Format your responses clearly and politely. If a student ID is not found, notify the user.

Example:
User: What subjects does Amanda do?
Assistant: Amanda Onipe is enrolled in the Science course. The subjects she does are:
1. English
2. Mathematics
3. Chemistry
4. Physics
5. Biology
6. Technical Drawing

Do not make up data.
"""


builder = StateGraph(MessagesState)

builder.add_node("current_state", state_node)
builder.add_node("tools", ToolNode([get_students_in_class, get_student_results, get_student_info, add_new_student, update_fee_status, get_subjects_for_student, get_subjects_for_course]))

builder.add_edge(START, "current_state")
builder.add_conditional_edges("current_state", tools_condition)
builder.add_edge("tools", "current_state")

is_first = True

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

def runGroup1Agent(query,id):
    global is_first
    
    if is_first:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        is_first = False
    else:
        messages = [HumanMessage(content=query)]
        
    res = graph.invoke({"messages":messages},{"configurable": {"thread_id": id}},)

    return res["messages"][-1].content