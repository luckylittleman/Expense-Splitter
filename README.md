# Expense-Splitter
A backend REST API for tracking and splitting shared expenses within groups — think "Splitwise" backend. 

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic

## Features
It has the following features:
- User Authentication
- Group Management
- Expense Logging
- Automatic debt calculations across multiple group members

## Schema Overview
The API is built around 6 relational tables, designed to cleanly separate who owes what from who paid what, this treats the two independently rather than conflating them.

 **Users**— `user_id` ,`user_name`

 Represents an individual using the app.

 **Groups**— `group_id`, `group_name`

 A collection of users who share expenses together (e.g. roommates, a trip).

 **UserGroup** — `user_group_id`, `user_id (FK)`, `group_id (FK)`

 A many-to-many join table linking users to groups, since a user can belong to multiple groups and a group has multiple users.

 **Expenses** — `expense_id`, `expense_name`, `amount`, `group_id (FK)`, `created_at`

 A single expense event tied to a group (e.g. "Dinner — $30").

 **Paid** — `paid_id`, `user_id (FK)`, `expense_id (FK)`, `paid_amount`

 Records who actually paid money toward an expense, and how much. Not every participant necessarily appears here — only those who contributed a payment.

 **Debt** — `debt_id`, `user_id (FK)`, `expense_id (FK)`, `amount_owed`
 
 Records each participant's fair share of an expense, regardless of whether they paid anything toward it.

 ## Why separate Paid and Debt ?
 A single "amount" per person isn't enough to describe an expense — you need to know both how much someone was required to contribute (their fair share) and how much they actually paid, and these are often different numbers for the same person on the same expense. Someone might pay more than their share, less than their share, or nothing at all. Storing these as two separate tables preserves that distinction, and lets the API calculate each person's net balance (paid − owed) to determine who owes who.
