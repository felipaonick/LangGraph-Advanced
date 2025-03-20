# Fullstack app con MongoDB

Al posto di usare Postgres per memorizzare i chat, useremo MongoDB.

Quindi avremo tre container:

```yaml
version: "3.8"

services:
  
  mongodb:
    image: mongo:latest
    container_name: mongodb
    restart: always
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=example

  backend:
    build:
      context: ./backend
    container_name: backend_service
    restart: always
    depends_on:
      - mongodb
    ports:
      - "8000:8000"
    environment:
      - MONGO_URI=mongodb://root:example@mongodb:27017
    command: ["uvicorn", "app_mongo:app", "--host", "0.0.0.0", "--port", "8000"]

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: angular_frontend
    ports:
      - "5555:5555"
    environment:
      - NODE_ENV=production

```

## Connessione col contaner **mongodb**


Il comando:

```sh
docker exec -it mongodb mongosh --username root --password example --authenticationDatabase admin
```

serve per **accedere alla shell di MongoDB (mongosh) all'interno del container Docker** chiamato `mongodb`. Ecco una spiegazione dettagliata dei vari componenti:

---

### 🔹 **Spiegazione dei parametri**
1. **`docker exec`** → Esegue un comando dentro un container già in esecuzione.
2. **`-it`** → Permette l'**interazione con la shell** (modo interattivo).
3. **`mongodb`** → È il **nome del container** su cui eseguire il comando.
4. **`mongosh`** → Avvia la shell di MongoDB (la nuova shell interattiva di MongoDB, che ha sostituito `mongo`).
5. **`--username root`** → Specifica l'utente `root` per autenticarsi.
6. **`--password example`** → Usa la password `example` per autenticarsi.
7. **`--authenticationDatabase admin`** → Indica che l'autenticazione deve essere fatta sul database `admin`.

---

### 🔹 **Cosa succede dopo aver eseguito il comando?**
- Ti trovi **all'interno della shell di MongoDB (`mongosh`)**, connesso al database in esecuzione dentro il container.
- Ora puoi eseguire comandi MongoDB come `show dbs`, `use`, `show collections`, `db.collection.find()`, ecc.

---

### 🔹 **Esempio di output atteso**
Dopo l'esecuzione, vedrai un prompt simile a:
```
Current Mongosh Log ID: 67dc2bf8eef5905dba6b140a
Connecting to: mongodb://<credentials>@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+2.4.2
Using MongoDB: 8.0.5
Using Mongosh: 2.4.2
```
E ti ritroverai in una sessione **MongoDB** con il prompt:
```
test>
```
A questo punto puoi eseguire comandi MongoDB.

---


Con il comando show dbs vediamo i database presenti:

```sh
show dbs
```

Selezioniamo il database:
```sh
use threads_db
```

E vediamo le collection:
```sh
show collections
```

Mostriamo i documenti della collection threads:
```sh
db.threads.find().pretty()
```

Così vediamo ad esempio gli stati memorizzati nel mongodb:
```json
[
  {
    _id: ObjectId('67dc2a1664e1a3b04e2cd54c'),
    thread_id: '8e57a604-84db-4870-9c71-12e7c60e2ce0',
    question_asked: true,
    confirmed: true,
    error: false,
    question: 'How is the weather in Munich?',
    answer: 'Article not relevant for news agency'
  },
  {
    _id: ObjectId('67dc2aee64e1a3b04e2cd54e'),
    thread_id: '40b3eb18-4fa2-49c2-a24f-6c72378910e5',
    question_asked: true,
    confirmed: true,
    error: false,
    question: 'Lionel Messi will go to the Real Madrid in 2025',
    answer: 'GOAT!!!'
  }
]
```

