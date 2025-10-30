from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import START, END, StateGraph, MessagesState
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage,HumanMessage

from pydantic import BaseModel, Field
from typing import List, Optional

from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()


last_response = None
interview_results = None
has_ended = False

class LLMOutput(BaseModel):
    response : str =  Field(description="LLM response")
    is_question : bool =  Field(description=("response is a question"))
    question_type : str = Field(description="Type of question being asked can be normal, objective or coding")

class QuestionCorrection(BaseModel):
    question_asked : str = Field(description="Original question asked")
    user_answe : str = Field(description="User Answer")
    correct_answer : str = Field(description="Correct question answer")
    explanation : str = Field("short explanation to question answer")

class InterviewResult(BaseModel):
    total_questions : int = Field(description="Total number of interview questions")
    num_correct_answers : int = Field(description="Number of questions the canditate got right")
    num_wrong_answers : int = Field(description="Number of questions the canditate got wrong")
    interview_percentage : str = Field(description="Interview score in percentage")
    review_from_ai : str = Field(description='Reviewer remark/ short advice for improvement')
    corrections : List[QuestionCorrection]

class AIOutput(BaseModel):
    response : Optional[LLMOutput]
    results : Optional[InterviewResult]
    interview_has_ended : bool = Field(description="Tells us if interview has ended or not")

model = init_chat_model(model="gpt-4o",model_provider="openai")
model = model.with_structured_output(AIOutput)

class State(MessagesState):
    is_question:bool = Field(description="Is the LLM asking a question")

def sendMessage(state):
    message = state['messages']
    res = model.invoke(message)

    global interview_results

    if res.response:
        global last_response
        last_response = res.response
        if res.interview_has_ended:
            global has_ended
            has_ended = res.interview_has_ended

        return {"messages": res.response.response}
    
    elif res.results:
        interview_results =  res.results
    
    return {"messages":"done"}

def setupAgent(role,difficulty,number_of_questions,interview_type):

    placeholder_prompt = f"""
You are a **job interviewer** responsible for assessing the **capabilities of a candidate**.

---

### 🎯 Interview Types

The interview may fall under one of the following categories:

* **Technical** – evaluates the candidate’s ability to perform the required tasks.
* **Behavioural** – assesses cultural fit, communication, and interpersonal skills.
* **Situational** – examines how the candidate would respond to specific challenges related to the role.

---

### 🧭 Objective

Generate interview questions to assess the candidate’s strengths for the **role of {role}**.  
The **interview type** is **{interview_type}**.

---

### 📘 Allowed Question Types

* **Multiple choice** (options A–D)
* **Coding exercises**
* **Theory questions**

---

### ⚙️ Interview Settings

* **Difficulty:** {difficulty}
* **Number of questions:** {number_of_questions}

---

### 🧩 Guidelines

1. Present one question at a time (e.g., “Question 1”, “Question 2”, etc.).
2. After the user responds, immediately proceed to the next question.
3. Maintain a balanced rotation of question types (avoid overusing one type).
4. Do **not** provide hints, feedback, or indicate correctness during the questioning phase.
5. Do not give corrections to question until after the user request result. even if they enter a wrong answer, proceed to the next question.

---

### ✅ Completion Rule

After all questions have been answered, end the interview.  
Do **not** return results unless the user specifically requests them.
"""

    return SystemMessage(content=placeholder_prompt)


builder = StateGraph(State)

builder.add_node('llm',sendMessage)

builder.add_edge(START,"llm")
builder.add_edge('llm',END)

graph = builder.compile(checkpointer=checkpointer)

is_first = True

def group2_agent(message,setup={},id="1"):
    global last_response
    global is_first
    global interview_results

    if is_first:
        is_first = False
        system_prompt = setupAgent(setup['role'],setup['difficulty'],setup['number_of_questions'],setup['interview_type'])
        messages = [
            system_prompt,
        ]
    else:
        messages = [HumanMessage(content=message)]

    graph.invoke({"messages":messages},{"configurable": {"thread_id": id}})

    if interview_results:
        res = interview_results
        interview_results = None
        return(res,None,True,)
    
    return (last_response.response, last_response.question_type,has_ended)