# From Jupyter Notebooks to Real World Applications

Quando si sviluppano real world applications, spesso si vuole che altre persone interagiscano con la nostra applicazione tramite API o se no tramite un frontend come in una chat application.

Prenderemo il Football News Agency Agent che abbiamo già costruito e lo trasformeremo in una applicazione fullstack.

## Techstack:

### Frontend
Il frontend è costruito con Angular (JavaScript Framework), ma non lo tratteremo dato che non siamo dei frontend developers.

### Backend
Il backend è costruito usando LangGraph per creare l'agente avvolto/wrapped un API layer utilizzando FastAPI (Python Framework), che è un framework web molto veloce e facile da usare.

FastAPI si integra perfettamente con LangGraph dato che entrambi consentono l'asynchronous programming alimentata da Uvicorn rendondal altamente performante e pronta per la produzione.

### Database
Potenzieremo i checkpointers. Precedentemente abbiamo utilizzato il memory checkpoint, il quale perde tutti gli snapshots quando l'applicazione si ferma o viene riavviata.

Per assicurare la persistenza degli stati, useremo LangGraph Postgres Server, un production ready checkpoint che memorizza gli snapshots in un database Postgres.

### Docker

Infine, per rendere la nostra applicazione semplice da avviare e fermare ed eseguirla compatibilmente attraverso diversi sistemi operativi, utilizzeremo Docker.

Docker è un tool di containerization che impachetta la nostra applicazione e le sue dipendenze all'interno di una unità standardizzata.

#### Docker compose

Useremo il file docker-compose.yaml dove al suo interno troviamo la sezione **services** nella quale abbiamo Postgres service, il nostro backend service ed il nostro frontend service.

Il **Postgres service** è il responsabile di tenere i nostri snapshots persistenti.

**Backend service** è il responsabile della creazione della nostra API oltre che del nostro agente.

**Frontend services** è per mostrare gli output del nostro agente.

### Avvio

Per avviare la nostra applicazione entriamo nella cartella dove è presente il file docker-compose.yaml e nel terminale digitiamo il comando **docker compose up --build** il quale creerà tutte le immagini. Per il frontend usiamo la cartella "./frontend" per il backend la cartella "./backend" messi nella chiave "context". Invece per il database Postgres usiamo la immagine Postgres 15 e lo buildiamo localmente. 

Una volta avviato il docker compose avremo 3 applicazioni in running che possiamo controllare con il comando **docker ps**.


Il frontend è disponibile in **http://localhost:5555/admin** il backend invece in **http://localhost:8000/docs**.


#### Backend

Il primo passo è creare un thread. Con l'endpoint **/start_thread** ci creera una sessione nel nostro backend e poi potremo usare tale thread per fare una "question" (endpoint /ask_quiestion/{thread_id}), per editare/update uno stato (/edit_state/{thread_id}) e per confermare qualcosa (/confirm/{thread_id}). Inoltre possiamo usare il thread_id per cancellare il nostro articolo.

Procediamo a creare un thread che ci da in output un thread ID. Copiamo l'ID e facciamo una domanda nell'endpoint /ask_question che ci da in output dei valori che vengono usrati nel frontend.

esempio di output:

```json
{
  "thread_id": "365843c2-49ee-4155-9e50-abbd4c62a977",
  "question_asked": true,
  "question": "How is the weather in Munich?",
  "answer": "Article not relevant for news agency",
  "confirmed": false,
  "error": false
}
```

Nel frontend vediamo:

![alt text](../frontend.png)

Tuttavia siccome non è ancora confermato non vediamo ancora niente nella pagina /articles del frontend. Questo è come implementiamo il Human-in-the-loop. 

L'API memorizza li snapshots e quindi siamo in grado (con un solo click) di confermare lo stato. Quindi confermando si passa al secondo step,  cioè dove il flusso viene ripreso dall conferma umana dallo stato in cui si era fermato per ottenre la conferma, come sappiamo rieseguendo l'invocazione con None (questo non si vede dato che è in backend). Una volta confermato, e quindi ripreso il flusso dall'interruzione per lo human-in-the-loop, vedremo nella pagina /articles del frontend il nostro articolo:

![alt text](../frontend_1.png)

Facciamo un'altro esempio. Come primo passo creiamo un nuovo thread_id con l'endpoint /start_thread lo copiamo e passiamo la question "Lionel Messi will go to Real Madrid in 2025" nell'endpoint /ask_question. Il risultato è:

