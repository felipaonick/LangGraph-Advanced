from contextlib import asynccontextmanager
from typing import Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
"""
MongoDB di per sé non è asincrono, ma il pacchetto motor fornisce un'interfaccia compatibile con asyncio.

Se usi motor.motor_asyncio.AsyncIOMotorClient, puoi eseguire operazioni asincrone con await, come find_one(), insert_one(), update_one(), ecc.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from workflows.human_workflow import HumanWorkflow

"""
When deploying agents on the LangGraph platform, you often need to initialize resources like database connections when your server starts up, 
and ensure they're properly closed when it shuts down. 
Lifespan events let you hook into your server's startup and shutdown sequence to handle these critical setup and teardown tasks.
"""

import os

# Legge la connessione da ENV
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongodb:27017")

DB_NAME = "threads_db"

human_workflow = HumanWorkflow()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 1. Connessione a MongoDB quando l'app si avvia
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    mongo_db = mongo_client["threads_db"]

    # 🔹 2. Creiamo il checkpointer per i workflow
    checkpointer = AsyncMongoDBSaver(mongo_client)

    # 🔹 3. Assegniamo il checkpointer al workflow AI
    human_workflow.set_checkpointer(checkpointer)

    # 🔹 4. Definiamo la collection "threads"
    global threads_collection
    threads_collection = mongo_db["threads"]

    print("🔵 MongoDB connesso e pronto!")

    yield  # 🔹 Mantiene il contesto aperto finché l'app è attiva

    # 🔹 5. Quando l'app si chiude, chiudiamo MongoDB
    mongo_client.close()
    print("🛑 Connessione a MongoDB chiusa.")


"""
🔹 Spiegazione passo per passo
1️⃣ Connette FastAPI a MongoDB con AsyncIOMotorClient.
2️⃣ Inizializza il checkpointer con AsyncMongoDBSaver, per salvare i checkpoint.
3️⃣ Assegna il checkpointer al workflow (human_workflow.set_checkpointer(checkpointer)).
4️⃣ Definisce threads_collection globalmente, così gli altri endpoint possono usarla.
5️⃣ Mantiene il database attivo mentre l'app è in esecuzione (yield).
6️⃣ Chiude la connessione a MongoDB quando l'app viene arrestata.
"""


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ThreadResponse(BaseModel):
    thread_id: str
    question_asked: bool
    question: Optional[str] = None
    answer: Optional[str] = None
    confirmed: bool
    error: bool



class StartThreadResponse(BaseModel):
    thread_id: str


class ChatRequest(BaseModel):
    question: Optional[str] = None


class UpdateStateRequest(BaseModel):
    answer: str


@app.post("/start_thread", response_model=StartThreadResponse)
async def start_thread():
    thread_id = str(uuid4())
    new_thread = {
        "thread_id": thread_id,
        "question_asked": False,
        "confirmed": False,
        "error": False,
        "question": None,
        "answer": None,
    }
    await threads_collection.insert_one(new_thread)
    return StartThreadResponse(thread_id=thread_id)


@app.post("/ask_question/{thread_id}", response_model=ThreadResponse)
async def ask_question(thread_id: str, request: ChatRequest):
    thread = await threads_collection.find_one({"thread_id": thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread ID does not exist.")
    if thread["question_asked"]:
        raise HTTPException(status_code=400, detail="Question already asked.")

    if not request.question:
        raise HTTPException(status_code=400, detail="Missing question.")

    # Esegui il workflow
    response_state = await human_workflow.ainvoke(
        input={"question": request.question},
        config={"recursion_limit": 15, "configurable": {"thread_id": thread_id}},
        subgraphs=True,
    )

    # Aggiorna il thread in MongoDB
    update_fields = {
        "question_asked": True,
        "question": request.question,
        "answer": response_state[1].get("answer"),
        "error": response_state[1].get("error", False),
    }
    await threads_collection.update_one({"thread_id": thread_id}, {"$set": update_fields})

    # Ritorna il thread aggiornato
    updated_thread = await threads_collection.find_one({"thread_id": thread_id})
    return ThreadResponse(**updated_thread)



@app.patch("/edit_state/{thread_id}", response_model=ThreadResponse)
async def edit_state(thread_id: str, request: UpdateStateRequest):
    thread = await threads_collection.find_one({"thread_id": thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread ID does not exist.")
    if not thread["question_asked"]:
        raise HTTPException(status_code=400, detail="Cannot edit a thread without a question.")
    if thread["confirmed"]:
        raise HTTPException(status_code=400, detail="Cannot edit a confirmed thread.")

    # Aggiorniamo lo stato in LangGraph e MongoDB
    await human_workflow.workflow.aupdate_state(
        config={"configurable": {"thread_id": thread_id}},
        values={"answer": request.answer},
    )
    await threads_collection.update_one({"thread_id": thread_id}, {"$set": {"answer": request.answer}})

    updated_thread = await threads_collection.find_one({"thread_id": thread_id})
    return ThreadResponse(**updated_thread)


@app.post("/confirm/{thread_id}", response_model=ThreadResponse)
async def confirm(thread_id: str):
    thread = await threads_collection.find_one({"thread_id": thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread ID does not exist.")
    if not thread["question_asked"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot confirm thread {thread_id} as no question has been asked.",
        )

    # Riprendiamo l'esecuzione del workflow da MongoDB
    response_state = await human_workflow.ainvoke(
        input=None,
        config={"configurable": {"thread_id": thread_id}},
    )

    # Aggiorniamo il thread con lo stato ottenuto
    update_fields = {
        "confirmed": bool(response_state.get("confirmed", False)),
        "answer": response_state.get("answer"),
    }
    await threads_collection.update_one({"thread_id": thread_id}, {"$set": update_fields})

    # Recuperiamo il thread aggiornato
    updated_thread = await threads_collection.find_one({"thread_id": thread_id})
    return ThreadResponse(**updated_thread)




@app.delete("/delete_thread/{thread_id}", response_model=ThreadResponse)
async def delete_thread(thread_id: str):
    thread = await threads_collection.find_one({"thread_id": thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread ID does not exist.")

    await threads_collection.delete_one({"thread_id": thread_id})
    return ThreadResponse(**thread)


@app.get("/sessions", response_model=list[ThreadResponse])
async def list_sessions():
    threads = await threads_collection.find().to_list(length=None)
    return [ThreadResponse(**thread) for thread in threads]
