# Smart Expense Tracker API

A REST API for tracking personal expenses, built with **FastAPI** and **Pydantic**. Data is persisted to a local JSON file — no database required.

## Features

- Add an expense (`title`, `amount`, `category`, `date`)
- View all expenses
- Filter expenses by category (case-insensitive)
- Calculate total expenses — overall and filtered by category
- Delete an expense by id
- Input validation (empty title/category, zero or negative amount, invalid date, missing fields) with clear 422 error responses
- 404 responses for deleting a non-existent expense
- Auto-generated interactive API docs via FastAPI (Swagger UI + OpenAPI schema) — **bonus feature**

## Test Status

The project includes an automated test suite with **20 passing test cases** covering core functionality and edge cases:

```bash
20 passed
```

## Tech Stack

- Python 3.12
- FastAPI
- Pydantic v2
- Uvicorn (ASGI server)
- Pytest + httpx (testing)

## Project Structure

```
src/
  main.py                    # FastAPI app + global validation error handler
  api/expenses.py            # route definitions
  services/expense_service.py # business logic (create/list/filter/total/delete)
  schemas/expense_schema.py  # request/response models + field validation
  models/expense.py          # internal Expense model
  storage/json_storage.py    # JSON file read/write, corrupt-file handling
  utils/validators.py        # ISO date parsing helper
  data/expenses.json         # local data store (created automatically if missing)
tests/
  test_expenses.py           # 20 test cases covering happy paths + edge cases
```

## Setup & Installation

Requires Python 3.9 or later.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn src.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Interactive docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Running Tests

```bash
pytest tests/ -v
```

All tests run against an isolated temporary JSON file (via a `pytest` fixture), so they never touch `src/data/expenses.json`.

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/expenses` | Create a new expense |
| `GET` | `/expenses` | List all expenses (optional `?category=` filter) |
| `GET` | `/expenses/total` | Get total amount (optional `?category=` filter) |
| `DELETE` | `/expenses/{expense_id}` | Delete an expense by id |
| `GET` | `/health` | Health check |

### Example: Create an expense

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title": "Coffee", "amount": 3.50, "category": "Food", "date": "2026-08-01"}'
```

### Example: Filter by category

```bash
curl "http://127.0.0.1:8000/expenses?category=Food"
```

### Example: Total by category

```bash
curl "http://127.0.0.1:8000/expenses/total?category=Food"
```

## Edge Cases Handled

- Missing required fields → `422` with per-field error detail
- Empty/whitespace-only `title` or `category` → `422`
- Zero or negative `amount` → `422`
- Invalid date format → `422`
- Deleting an id that doesn't exist → `404`
- Filtering by a category with no matches → `200` with an empty list
- Category matching is case-insensitive (`Food` == `food`)
- Corrupted/unreadable `expenses.json` → API logs the error and falls back to an empty list instead of crashing
- Empty expense list → total returns `0.0` instead of erroring

## Notes

- Storage is a flat JSON file (`src/data/expenses.json`), auto-created on first run if it doesn't exist.
- See `AI_NOTES.md` for details on how AI tools were used while building this.
