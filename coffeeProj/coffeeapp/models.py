from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Initial data (for the categories & menu) is in fixtures -> data.json

class Category(models.Model): #categories a separate table
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"


class Item(models.Model):
    ItemName = models.CharField(max_length=30, unique=True)
    image = models.ImageField(default = "")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ItemPrice = models.FloatField()
    quantity_sold = models.IntegerField(default=0) #total quantity sold

    def __str__(self):
        return f"{self.ItemName}:    Type:{self.category}    Price:{self.ItemPrice}    Quantity sold:{self.quantity_sold}"


class CustomerOrder(models.Model):
    order_id = models.IntegerField(primary_key=True)
    cust_id = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='OrderDetail')
    OrderDate = models.DateTimeField()
    TotalPrice = models.FloatField()


class OrderDetail(models.Model):
    details_id = models.AutoField(primary_key=True)
    order_det_id = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)
    item_det_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_bought_quant = models.IntegerField()
    item_price = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if not self.item_price:
            self.item_price = self.Item.ItemPrice
        super(OrderDetail, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('order_det_id', 'item_det_id'),)