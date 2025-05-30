from django.contrib import admin
from .models import Category,Item,CustomerOrder,OrderDetail
# Register your models here.
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(CustomerOrder)
admin.site.register(OrderDetail)
