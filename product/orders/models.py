from django.db import models

# Create your models here.
class Order(models.Model):
    status_choices=[
        ('pending','PENDING'),
        ('processed','PROCESSED'),
        ('failed','FAILED')
    ]
    customer_name=models.CharField(max_length=100)
    product_id=models.IntegerField()
    quantity=models.IntegerField()
    status=models.CharField(max_length=10,choices=status_choices,default='pending')
    total_price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    processed_at=models.DateTimeField(null=True,blank=True)