```json
{
  "thread_id": "8fbcebb8-3506-4425-af0f-ea9ad4f264a5",
  "question_asked": true,
  "question": "Lionel Messi will go to Real Madrid in 2025",
  "answer": "Lionel Messi, the renowned Argentine football superstar, is expected to make a significant move to Real Madrid in the year 2025, a transfer that has generated considerable excitement and speculation among football fans and analysts alike. Currently, Messi's market value stands at an impressive €50 million, reflecting his immense talent, experience, and the impact he has had on the game over the years. At present, Messi is playing for Paris Saint-Germain, a prominent club in France's Ligue 1, where he has showcased his exceptional skills since joining the team. The potential transfer to Real Madrid would mark a pivotal moment in his career, as it will bring him to one of the greatest rivalries in football, known as \"El Clásico,\" where he would face off against his long-standing rivals and provide fans with thrilling matches.",
  "confirmed": false,
  "error": false
}
```

![alt text](../frontend_2.png)


Stavolta vogliamo editare/update lo stato. Ora siamo nell'interrupt after il nodo newsagent_node in attesa dell'attivitàn umana che con l'endpoint o il tato edit nel frontend si va a prendere lo snapshot di questo thread e si va a modificare la chiave "answer" per poi riprendere il flusso con lo stesso thread bisogna confermare col bottone che va a chiamare l'endpoint /confirm.

Il risultato sarà:

![alt text](../frontend_3.png)



# Backend FastAPI

nel modulo app.py usiamo la classe HumanWorkflow() agent il quale usa tutti i sottoagneti o agenti specializzati.

Dunque creimo una singola istanza di HumanWorkflow(). Perchè creiamo una singola istanza?

Questo perchè questa istanza è responsabile del gestire le connessioni con il nostro Postgres database. Quindi usiamo una **connection pool** e usando un single human workflow istance evitiamo conflitti ed ottimiziamo il resource management centralizzando il connection pool management.

Come si vede utilizziamo una seconda connection string:

```python
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@postgres_local:5432/postgres"
)
TARGET_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@postgres_local:5432/threads_db"
)

default_engine = create_engine(DEFAULT_DATABASE_URL, future=True)
target_engine = create_engine(TARGET_DATABASE_URL, future=True)
```

Questo perchè vogliamo creare un'altra tabella.

Questa Thread Table è la responsabile per aiutare la gestione e la persistenza degli stati della nostra conversazione.

Vogliamo controllare se il Thread ID già esiste, se la question è già stata chiesta o no, memorizzare la question iniziale e la risposta, e merizzare anche la informazione se il workflow è già stato confermato o meno. Utilizzando questa informazione possiamo assicurarci che non fare qualcosa come il double texting o di usare los stesso Thread iD più volte. 

```python
class Thread(Base):
    __tablename__ = "threads"
    thread_id = Column(String, primary_key=True, index=True)
    question_asked = Column(Boolean, default=False)
    question = Column(String, nullable=True)
    answer = Column(Text, nullable=True)
    confirmed = Column(Boolean, default=False)
    error = Column(Boolean, default=False)


def initialize_database():
    with default_engine.connect() as connection:
        with connection.execution_options(isolation_level="AUTOCOMMIT"):
            result = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'threads_db'")
            ).fetchone()
            if not result:
                connection.execute(text("CREATE DATABASE threads_db"))

def ensure_tables():
    Base.metadata.create_all(bind=target_engine)
```

Inoltre definiamo una funzione per inizializzare il database, e assicurare che le tabelle che abbiamo creato esistano.


