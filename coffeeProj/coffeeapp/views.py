import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
from coffeeapp.models import Item, Category, CustomerOrder, OrderDetail
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import CreateCustomer
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.utils.timezone import make_aware
import json


# Create your views here.

def index(request): #home page
    context = {
        'items': Item.objects.all(),
        'categories': Category.objects.all(),
    }
    ##request.session.flush() ##clear the session - remove only if coming from order.html
    if request.method == 'POST':
        if not request.session.has_key('cart'):  ##create a cart if it doesn't exist
            request.session['cart'] = {}
        cart = request.session.get('cart')

        for item in Item.objects.all():
            if request.POST.get('q'+str(item.id)) is not None:
                quantity = int(request.POST.get('q'+str(item.id)))
                if (request.POST.get('addToCart' + str(item.id))) and (quantity != 0):  ##if addToCart exists for that item
                    price = item.ItemPrice
                    messages.success(request, str(quantity) + ' ' + item.ItemName + ' of price ' + str(price) + ' is added to cart successfully!')
                    if(cart.get(item.ItemName) is not None): ##if item already exists in cart
                        quantity = cart.get(item.ItemName).get('quantity') + quantity
                    cart.update({item.ItemName: {'id':item.id, 'quantity': quantity, 'price': price}})

    return render(request, 'coffeeapp/index.html', context)

def search(request): ##Search by name or by category - WORKS FINE
    iName = request.GET.get('name') #get name; default = None
    iCat = request.GET.get('cat') #get category selected; default = 'All'
    queryset = Item.objects.all() #default - return all items

    if iName is not None and iCat != 'All':     #If name is 'something' and category is something
        queryset = Item.objects.filter(Q(category=iCat) &Q(ItemName__icontains=iName)) #get items based on both
    else:
        if iName is not None: #if only name is entered
            queryset = Item.objects.filter(Q(ItemName__icontains=iName))
        elif iCat is not None: #if category search is used
            queryset = iCat.item_set.all()
    context = { #send search result items and all categories
        'items': queryset,
        'categories': Category.objects.all(), #all categories are sent because they are used to populate the drop-down list in index.html
    }
    return render(request, 'coffeeapp/index.html', context)

def signupPage(request):
    context ={}
    if request.POST: #if register button is clicked
        signForm = CreateCustomer(request.POST) #get register form data
        if signForm.is_valid(): #if validity checking is okay
            signForm.save()
            usern = signForm.cleaned_data.get('username') #get username from the form
            messages.success(request,'Account ' + usern + ' successfully created!') #send a flash message to the login page that displays the user is created successfully
            return redirect('login') #redirect to login page
        else:
            context['signForm'] = signForm #if not valid then load the same form again - and display errors
    else: #GET - user first goes to register page
        signForm = CreateCustomer() #empty form
        context['signForm'] = signForm
    return render(request, 'coffeeapp/signup.html', context)

def loginPage(request):
    context = {}
    if request.POST: #get login user name and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        cUser = authenticate(request, username=username, password=password) #authenticate the username and password

        if cUser is not None: #if valid
            login(request,cUser) #login user
            if request.session.get('fromCheck'): ##if came from cart page then after logging in, redirect to checkout
                return redirect('checkout') #give access to checkout page
            else: ##if logging in normally then redirect back to main page
                return redirect('index')
        else:
            messages.info(request,'Username or password is incorrect') #Error message if not valid
            return render(request, 'coffeeapp/login.html', context) #load same page and display error message if not valid

    return render(request, 'coffeeapp/login.html', context)

def logoutUser(request):
    logout(request) #logout current user and redirect to login page
    return redirect('login')

def viewCart(request): #COMPLETE
    request.session['totalPrice'] = 0
    if request.GET.get('Clear') == 'True':
        request.session['cart'] = {}

        context = {
            'cart': None,
            'totalPrice': 0
        }
    else:
        cart = request.session.get('cart')
        quantity= 0; price = 0; tp=0
        if cart is not None:
            for item in cart.copy().keys():
                if request.GET.get(item) == 'True':
                    del cart[item]
                    break
            for item in cart.items():
                for k,v in item[1].items():
                    if(k == 'quantity'):
                        quantity=v
                    elif(k == 'price'):
                        price=v
                    itemPrice = quantity*price
                tp +=itemPrice
            request.session['totalPrice'] = tp
            context = {
                'cart': cart,
                'totalPrice': request.session.get('totalPrice')
            }
        if cart=={} or cart is None:
            context = {
                'cart': None,
                'totalPrice': request.session.get('totalPrice')
            }
    return render(request, 'coffeeapp/cart.html', context)

def checkout(request):
    ##access to only logged in users
    if(request.user.is_authenticated):
        context={
            'cart': request.session.get('cart'),
            'customer': User.objects.get(id=request.user.id)
        }
        return render(request, 'coffeeapp/checkout.html', context)
    else:
        messages.info(request,'Please login before you checkout!')
        request.session['fromCheck']=True ##used to notify if the user has come from cart->login (to redirect to checkout after login)
        return redirect('login')

def orderFinal(request): ##here add to Customer order and order details and update quantity_sold of items
    cust = User.objects.get(id=request.user.id)
    newOrder = CustomerOrder(cust_id=cust, OrderDate=make_aware(datetime.datetime.now()), TotalPrice=request.session.get('totalPrice'))
    newOrder.save()

    newOrder = CustomerOrder.objects.last()

    for item in request.session['cart'].items():
        i_id = item[1].get('id')
        o_item = Item.objects.get(id = i_id)
        o_item.quantity_sold += item[1].get('quantity')
        o_item.save()
        ord_det = OrderDetail(order_det_id=newOrder,item_det_id=o_item,item_price=item[1].get('price'),item_bought_quant=item[1].get('quantity'))
        ord_det.save()
    request.session['cart'] = {}
    return render(request, 'coffeeapp/finalOrder.html', {})

def previousOrders(request):
    prevOrder={}
    cust = User.objects.get(id=request.user.id)
    orders = CustomerOrder.objects.filter(cust_id=cust)
    print(orders) ##check condition if order is empty or none
    for order in orders:
        orderDict = {}
        od = OrderDetail.objects.filter(order_det_id=order)
        if (od.count() > 0):
            for something in od:
                orderDict[something.item_det_id] = {'quantity':something.item_bought_quant, 'price': something.item_price}
        prevOrder[order] = orderDict

    context = {'prevOrders': prevOrder}
    return render(request, 'coffeeapp/prevOrders.html', context)

def charts(request):
    catg_total = {}
    for c in Category.objects.all():
        for i in c.item_set.all():
            if catg_total.get(c.name) is None:
                catg_total[c.name] = i.quantity_sold
            else:
                catg_total[c.name] += i.quantity_sold

    
    context = {
        'item':Item.objects.all(),
        'cat_total':catg_total
    }
    return render(request,'coffeeapp/charts.html',context)