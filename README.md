# Contract Clause Tracker

A tool for labeling and tracking clause types within contracts, letting users categorize individual sentences by their legal function.

**Entities:**
- **Contracts**: Each file represents a contract (`.txt` or `.md`).
- **Sentences**: Each contract is auto-parsed into sentences on upload.
- **Clauses (Labels)**: Each sentence can optionally be labeled with a clause type.

## Getting Started

```bash
git clone <repo-url>
cd contract-clause-tracker
docker compose up --build
compose exec backend uv run pytest #Run tests
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:4200`

---

## Backend

**Stack:** FastAPI, SQLAlchemy, SQLite, NLTK

### Contract Management

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contracts/` | Retrieve all contracts. Supports `?search=` (filename) and `?clause_id=` filters. |
| GET | `/contracts/{contract_id}` | Retrieve a contract with all its sentences and their labels. |
| POST | `/contracts/` | Upload a contract. Accepts a `.txt` or `.md` file via multipart form (`file` field). |

### Sentence Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| PATCH | `/sentences/{sentence_id}` | Update a sentence's clause label. Body: `{ "label_id": <int or null> }` |

### Clause Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clauses/` | Retrieve all clause types (seeded on startup). |

**Seeded clauses:** Limitation of Liability, Termination for Convenience, Non-Compete, Confidentiality, Indemnification, Force Majeure.

---

## Frontend

**Stack:** Angular 21, Angular Material, TypeScript, RxJS

### Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard: lists all contracts, search by filename, filter by clause type, upload new contracts. |
| `/contracts/:id` | Contract detail: view all sentences, assign or remove clause labels per sentence. |