E come vediamo usiamo la funzione **lifespan** che è la responsabile della gestione del lifespan (durata di vita) di una applicazione. Quindi quando un server si avvia poi vogliamo runnare tale funzionalità del db una sola volta. Quindi qui impostiamo il nostro db, vogliamo assicurarci che le tabelle esistano e impostare la nostra connection pool. Facciamo tutto questo solo una volta all'avvio del server. Questo è molto importante dato che utilizziamo l'**AsyncPostgresSaver** il che significa che le operazioni del nostro database sono anch'esse asincrone. Per questo utilizziamo anche la **AsyncConnectionPool** class.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    ensure_tables()
    conn_string = DEFAULT_DATABASE_URL.replace("postgresql+psycopg", "postgresql")

    async with AsyncConnectionPool(
        conninfo=conn_string,
        kwargs={"autocommit": True},
        max_size=20,
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        human_workflow.set_checkpointer(checkpointer)

        yield
```

### **📌 Analisi dettagliata del codice per l'avvio del DB**
Il codice crea un'**applicazione FastAPI con integrazione a PostgreSQL**, utilizzando SQLAlchemy per la gestione del database e `AsyncPostgresSaver` per la persistenza dello stato di un workflow (`HumanWorkflow`).

L'architettura si basa su:
- **FastAPI** per gestire le API REST.
- **SQLAlchemy** per la gestione del database (`threads_db`).
- **`asynccontextmanager`** per gestire il ciclo di vita dell'app.
- **`AsyncPostgresSaver`** per la gestione del checkpoint del workflow.
- **`psycopg_pool`** per connessioni asincrone al database.

---

## **🔹 1. Configurazione del Database**
### **📌 Connessione ai database**
```python
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@postgres_local:5432/postgres"
)
TARGET_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@postgres_local:5432/threads_db"
)

default_engine = create_engine(DEFAULT_DATABASE_URL, future=True)
target_engine = create_engine(TARGET_DATABASE_URL, future=True)
```
🔹 **Cosa fa?**
- Definisce due **URL di connessione**:
  - `DEFAULT_DATABASE_URL`: database principale.
  - `TARGET_DATABASE_URL`: database per la gestione dei thread.
- Crea due **engine SQLAlchemy** (`default_engine` e `target_engine`).


### **🔹 Perché si creano due `engine`?**
Il codice crea **due `engine` SQLAlchemy** per connettersi a **due database diversi**:

```python
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@postgres_local:5432/postgres"
)
TARGET_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@postgres_local:5432/threads_db"
)

default_engine = create_engine(DEFAULT_DATABASE_URL, future=True)
target_engine = create_engine(TARGET_DATABASE_URL, future=True)
```
🔹 **Motivo principale**: Separare la **gestione del database principale** da quella del **database specifico per i thread (`threads_db`)**.

---

## **📌 Differenza tra i due `engine`**
| **Engine**        | **Database usato**          | **Scopo** |
|------------------|-------------------------|----------|
| `default_engine` | **`postgres`**           | Controlla l'esistenza di `threads_db` e lo crea se necessario. |
| `target_engine`  | **`threads_db`**         | Usato per salvare e leggere i dati dei thread. |

---

## **🔹 Quando viene usato `default_engine`?**
Viene usato **solo all'avvio** per verificare se il database `threads_db` esiste e crearlo se necessario:

```python
def initialize_database():
    with default_engine.connect() as connection:  # ✅ Usa `default_engine`
        with connection.execution_options(isolation_level="AUTOCOMMIT"):
            result = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'threads_db'")
            ).fetchone()
            if not result:
                connection.execute(text("CREATE DATABASE threads_db"))
```
🔹 **Conclusione**: `default_engine` è temporaneo e serve **solo per creare il database all'avvio**.

---

## **🔹 Quando viene usato `target_engine`?**
Viene usato per tutte le operazioni **sul database `threads_db`**, ad esempio:

### **1️⃣ Creazione delle tabelle**
```python
def ensure_tables():
    Base.metadata.create_all(bind=target_engine)  # ✅ Usa `target_engine`
```

### **2️⃣ Creazione della sessione del database**
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=target_engine)
```
Tutte le operazioni del database useranno **questa sessione**, che è collegata a `target_engine`.

### **3️⃣ Accesso ai dati con `get_db()`**
```python
def get_db():
    db = SessionLocal()  # ✅ Usa `target_engine`
    try:
        yield db
    finally:
        db.close()
```
🔹 **Conclusione**: `target_engine` è il **database effettivo** usato dall'applicazione.

---

## **📌 Riassunto**
| **Engine** | **Database** | **Quando viene usato?** |
|------------|-------------|-------------------------|
| `default_engine` | `postgres` | Solo all'avvio per controllare e creare `threads_db`. |
| `target_engine` | `threads_db` | Per tutte le operazioni di lettura/scrittura sui thread. |

✅ Dopo la fase di inizializzazione, **solo `target_engine` viene usato nell'app FastAPI**.

💡 **Conclusione**: Creare due `engine` permette di **separare la gestione del database principale dalla logica applicativa**, migliorando modularità e sicurezza! 🚀

---

