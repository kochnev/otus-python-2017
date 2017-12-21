# Scoring API

Structure of request:

{"account": "", "login": "", "method": "", "token": "", "arguments": {}}

account ‑ sting, not required, can be empty
login ‑ sting, required, can be empty
method ‑ sting, required, can be empty
token ‑ sting, required, can be empty
arguments ‑ dict (json object), required, can be empty


## Getting Starter

To run server, please type: python api.py

Optional parameters:
--port , --log  


Examples requests:

curl -X POST  -H "Content-Type: application/json" -d '{"account": "admin_test", "login":"admin","method": "online_score","token":"eed94f65ea73f6429ef74372307357652a4a5291906eb042e27401c29eebe7e6b510a7a6cb5cab32107aded8bff4b7593ff7db40ab988e20e29c296f819e2652",
 "arguments": {"phone": "79175002040", "email": "ivanov@otus.ru", "first_name": "Ivanov",
"last_name": "Иванов", "birthday": "01.01.199", "gender": 1}}' http://127.0.0.1:8080/method/

curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin",
"method": "clients_interests", "token":
"d3573aff1555cd67dccf21b95fe8c4dc8732f33fd4e32461b7fe6a71d83c947688515e36774c00fb630b039fe2223c991f045f13f2",
 "arguments": {"client_ids": [1,2,3,4], "date": "20.07.2017"}}' http://127.0.0.1:8080/method/


## Prerequisites

Python version 2.7

## Installing

No special installation procedure is required. 

## License

This project is licensed under the MIT License

