# Scoring API

Structure of request:

{"account": "", "login": "", "method": "", "token": "", "arguments": {}}

* account ‑ sting, not required, can be empty
* login ‑ sting, required, can be empty
* method ‑ sting, required, can be empty
* token ‑ sting, required, can be empty
* arguments ‑ dict (json object), required, can be empty


## Getting Starter

To run server, please type: python api.py

Optional parameters:
--port , --log  


Examples requests:

curl -X POST  -H "Content-Type: application/json" -d '{"account": "user", "login":"user","method": "online_score","token":"aa34e991ff440298f58c8021c8ce0d337fdc01e75488f6fbae94a16e7c8c2ed49514e8da4df2ec398bcdd67ca5bd9a3600d2b09c698a27c6e0a2dad8eee9a634",
 "arguments": {"phone": "79175002040", "email": "ivanov@otus.ru", "first_name": "Ivanov",
"last_name": "Иванов", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/

curl -X POST  -H "Content-Type: application/json" -d '{"account": "user", "login": "user",
"method": "clients_interests", "token":
"aa34e991ff440298f58c8021c8ce0d337fdc01e75488f6fbae94a16e7c8c2ed49514e8da4df2ec398bcdd67ca5bd9a3600d2b09c698a27c6e0a2dad8eee9a634",
 "arguments": {"client_ids": [1,2,3,4], "date": "20.07.2017"}}' http://127.0.0.1:8080/method/


## Prerequisites

Python version 2.7

## Installing

No special installation procedure is required. 

## License

This project is licensed under the MIT License

