from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('signup/',views.signupPage,name='signup'),
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('search/',views.search,name='searchresults'),
    path('cart/',views.viewCart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('order/',views.orderFinal,name='order'),
    path('prevOrders/',views.previousOrders,name='prevOrder'),
    path('charts/',views.charts, name='charts'),
]