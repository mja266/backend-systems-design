# TEST CASES — Backend API

## Base URL

http://127.0.0.1:5000

---

# ✅ USERS ENDPOINTS

## 1. GET /users (All users)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/users" -Method GET
```

**Expected**

* 200 OK
* Returns list of users

**Result**

* ✔️ Passed

---

## 2. GET /users/<id> (Valid user)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/users/1" -Method GET
```

**Expected**

* 200 OK
* Returns user object

**Result**

* ✔️ Passed

---

## 3. GET /users/<id> (Invalid user)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/users/999" -Method GET
```

**Expected**

* 404 Not Found
* {"error": "User not found"}

**Result**

* ✔️ Passed

---

## 4. POST /users (Valid)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/users" `
-Method POST `
-Headers @{"Content-Type"="application/json"} `
-Body '{"name":"Test","email":"test@email.com"}'
```

**Expected**

* 201 Created

**Result**

* ✔️ Passed

---

## 5. POST /users (Missing fields)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/users" `
-Method POST `
-Headers @{"Content-Type"="application/json"} `
-Body '{"name":"Test"}'
```

**Expected**

* 400 Bad Request
* {"error": "Name and email required"}

**Result**

* ✔️ Passed

---

# ✅ TASKS ENDPOINTS

## 6. GET /tasks

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" -Method GET
```

**Expected**

* 200 OK
* Returns list of tasks

**Result**

* ✔️ Passed

---

## 7. GET /tasks/<id> (Valid)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/3" -Method GET
```

**Expected**

* 200 OK

**Result**

* ✔️ Passed

---

## 8. GET /tasks/<id> (Invalid)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/1" -Method GET
```

**Expected**

* 404 Not Found

**Result**

* ✔️ Passed

---

## 9. POST /tasks (Valid)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" `
-Method POST `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Test Task","user_id":1}'
```

**Expected**

* 201 Created

**Result**

* ✔️ Passed

---

## 10. POST /tasks (Missing user_id)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" `
-Method POST `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Bad request"}'
```

**Expected**

* 400 Bad Request
* {"error": "Title and user_id required"}

**Result**

* ✔️ Passed

---

## 11. POST /tasks (Invalid JSON)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" `
-Method POST `
-Headers @{"Content-Type"="application/json"} `
-Body ''
```

**Expected**

* 400 Bad Request
* {"error": "Invalid JSON"}

**Result**

* ✔️ Passed

---

## 12. PUT /tasks/<id> (Valid)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/3" `
-Method PUT `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Updated Task","user_id":1,"completed":true}'
```

**Expected**

* 200 OK

**Result**

* ✔️ Passed

---

## 13. PUT /tasks/<id> (Invalid ID)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/999" `
-Method PUT `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Test","user_id":1,"completed":true}'
```

**Expected**

* 404 Not Found
* {"error": "Task not found"}

**Result**

* ✔️ Passed

---

## 14. DELETE /tasks/<id> (Valid)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/3" -Method DELETE
```

**Expected**

* 200 OK

**Result**

* ✔️ Passed

---

## 15. DELETE /tasks/<id> (Invalid ID)

**Command**

```
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/999" -Method DELETE
```

**Expected**

* 404 Not Found

**Result**

* ✔️ Passed

---

# ✅ SUMMARY

All endpoints behave as expected:

* Proper success responses (200 / 201)
* Proper validation errors (400)
* Proper missing resource handling (404)

System is functioning as a production-style backend API.
