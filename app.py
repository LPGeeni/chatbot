from fastapi import FastAPI,Depends
from pydantic import BaseModel
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults

import os
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from database import engine
from models import ChatLog
ChatLog.metadata.create_all(bind=engine)
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

load_dotenv( )
groq_api_key=os.getenv ("GROQ" )
os.environ["TAVILY_API_KEY"]=os.getenv ("TAVILY" )

MODEL_NAMES=[
    "gemma2-9b-it",
    "mistral-saba-24b"
]

tool_tavily=TavilySearchResults( max_results=2)

tools=[tool_tavily]

app=FastAPI(title="langgraph ai agent" )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Replace with specific origins in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestState(BaseModel ):
    model_name:str
    system_prompt:str
    messages:List[str]
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat" )
def chat_endpoint(request:RequestState,db:Session=Depends(get_db) ):
    if request.model_name not in MODEL_NAMES:
        return{"error":"invalid model name. please select valid model"}
    llm=ChatGroq(groq_api_key=groq_api_key,model_name=request.model_name )
    agent=create_react_agent(llm,tools=tools,state_modifier=request.system_prompt )
    state={"messages":request.messages}
    result=agent.invoke(state )
    final_messages=result.get("messages",[])
    if not final_messages:
        return {"error":"no response generated"}
    response_text=final_messages[-1].content

    chat_log=ChatLog(
        model_name=request.model_name,
        system_prompt=request.system_prompt,
        user_messages="\n".join (request.messages),
        response=response_text

    )
    db.add(chat_log)
    db.commit()
    db.refresh(chat_log)

    return{
        "messages":[
            {"type":"ai","content":response_text}
        ]
    }
if __name__ =='__main__':
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8001)


