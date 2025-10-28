# 🧾 Order Processing System — Django + ActiveMQ + SQL Server

## 📘 Overview
This project demonstrates a **message-driven Order Processing System** built using:
- **Django** (Producer service)
- **ActiveMQ** (Message broker)
- **Python Consumer** (Worker service)
- **Microsoft SQL Server** (Database)

The system simulates how e-commerce or enterprise apps handle orders **asynchronously** — ensuring reliable and scalable background processing.

---

Workflow:

The user submits an order through the Django form.

Django saves it to the database with status='pending'.

Django publishes the order details to ActiveMQ.

The Python Consumer listens for new messages.

The consumer calculates the total price and updates the order as status='PROCESSED'.

⚙️ Components
🟢 Django (Producer)
Handles order creation through a simple form.

Publishes order data to ActiveMQ using stomp.py.

Updates order status to:

pending → initially created.

processed → successfully sent to queue.

failed → message publish failed.

🔵 ActiveMQ
Acts as the message broker between producer and consumer.

Queue: /queue/order.processing

🟠 Consumer (Python Script)
Listens to the ActiveMQ queue.

Fetches messages in JSON format.

Updates SQL Server:

Calculates total price.

Sets status='PROCESSED'.

Adds processed_at timestamp.

🟣 SQL Server
Stores all order details:

id

customer_name

product_id

quantity

status

total_price

created_at

processed_at

## 🧩 Project Structure

    order_processing_system/
    │
    ├── producer/ # Django project (Producer service)
    │ ├── orders/ # Orders app
    │ │ ├── models.py # Order model (database schema)
    │ │ ├── views.py # Handles order form & message publishing
    │ │ ├── forms.py # Django form for order submission
    │ │ └── templates/ # HTML templates
    │ │ ├── order.html # Order form page
    │ │ └── success.html # Success message page
    │ └── manage.py # Django management script
    │
    ├── consumer/ # Consumer service
    │ └── consumer.py # Listens to ActiveMQ and processes orders
    │
    ├── requirements.txt # Python dependencies
    └── README.md # Project documentation







🚀 Setup & Installation
1️⃣ Start ActiveMQ (Docker)
bash
Copy code
docker run -d \
  -e 'ACTIVEMQ_ADMIN_LOGIN=admin' \
  -e 'ACTIVEMQ_ADMIN_PASSWORD=admin' \
  -p 8161:8161 -p 61613:61613 \
  --name activemq \
  rmohr/activemq:latest
Visit ActiveMQ Console → http://localhost:8161/admin (login: admin/admin)

2️⃣ Setup SQL Server (Docker or Local)
If using Docker:

bash
Copy code
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourStrong!Pass1' \
   -p 1433:1433 --name mssql \
   mcr.microsoft.com/mssql/server:2022-latest
Create the database:

sql
Copy code
CREATE DATABASE order_db;
3️⃣ Setup Django (Producer)
bash
Copy code
cd producer
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Open → http://127.0.0.1:8000/orders/

4️⃣ Run Consumer (Worker)
In another terminal:

bash
Copy code
cd consumer
python consumer.py
You should see:
Connected and listening to ActiveMQ.
Processed order 1: unit_price=90.0, total_price=180.0

🧠 Example Message
json
Copy code
{
  "order_id": 1,
  "customer_name": "Ajay",
  "product_id": "P123",
  "quantity": 2
}
📊 Status Flow
Stage	Description
pending	Order saved in DB, not yet sent to queue
processed	Successfully published to ActiveMQ
PROCESSED	Consumer picked and updated successfully
FAILED	Error occurred during processing

🛠️ Technologies Used
Python 3.11+

Django 5.x

ActiveMQ 5.x

stomp.py

pyodbc

SQL Server 2022

📹 Recommended Demo Flow
Run Django and create a new order.

Show message published in console.

Open ActiveMQ admin → show message queue.

Run consumer → show message processing log.

Show SQL Server table update (status, total_price, processed_at).
 