## **🔹 2. Definizione del Modello di Database (`Thread`)**
```python
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=target_engine)

class Thread(Base):
    __tablename__ = "threads"
    thread_id = Column(String, primary_key=True, index=True)
    question_asked = Column(Boolean, default=False)
    question = Column(String, nullable=True)
    answer = Column(Text, nullable=True)
    confirmed = Column(Boolean, default=False)
    error = Column(Boolean, default=False)
```
🔹 **Cosa fa?**
- `Base = declarative_base()` → Definisce una base per i modelli SQLAlchemy.
- `SessionLocal` → Crea una sessione del database per eseguire query.
- **Crea la tabella `threads`**, che memorizza informazioni su un thread con i seguenti campi:
  - `thread_id` (String) → Identificativo univoco.
  - `question_asked` (Boolean) → Se è stata posta una domanda.
  - `question` (String) → Testo della domanda.
  - `answer` (Text) → Risposta associata.
  - `confirmed` (Boolean) → Se la risposta è stata confermata.
  - `error` (Boolean) → Flag per segnalare errori.

---

## **🔹 3. Creazione e inizializzazione del database**
```python
def initialize_database():
    with default_engine.connect() as connection:
        with connection.execution_options(isolation_level="AUTOCOMMIT"):
            result = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'threads_db'")
            ).fetchone()
            if not result:
                connection.execute(text("CREATE DATABASE threads_db"))
```
🔹 **Cosa fa?**
- Controlla se il database **`threads_db`** esiste già.
- Se non esiste, lo **crea dinamicamente**.

---
```python
def ensure_tables():
    Base.metadata.create_all(bind=target_engine)
```
🔹 **Cosa fa?**
- **Crea le tabelle** nel database `threads_db` se non esistono.

---

## **🔹 4. Gestione della connessione al database (`get_db`)**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
🔹 **Cosa fa?**
- **Crea una connessione al database** con `SessionLocal()`.
- **Usa `yield` per passarla a FastAPI**.
- **Chiude la connessione automaticamente** quando non è più necessaria.

---

## **🔹 5. Gestione del ciclo di vita dell’app (`lifespan`)**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    ensure_tables()
    conn_string = DEFAULT_DATABASE_URL.replace("postgresql+psycopg", "postgresql")

    async with AsyncConnectionPool(
        conninfo=conn_string,
        kwargs={"autocommit": True},
        max_size=20,
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        human_workflow.set_checkpointer(checkpointer)

        yield
```
🔹 **Cosa fa?**
1. **Avvia il database** chiamando `initialize_database()` e `ensure_tables()`.
2. **Configura una connessione asincrona (`AsyncConnectionPool`)** con PostgreSQL.
3. **Imposta il `checkpointer` per salvare lo stato del workflow (`HumanWorkflow`)**:
   - `AsyncPostgresSaver(pool)` → Usa un database PostgreSQL per il checkpoint.
   - `human_workflow.set_checkpointer(checkpointer)` → Il workflow può ora salvare stati intermedi.
4. **Usa `yield`** per mantenere la connessione attiva finché l'app è in esecuzione.

---

## **📌 Riassunto delle funzionalità**
| **Componente**  | **Funzione** |
|----------------|-------------|
| `DEFAULT_DATABASE_URL` & `TARGET_DATABASE_URL` | URL di connessione a PostgreSQL |
| `create_engine()` | Crea connessioni al database |
| `Thread` | Modello SQLAlchemy per gestire i thread |
| `initialize_database()` | Crea `threads_db` se non esiste |
| `ensure_tables()` | Crea le tabelle se non esistono |
| `get_db()` | Gestisce una connessione al database per FastAPI |
| `lifespan()` | Avvia il database e configura il checkpoint per `HumanWorkflow` |

---

## **📌 Esempio di utilizzo con FastAPI**
```python
from fastapi import FastAPI, Depends

app = FastAPI(lifespan=lifespan)

@app.get("/threads/")
def get_threads(db: Session = Depends(get_db)):
    return db.query(Thread).all()
```
✔️ **L'API ora può interrogare il database `threads_db` per ottenere tutti i thread!**

---

## **📌 Conclusione**
✅ **Gestisce un database PostgreSQL** con SQLAlchemy.  
✅ **Inizializza dinamicamente il database** se non esiste.  
✅ **Configura una connessione asincrona** per il checkpoint del workflow.  
✅ **Usa `lifespan()` per avviare le risorse al momento del lancio dell'app**.  

💡 **Questo codice è un'ottima base per un sistema di gestione di thread basato su FastAPI e PostgreSQL! 🚀**