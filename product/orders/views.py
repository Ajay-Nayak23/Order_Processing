import json
import stomp


from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import OrderForm


MQ_HOST = 'localhost'
MQ_PORT = 61613
MQ_USER = 'admin'
MQ_PASS = 'admin'
QUEUE = '/queue/order.processing'



def publish_message(message):
    try:
        body = json.dumps(message)
        conn = stomp.Connection([(MQ_HOST, MQ_PORT)])
        conn.connect(MQ_USER, MQ_PASS, wait=True)
        conn.send(body=body, destination=QUEUE, headers={'content-type': 'application/json'})
        print("✅ Message published:", message)
    finally:
        conn.disconnect()
  
    

# Create your views here.
def order_list(request):
    if request.method == 'POST':
        form=OrderForm(request.POST)

        if form.is_valid():
            order=form.save(commit=False)
            order.status='pending'
            order.save() 

            message={
                'order_id':order.id,
                'customer_name':order.customer_name,
                'product_id':order.product_id,
                'quantity':order.quantity
            }

            try:
                publish_message(message)
                order.status='pending'
                order.save()
                return render(request, 'success.html',{'order_id':order.id})
            except Exception as e:
                print("❌ Failed to publish message:", e)
                order.status = 'failed'
                order.save()
                return render(request, 'order.html', {'form': form, 'error': 'Failed to process order.'})

           
        else:
            return render(request, 'order.html', {'form': form, 'error': 'Invalid data submitted.'})

    else:
            form=OrderForm()   
    return render(request,'order.html',{'form':form})         