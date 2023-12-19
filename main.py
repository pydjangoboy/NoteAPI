from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI()


# Pydantic model for notes
class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime = datetime.now()


# In-memory database (list) to store notes
notes_db: List[Note] = []
next_note_id: int = 1


# CRUD operations

@app.post("/notes/", response_model=Note, summary="Create a new note")
def create_note(note: Note):
    global next_note_id
    note.id = next_note_id
    next_note_id += 1
    notes_db.append(note)
    return note


@app.get("/notes/", response_model=List[Note], summary="Get all notes")
def read_notes():
    return notes_db


@app.get("/notes/{note_id}", response_model=Note, summary="Get a specific note")
def read_note(note_id: int):
    note = next((n for n in notes_db if n.id == note_id), None)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/{note_id}", response_model=Note, summary="Update a note")
def update_note(note_id: int, updated_note: Note):
    note_index = next((i for i, n in enumerate(notes_db) if n.id == note_id), None)
    if note_index is None:
        raise HTTPException(status_code=404, detail="Note not found")

    # Ensure that the updated_note.id matches the provided note_id
    if note_id != updated_note.id:
        raise HTTPException(status_code=400, detail="Note ID mismatch")

    # Update the note in the database
    notes_db[note_index] = updated_note
    return updated_note


@app.delete("/notes/{note_id}", response_model=Note, summary="Delete a note")
def delete_note(note_id: int):
    note = next((n for n in notes_db if n.id == note_id), None)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    # Delete the note from the database
    notes_db.remove(note)
    return note


# FastAPI automatic OpenAPI and Swagger documentation
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="FastAPI Swagger UI")


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    return JSONResponse(content=app.openapi())


