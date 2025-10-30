from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from group1_agent import runGroup1Agent
from group2_agent import group2_agent
from group3_agent import runGroup3Agent
from group4_agent import runGroup4Agent

app = FastAPI() # creating a FastAPI instance and storing it in app variable

origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    "https://emmanuelattah1.github.io/vf_cbc_ai_1",
    "https://emmanuelattah1.github.io/vf_cbc_ai_2",
    "https://emmanuelattah1.github.io/vf_cbc_ai_3",
    "https://emmanuelattah1.github.io/vf_cbc_ai_4"
]

app.add_middleware( 
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InterviewSetup(BaseModel):
    """Creating our post request class with a single key `query` """
    role : str
    difficulty: str
    question_type: str
    num_questions : int
    id:str

class ResponseType(BaseModel):
    message:str
    id:str

@app.post("/setup/")
def handle_group2_setup(data:InterviewSetup):
    print(data)
    res = group2_agent(
        "",
        {"role":data.role,"difficulty":data.difficulty,"interview_type":data.question_type,"number_of_questions":data.num_questions},
        data.id
    )
    return {"ai_response":res[0],"type":res[1]}


@app.post("/message/")
def handle_group2_message(data:ResponseType):
    res,q_type,has_ended = group2_agent(data.message,data.id)
    return {"ai_response":res,"type":q_type,"has_ended":has_ended}


@app.post("/group1/")
def handle_group2_message(data:ResponseType):
    res = runGroup1Agent(data.message,data.id)
    return {"ai_response":res}


@app.post("/group3/")
def handle_group3_setup(data:ResponseType):
    print(data)
    res = runGroup3Agent(data.message,data.id)
    return {"ai_response":res}

@app.post("/group4/")
def handle_group4_setup(data:ResponseType):
    res = runGroup4Agent(data.message,data.id)
    return {"ai_response":res}