from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup_view, name="signup"),
    path("cart", views.cart_view, name="cart"),
    path("order", views.order_view, name="order"),
    path("topping/<int:cart_id>/", views.topping_view, name="topping"),
    path("removefromcart/<int:cart_id>/", views.removefromcart_view, name="removefromcart"),
    path("apert_caja/", views.apertura_caja_view, name="apert_caja"),
    path("agregar_monto/", views.agregar_monto),
    path("ventas/", views.ventas_view, name="ventas"),
    path('order/<int:order_number>/', views.order_detail, name='order_detail'),
    path("eliminarOrden/<int:order_number>/", views.eliminarOrden, name="eliminarOrden"),
    path("pagarOrden/<int:order_number>/", views.pagarOrden, name="pagarOrden"),
    path("mesas/", views.mesas_view, name="mesas"),
    path("facturas/", views.facturas_view, name="facturas"),
    path('convert_to_pdf/', views.convert_to_pdf, name='convert_to_pdf'),
    ]
    
