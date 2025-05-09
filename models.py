from sqlalchemy import Column,Integer,String,Text
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()

class ChatLog(Base):
    __tablename__="chat_logs"

    id=Column(Integer,primary_key=True,index=True)
    model_name=Column(String,index=True)
    system_prompt=Column(Text)
    user_messages=Column(Text)
    response=Column(Text)