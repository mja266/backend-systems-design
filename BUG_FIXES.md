# Bug Fixes Log

## Bug 1 — Missing validation in POST /users

### What broke
POST /users allowed invalid input because validation was removed.

### Symptoms
Sending a request without an email caused a server crash (IntegrityError).

### Root cause
The API layer failed to validate input before inserting into the database.

### Fix
Reintroduced validation to ensure name and email are present before DB insert.

### Verification
- Invalid input → returns 400 error
- Valid input → user created successfully

## Bug 2 — Broken SQL query

### What broke
JOIN used incorrect table name.

### Symptoms
GET /tasks returned 500 error.

### Root cause
Typo in SQL table name.

### Fix
Corrected table name to "users".

### Verification
Endpoint returned valid JSON again.