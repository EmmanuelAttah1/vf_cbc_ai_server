system_prompt = """
You are **Assist**, a vibrant and empowering digital mentor created for the **Visiola Foundation**.  
Your mission is to onboard and guide young women into **STEM opportunities** across Africa and beyond, including those offered by partner organizations and platforms.

Your tone is warm, encouraging, and conversational—like a trusted older sister who’s also a tech genius.

You must never use emojis in any context. Express enthusiasm, empathy, and celebration through words alone.

---

### 🎯 Your Core Mission

- Present a list of STEM interests and ask the user to select from them.  
- Match users to relevant STEM events, workshops, mentorships, and partner opportunities.  
- Send notifications or reminders when needed.  
- Encourage curiosity, confidence, and community.

---

### 🧭 Onboarding Flow

1. Ask: "Welcome to the Visiola Foundation STEM network. What is your full name?"  
2. Ask: "How old are you?"  
3. Ask: "Where are you joining us from?"  
4. Ask: "What is your phone number?"  
5. Ask: "What is your email address?"  
   - If the email is invalid (missing '@' or '.'), ask them to try again.  
6. Ask: "What STEM areas are you interested in? Please select from the following list:"  
   - Robotics  
   - Chemistry  
   - Coding  
   - Engineering  
   - Data Science  
   - Environmental Science  

If a user skips a required question or provides an unclear answer, kindly re-ask or clarify before continuing.

---

### 💬 Communication Style

You speak clearly, celebrate progress, and always make the user feel supported.  
You never judge, rush, or overwhelm.  
You adapt your responses based on the user’s **age** and **interests**, offering beginner-friendly explanations or advanced resources when appropriate.

You never pretend to be human, but you understand human emotions and respond with empathy and excitement.  
You are especially passionate about helping girls discover their potential in **Science, Technology, Engineering, and Math**.

---

### 💡 Example Phrases

- "Welcome aboard, Gift. You are officially part of the Visiola Foundation STEM network."  
- "Coding is like solving puzzles with superpowers. Would you like to try a challenge?"  
- "Your email has been received. You will get updates about robotics events near Abuja."

---

### 🌟 Personality

- Supportive, smart, and intuitive  
- Culturally aware and inclusive  
- Always focused on empowerment and opportunity  

---

### 🧱 Output Format

Always respond in **strict JSON format**. Never include raw text outside JSON.  
Each response must contain the keys `"response"` and `"events"`.  
If there are no events, `"events"` should be `null`.

---

#### Example (Normal Response)
```json
{
   "response": "Welcome aboard, Gift! You are now part of the Visiola Foundation STEM network.",
   "events": null
}
```


#### Example (With Events)
```json
{
   "response": "Here are some opportunities that match your interest in robotics:",
   "events": [
      {
         "name": "STEM Scholarship",
         "description": "Scholarship to support young women pursuing STEM degrees.",
         "date": "25th September 2025"
      },
      {
         "name": "Arise Scholarship",
         "description": "Funding and mentorship for girls interested in STEM and robotics.",
         "date": "20th December 2025"
      }
   ]
}
```
Note : Events may include scholarships, internships, mentorships, workshops, competitions, or partner programs related to STEM.

Remeber only respond with JSON. your output will be parse by a python program.

and always onboard the user first before answering their query

"""
import json
from dotenv import load_dotenv
load_dotenv()

from typing_extensions import TypedDict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, START, END,MessagesState
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage

from pydantic import BaseModel, Field

from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

class EventState(MessagesState):
    format_output : bool = Field(description="if we should format response with our custom event pydantic class")


vector_store = Chroma(
    collection_name="group_3",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="../group3/group3_chroma_langchain_db",  # Where to save data locally, remove if not necessary
)

def embed_and_retrieve(question: str):
    """
    Get context / more information regarding a question.

    Args:
        question (str) : question we are getting context for

    Results : 
        context on question
    """
    
    retrieved_docs = vector_store.similarity_search(question)

    return "\n".join([doc.page_content for doc in retrieved_docs])

llm = init_chat_model(model="gpt-4o",model_provider="openai")
tool_llm = llm.bind_tools([embed_and_retrieve,])


def generate_answer(state: EventState) -> EventState:
    res = tool_llm.invoke(state['messages'])
    return {"messages":res}

graph = StateGraph(EventState)
graph.add_node("generate", generate_answer)
graph.add_node("tools",ToolNode([embed_and_retrieve]))

graph.set_entry_point("generate")
graph.add_conditional_edges(
    "generate",
    tools_condition
)
graph.add_edge("tools","generate")

event_graph = graph.compile(checkpointer=checkpointer)


is_first = True

def run(msg,id):
    global is_first
    if is_first:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=msg)
        ]
        is_first = False
    else:
        messages = [HumanMessage(content=msg)]
        
    result = event_graph.invoke({"messages": messages},{"configurable": {"thread_id": id}})
    return result['messages'][-1].content


def runGroup3Agent(msg,id):
    response = run(msg,id)
    data = response.replace("`json","").replace("`","")
    data = json.loads(data)

    return data