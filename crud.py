from typing import List
from starlette import status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, status, Body, HTTPException, Request, Form
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

messages_db = []


class Message(BaseModel):
    id: int = None
    text: str

    model_config = {
        "json_schema_extra": {
            "examples":
                [
                   {
                        "text": "Simple message",
                   }
                ]
        }
    }


@app.get("/")
async def get_all_messages(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("message.html", {"request": request, "messages": messages_db})


@app.get("/message/{message_id}")
async def get_message(request: Request, message_id: int) -> HTMLResponse:
    try:
        return templates.TemplateResponse("message.html", {"request": request, "message": messages_db[message_id]})
    except IndexError:
        raise HTTPException(status_code=404, detail="Message not found")


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_message(request: Request, message: str = Form()) -> HTMLResponse:
    if len(messages_db) == 0:
        max_id_message = 0
    else:
        max_id_message = max([i.dict()["id"] for i in messages_db]) + 1
    messages_db.append(Message(id=max_id_message, text=message))
    return templates.TemplateResponse("message.html", {"request": request, "messages": messages_db})


@app.put("/message/{message_id}")
async def update_message(message_id: int, message: str = Body()) -> str:
    try:
        edit_message = messages_db[message_id]
        edit_message.text = message
        return "Message updated!"
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.delete("/message/{message_id}")
async def delete_message(message_id: int) -> str:
    try:
        messages_db.pop(message_id)
        return f"Message ID={message_id} deleted!"
    except IndexError:
        raise HTTPException(status_code=404, detail="Message not found")


@app.delete("/")
async def kill_message_all() -> str:
    messages_db.clear()
    return "All messages deleted!"
