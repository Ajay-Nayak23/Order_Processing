# # import stomp

# # class MsgListener(stomp.ConnectionListener):
# #     def __init__(self):
# #         self.msg_recieved = 0
# #     def on_error(self, message):
# #         print('Received the error:' + message)
    
# #     def on_message(self, message):
# #         print('Received the error:' + message)
# #         self.msg_recieved +=1

# # host = [('localhost', 61613)]
# # conn = stomp.Connection(host_and_ports=host)
# # conn.set_listener('listener', MsgListener())
# # conn.connect('admin','admin', wait=True)
# # conn.subscribe(destination='/queue/order.processing',id=1, headers={})


 


# import json, stomp, pyodbc
# from datetime import datetime

# MQ_HOST = 'localhost'
# MQ_PORT = 61613
# MQ_USER = 'admin'
# MQ_PASS = 'admin'
# QUEUE = '/queue/order.processing'

# # MSSQL connection string via pyodbc
# conn_str = (
#     'DRIVER={ODBC Driver 17 for SQL Server};'
#     'SERVER=LT-GLCVYB4;'
#     'DATABASE=order_db;'
#     'Trusted_Connection=yes;'
# )


# # conn_str = (
# #     'DRIVER={ODBC Driver 17 for SQL Server};'
# #     'SERVER=localhost,1433;'
# #     'DATABASE=order_db;'
# #     'UID=order_user;'
# #     'PWD=OrderPass!123;'
# #     'Encrypt=yes;'
# #     'TrustServerCertificate=yes;'
# # )


# # def get_unit_price(product_id):
# #     # simple stub — replace with real lookup
# #     price_map = {'P-001': 100.0, 'P-002': 250.0}
# #     return price_map.get(product_id, 50.0)
# def get_unit_price(product_id):
#     cursor = db_conn.cursor()
#     cursor.execute("SELECT price FROM products WHERE id = ?", product_id)
#     row = cursor.fetchone()
#     if row:
#         return float(row[0])
#     return 50.0  # fallback if not found


# class OrderListener(stomp.ConnectionListener):
#     def __init__(self, conn, db_conn):
#         self.conn = conn
#         self.db_conn = db_conn

#     def on_message(self, frame):
#         headers = frame.headers
#         message = frame.body

#         msg = json.loads(message)
#         order_id = msg['order_id']

#         try:
#             cursor = self.db_conn.cursor()
#             cursor.execute("SELECT status FROM orders_order WHERE id = ?", order_id)
#             row = cursor.fetchone()
#             if not row:
#                 self.conn.ack(headers['message-id'], headers['subscription'])
#                 return

#             status = row[0]
#             if status == 'PROCESSED':
#                 self.conn.ack(headers['message-id'], headers['subscription'])
#                 return

#             unit_price = get_unit_price(msg['product_id'])
#             subtotal = unit_price * msg['quantity']
#             total_price = round(subtotal * 0.9, 2)
#             processed_at = datetime.utcnow()

#             cursor.execute("""
#                 UPDATE orders_order
#                 SET status = ?, total_price = ?, processed_at = ?
#                 WHERE id = ?
#             """, ('PROCESSED', total_price, processed_at, order_id))
#             self.db_conn.commit()

#             self.conn.ack(headers['message-id'], headers['subscription'])
#             print(f"✅ Processed order {order_id}, total_price={total_price}")

#         except Exception as e:
#             print(f"❌ Processing failed for order {order_id}: {e}")
#             try:
#                 cursor.execute("UPDATE orders_order SET status = ? WHERE id = ?", ('FAILED', order_id))
#                 self.db_conn.commit()
#             except:
#                 pass

# def main():
#     db_conn = pyodbc.connect(conn_str, autocommit=False)
#     conn = stomp.Connection12([(MQ_HOST, MQ_PORT)])
#     listener = OrderListener(conn, db_conn)
#     conn.set_listener('', listener)
#     conn.connect(MQ_USER, MQ_PASS, wait=True)
#     conn.subscribe(QUEUE, id=1, ack='client-individual')
#     print("Listening...")
#     # keep alive
#     import time
#     while True:
#         time.sleep(10)

# if __name__ == '__main__':
#     main()


# # import pyodbc

# # conn_str = (
# #     "DRIVER={ODBC Driver 17 for SQL Server};"
# #     "SERVER=localhost,1433;"
# #     "DATABASE=order_db;"
# #     "UID=order_user;"
# #     "PWD=OrderPass!123;"
# # )
# # conn = pyodbc.connect(conn_str)
# # print("✅ Connected successfully!")
