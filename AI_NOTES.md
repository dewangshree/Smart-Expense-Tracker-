# AI Notes

This document explains how AI tools were used while building the Smart Expense Tracker API, per the assignment's requirement.

## 1. What was AI-generated vs. written by me

**AI-assisted (scaffolding / boilerplate):**
- Initial project structure (`src/api`, `src/services`, `src/schemas`, `src/models`, `src/storage`, `src/utils`) — I asked the AI for a layered FastAPI layout (routes → service → storage) rather than a single-file app, so the code is easier to test and extend.
- First draft of the Pydantic schemas (`ExpenseCreate`, `ExpenseResponse`, `TotalResponse`) and their field validators (empty title/category, non-positive amount).
- First draft of `json_storage.py` (read/write helpers) and the global `ValidationError` exception handler in `main.py`.
- First draft of the pytest suite in `tests/test_expenses.py`, including the `isolate_storage` fixture pattern for redirecting file I/O to a temp path per test.

**Written / decided by me:**
- Route design — which endpoints exist, `GET /expenses/total` as a separate endpoint rather than a query param on `/expenses`, and using `?category=` as a filter on both listing and totals.
- Choice of storage format (flat JSON list of dicts, not a nested structure) and folder layout under `src/`.
- Which validation rules to enforce (e.g. rejecting whitespace-only titles, not just empty strings).
- Decision to make category filtering case-insensitive.
- The specific edge cases covered in the test suite (see `README.md` → "Edge Cases Handled") — I went through the requirement list manually and added cases the first AI draft didn't cover.
- Picking Swagger/OpenAPI (FastAPI's built-in `/docs`) as the one optional bonus, instead of Docker or a search endpoint, since it required no extra code and is genuinely useful for a reviewer testing the API by hand.

## 2. What I validated, tested, or changed in the AI's output, and why

- **Ran the full test suite locally** (`pytest tests/ -v`) on a clean virtual environment before submitting — all 20 tests pass. I didn't take "the tests pass" on faith from the AI; I re-ran them myself after every change to `expense_service.py`.
- **`json_storage.py` handles a corrupted data file by design**: it catches `json.JSONDecodeError`, logs the problem, and returns an empty list instead of crashing the app, and `_ensure_file()` creates `expenses.json` automatically if it's missing. I reviewed this logic directly in the source rather than only trusting the AI's explanation of what it wrote.
- **404 vs 422 behavior is covered by automated tests**, not just manual poking — `test_delete_nonexistent_expense_returns_404` confirms deleting an unknown id returns `404`, and the validation tests (`test_create_expense_zero_amount`, `test_create_expense_negative_amount`, `test_create_expense_invalid_date`, etc.) confirm bad payloads return `422` with per-field messages rather than a generic 500.
- **Case-insensitive category filtering and total rounding are also test-backed**: `test_filter_by_category_case_insensitive` confirms `Food` and `food` match, and `test_total_by_category` / `test_total_all_expenses` confirm the `round(..., 2)` total math produces the expected sums.
- **Removed unused/generic code** the AI suggested — e.g. an initial version added a `PUT /expenses/{id}` update endpoint that wasn't in the requirements; I dropped it to keep the surface area matching the spec exactly, since the brief only asks for add/view/filter/total/delete.

## 3. AI suggestions I decided not to use, and why

- **A SQLite-backed storage layer** — the AI suggested swapping the JSON file for SQLite "for realism." I kept the JSON file because the assignment explicitly says no database is required, and a flat file is simpler to review and matches the spec.
- **Docker support as the bonus** — considered, but since only one bonus is required and Docker adds a dependency the reviewer has to have installed just to run `docker build`, I went with Swagger/OpenAPI instead, which works out of the box with zero extra setup.
- **A generic `try/except Exception` wrapper around every route** — the AI proposed this for "safety." I declined it because it would swallow real bugs (e.g. a typo in a service function) and mask them as generic 500s instead of surfacing them during testing.
- **Auto-generating UUIDs on the client side** — the AI's first draft accepted an optional `id` field in `ExpenseCreate`, letting the caller set their own id. I removed that field entirely so the server always generates the id (`uuid4()`), avoiding duplicate-id collisions.

---

*This file was drafted with AI assistance and reviewed/edited by me before submission, consistent with how the code itself was built.*
