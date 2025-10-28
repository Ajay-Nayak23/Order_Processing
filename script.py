import json
import time
import stomp
import pyodbc
from datetime import datetime

# ---------------- ActiveMQ Config ----------------
MQ_HOST = 'localhost'
MQ_PORT = 61613
MQ_USER = 'admin'
MQ_PASS = 'admin'
QUEUE = '/queue/order.processing'

# ---------------- SQL Server Config ----------------
CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=LT-GLCVYB4;'
    'DATABASE=order_db;'
    'Trusted_Connection=yes;'
    'Encrypt=yes;'
    'TrustServerCertificate=yes;'
)

# ---------------- Utility Functions ----------------
def get_db_connection():
    """Create a new database connection."""
    try:
        return pyodbc.connect(CONN_STR, autocommit=True)
    except Exception as e:
        print("DB connection failed:", e)
        return None


# ---------------- Listener Class ----------------
class OrderListener(stomp.ConnectionListener):
    def __init__(self, conn):
        self.conn = conn

    def on_disconnected(self):
        print("Disconnected from ActiveMQ — reconnecting...")
        reconnect_mq(self.conn)

    def on_message(self, frame):
        headers = frame.headers
        message = frame.body

        try:
            msg = json.loads(message)
            order_id = msg.get('order_id')
            quantity = msg.get('quantity', 1)

            db_conn = get_db_connection()
            if not db_conn:
                print("DB connection unavailable. Skipping order", order_id)
                return

            cursor = db_conn.cursor()
            cursor.execute("SELECT status FROM dbo.orders_order WHERE id = ?", (order_id,))
            row = cursor.fetchone()

            if not row:
                print("Order not found:", order_id)
                db_conn.close()
                return

            status = row[0]
            if status == 'PROCESSED':
                print("Order already processed:", order_id)
                db_conn.close()
                return

            # --- Fixed Pricing Logic ---
            base_price = 100.0
            discounted_price = base_price * 0.9
            total_price = round(discounted_price * quantity, 2)
            processed_at = datetime.utcnow().isoformat()

            # --- Update Order ---
            cursor.execute("""
                UPDATE dbo.orders_order
                SET status = ?, total_price = ?, processed_at = ?
                WHERE id = ?
            """, ('PROCESSED', total_price, processed_at, order_id))
            db_conn.close()

            print(f"Processed order {order_id}: unit_price={discounted_price}, total_price={total_price}")

        except Exception as e:
            try:
                db_conn = get_db_connection()
                if db_conn:
                    cursor = db_conn.cursor()
                    cursor.execute(
                        "UPDATE dbo.orders_order SET status = ? WHERE id = ?",
                        ('FAILED', msg.get('order_id', 0))
                    )
                    db_conn.close()
            except Exception as inner_e:
                print("Could not mark order as FAILED:", inner_e)


# ---------------- Connection Helpers ----------------
def reconnect_mq(conn):
    """Reconnect to ActiveMQ."""
    while True:
        try:
            conn.connect(MQ_USER, MQ_PASS, wait=True)
            conn.subscribe(destination=QUEUE, id='order_listener', ack='auto')
            print("Connected and listening to ActiveMQ.")
            return
        except Exception as e:
            print("ActiveMQ reconnect failed:", e)
            time.sleep(5)


# ---------------- Main Runner ----------------
def main():
    print("Starting Order Processor...")
    conn = stomp.Connection12([(MQ_HOST, MQ_PORT)])
    listener = OrderListener(conn)
    conn.set_listener('', listener)

    reconnect_mq(conn)

    print("Listening for order messages...")
    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
