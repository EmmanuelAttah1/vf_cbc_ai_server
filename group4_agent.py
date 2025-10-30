import json

system_prompt = """
You are an AI assistant that helps users find **scholarships** tailored to their background and goals.

---

### 🎯 Responsibilities
- Ask for key details: **academic level**, **country of residence and citizenship**, **field of study**, **demographics** (optional), **financial need**, and **application timeline**.  
- Recommend scholarships with clear summaries, including:  
  * name  
  * eligibility  
  * deadline  
  * award amount  
  * application link  
- Offer concise, practical tips and next steps for applying.

---

### 💬 Communication Style
Your tone is **professional, clear, and supportive**.  
Use **structured formatting** and keep responses concise.  
If details are missing or unclear, politely ask for clarification.  
Avoid guessing eligibility or recommending expired scholarships.  
Do **not** provide legal, financial, or admissions advice.

---

### 🚀 Session Start
Always begin each session by greeting the user and asking for the details needed to begin the search.  
Example:  
> "Hi! I can help you find scholarships that fit you. Could you tell me your academic level and where you're based?"

---

### 🧱 Output Format
Always respond **only in valid JSON**. Never include text outside of JSON.  
Your output will be parsed by a Python program.

Each response must include:
- `"response"`: the assistant’s main message or question.
- `"scholarships"`: a list of matching scholarships, or `null` if none are being shown.

---

### ✅ Example Responses

#### Normal Response
{
   "response": "Hi! I can help you find scholarships. Could you tell me your academic level and country of residence?",
   "scholarships": null
}

#### Response with Scholarships
{
   "response": "Here are some scholarships that match your profile:",
   "scholarships": [
      {
         "name": "Arts and Creativity Fund",
         "grant": "$7,500",
         "target": "For students demonstrating exceptional talent in visual or performing arts.",
         "deadline": "September 5, 2025",
         "requirements": "Open to undergraduate STEM majors."
      },
      {
         "name": "STEM Rising Stars Grant",
         "grant": "$10,000",
         "target": "For female students in engineering or computer science programs.",
         "deadline": "December 15, 2025",
         "requirements": "Must be enrolled full-time in a recognized institution."
      }
   ]
}


NOTE : when the user request for more info on a scholarship, respond with a normal response!!!
"""


from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

load_dotenv()

import bs4
# from langchain import hub
from langchain_community.document_loaders import  WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START,StateGraph
from typing_extensions import List, TypedDict


mock_data = [
    {   
        "Name": "Chevenings Scholarship",
        "Country": "USA",
        "Age": "17-20",
        "Program_offered": "All STEM program",
        "Scholarship_type": "Need-based",
        "Scholarship_info": "For young international and local females in STEM",
        "Academic_degree_level": "Undergraduate",
        'Application date': '15 November',
        'Dead line': '20 november',
        'requirement': [
            'Applicant should be an undergraduate, Masters, PhD.',
            'Applicant should at least have a score of 80 in the test.',
            'Application Form: Personal information and academic details, Completed application.',
            'Letter of Recommendation: Typically from teachers, mentors, or employers and Should highlight your strengths and qualifications.'
        ],
    },
    {
        "Name": "Jack Kent Cooke scholarship",
        "Country": "Russia",
        "Age": "20-27",
        "Program_offered": "Software programming",
        "Scholarship_type": "Merit-based",
        "Scholarship_info": "Open to all international students seeking for fundings for their education",
         "Academic_degree_level": "Masters",
        'Application date': "20 December",
        'Dead line': '31 December'
    },
        {
        "Name": "Fulbright scholarship",
        "Country": "Australia",
        "Age": "18-25",
        "Program_offered": "Fashion and design",
        "Scholarship_type": "Need-based",
        "Scholarship_info": "For African designers seeking to expand and incoporate western fashion into african heritage",
         "Academic_degree_level": "Masters",
          'Application date': "12 february",
          'Dead line': '17 february'
        },
    {
        "Name": "Bright Future scholarship",
        "Country": "China",        
        "Age": "30-40",
        "Program_offered": "all phD courses",
        "Scholarship_type": "Need-based",
        "Scholarship_info": "For Nigerians who desire to complete their phD abroad but can't due to insufficient funds",
         "Academic_degree_level": "phD",
        'Application date': "17 july",
        'Dead line':'18 july'
        }
]


Applicant = None

def CollectApplicantInfo():
    """
    Collects applicant information
    """
    Applicant = {}
    Applicant['name'] = input('Enter Name : ')
    Applicant['age'] = int(input('Enter age : '))
    Applicant['country'] = input('Enter country : ')
    Applicant['education_level'] = input('Enter education_level (Undergraduate/Masters/PhD): ')
    Applicant['Department'] = input('Enter Department : ')


def getAvailableScholarship():
    """
    get all scholarship from our data base

    Return
      list
    """
    return mock_data
    

def ScholarshipChecker(scholarship:str):
    '''
    return the requirements for a specified scholaship

    Arg:
        scholarship (str) : name of the scholarship
        
    '''

    for i in mock_data:
        if i["Name"] == scholarship:
            return i

    return None


model = init_chat_model(model="gpt-4o", model_provider="openai")
model_with_tool = model.bind_tools([CollectApplicantInfo, getAvailableScholarship,ScholarshipChecker])

def llm_node(state):
    return {'messages' : model_with_tool.invoke (state['messages'])}

builder = StateGraph(MessagesState)
builder.add_node('llm_node',llm_node)
builder.add_node('tools',ToolNode([CollectApplicantInfo,getAvailableScholarship,ScholarshipChecker,]))


builder.add_edge(START,'llm_node')
builder.add_conditional_edges(
    'llm_node',
    tools_condition,
)
builder.add_edge('tools','llm_node')


graph = builder.compile(checkpointer=checkpointer)

is_first = True

def run(msg,id):
    global is_first
    if is_first:
        messages = [
                  SystemMessage(content=system_prompt),     
                  HumanMessage(content=msg),
        ]
        is_first = False
    else:
        messages = [
                  HumanMessage(content=msg),
               ]
        
    res = graph.invoke({'messages':messages
        },{"configurable": {"thread_id": id}})

    return res['messages'][-1].content


def runGroup4Agent(msg,id):
    res = run(msg,id)
    data = res.replace("`json","").replace("`","")
    data = json.loads(data)
    return data