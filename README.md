# Expense Splitter API

A REST API for tracking and splitting shared expenses within groups — think "Splitwise" backend. Built with FastAPI and PostgreSQL, it handles user authentication, group management, expense logging, and automatic debt calculation (who owes who, and how much) across multiple group members.

**Live demo:** https://expense-splitter-jje7.onrender.com/docs
*(Hosted on Render's free tier — the first request after a period of inactivity may take 30–50 seconds to wake up.)*

## Features

- JWT-based authentication with hashed passwords (bcrypt)
- Group and membership management (many-to-many user-group relationships)
- Expense creation with automatic equal-split calculation across participants
- Separate tracking of "who paid what" and "who owes what" per expense
- A balances endpoint that aggregates debts and payments across a group into net balances per person
- Redis caching on the balances calculation
- A demonstrated fix for an N+1 query problem using SQLAlchemy eager loading
- A raw SQL query example (aggregation with `JOIN` + `GROUP BY`) alongside the ORM-based queries
- CORS, request logging, and rate limiting on the login endpoint
- Automated tests with pytest
- Alembic-managed database migrations

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (2.0 style)
- **Migrations:** Alembic
- **Caching:** Redis
- **Auth:** passlib (bcrypt) + python-jose (JWT)
- **Validation:** Pydantic
- **Testing:** pytest + FastAPI's TestClient
- **Deployment:** Render

## Database Schema

The API is built around 6 relational tables, designed to cleanly separate *who owes what* from *who paid what* — treating them as two independent facts rather than conflating them.

**Users** — `user_id`, `user_name`, `password_hash`
Represents an individual using the app. Passwords are never stored in plain text.

**Groups** — `group_id`, `group_name`
A collection of users who share expenses together (e.g. roommates, a trip).

**UserGroup** — `user_group_id`, `user_id` (FK), `group_id` (FK)
A many-to-many join table linking users to groups, since a user can belong to multiple groups and a group has multiple users.

**Expenses** — `expense_id`, `expense_name`, `amount`, `group_id` (FK), `created_at`
A single expense event tied to a group (e.g. "Dinner — $30").

**Paid** — `paid_id`, `user_id` (FK), `expense_id` (FK), `paid_amount`
Records who actually paid money toward an expense, and how much. Not every participant necessarily appears here — only those who contributed a payment.

**Debt** — `debt_id`, `user_id` (FK), `expense_id` (FK), `amount_owed`
Records each participant's fair share of an expense, regardless of whether they paid anything toward it.

### Why separate `Paid` and `Debt`?

A single "amount" per person isn't enough to describe an expense — you need to know both **how much someone was required to contribute** (their fair share) and **how much they actually paid**, and these are often different numbers for the same person on the same expense. Someone might pay more than their share, less than their share, or nothing at all. Storing these as two separate tables preserves that distinction, and lets the API calculate each person's net balance (paid − owed) to determine who owes who.

## API Endpoints

| Method | Path | Description | Auth required |
|---|---|---|---|
| GET | `/` | Health check | No |
| POST | `/users` | Register a new user | No |
| GET | `/users` | List all users | No |
| GET | `/users/{user_id}` | Get a single user | No |
| PUT | `/users/{user_id}` | Update a user | No |
| DELETE | `/users/{user_id}` | Delete a user | **Yes** |
| POST | `/login` | Log in and receive a JWT | No (rate-limited) |
| POST | `/groups` | Create a group | No |
| GET | `/groups` | List all groups | No |
| GET | `/groups/{group_id}` | Get a single group | No |
| PUT | `/groups/{group_id}` | Update a group | No |
| DELETE | `/groups/{group_id}` | Delete a group | No |
| POST | `/usergroups` | Add a user to a group | No |
| POST | `/expenses` | Create an expense with automatic splitting | No |
| GET | `/expenses` | List all expenses | No |
| GET | `/expenses/{expense_id}` | Get a single expense | No |
| PUT | `/expenses/{expense_id}` | Update an expense | No |
| DELETE | `/expenses/{expense_id}` | Delete an expense | No |
| GET | `/groups/{group_id}/balances` | Net balances per user in a group (Redis-cached) | No |
| GET | `/groups/{group_id}/expenses-with-payments` | Expenses with payment detail (eager-loaded) | No |
| GET | `/groups/{group_id}/debts-raw-sql` | Total owed per user, via raw SQL | No |

*Auth is currently applied to one route as a proof of concept; rolling it out to the remaining write/delete endpoints is a known next step (see "Known limitations" below).*

## Design Decisions & What I Learned

- **Schemas vs. models:** request/response schemas (Pydantic) and database models (SQLAlchemy) are kept strictly separate, even when they share field names — e.g. a `UserCreate` schema never leaks into what gets stored, and a `UserResponse` schema deliberately excludes `password_hash` from every response.
- **N+1 queries:** an early version of the `expenses-with-payments` endpoint queried the `Paid` table once per expense inside a loop. I measured this directly by logging SQL queries (3 expenses → 5 queries) and fixed it with a SQLAlchemy `relationship()` + `joinedload()`, reducing it to 2 queries regardless of expense count — verified with the same logging.
- **Caching:** the balances endpoint recomputes debts and payments from scratch on every request unless the result is cached in Redis. I verified the cache was actually working by comparing the SQL query logs on a cache miss vs. a cache hit.
- **Security-conscious naming:** the password column is named `password_hash`, not `password`, specifically so the field name itself signals that raw passwords should never be stored there.
- **Generic auth errors:** the login endpoint returns the same error message ("Invalid username or password") whether the username doesn't exist or the password is wrong, to avoid leaking which part of the credentials was incorrect (username enumeration).

## Known Limitations / Next Steps

- **Authorization is not yet implemented.** Authentication (proving who you are) is fully working, but authorization (restricting actions to the right people) is not — any authenticated user can currently modify or delete any resource. Planned for v2: either simple ownership checks or group-admin roles.
- **Only one route is currently protected** with authentication as a proof of concept; extending it to the remaining write/delete endpoints is a mechanical next step.
- **No settlement-matching algorithm yet.** The balances endpoint returns raw net balances per person rather than a simplified "who pays who" minimum-transaction list. Planned for v2.
- **Tests run against the real development database**, not an isolated test database, so test data can accumulate over time.

## Setup Instructions (Local Development)

1. Clone the repository and create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a PostgreSQL database and a local Redis instance.
4. Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/expense_splitter
   REDIS_HOST=localhost
   REDIS_PORT=6379
   SECRET_KEY=your-random-secret-key
   ALGORITHM=HS256
   ```
5. Run the database migrations:
   ```
   alembic upgrade head
   ```
6. Start the server:
   ```
   uvicorn app.main:app --reload
   ```
7. Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

### Running Tests

```
pytest
```
