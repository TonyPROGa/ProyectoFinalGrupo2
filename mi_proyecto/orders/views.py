from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from xhtml2pdf import pisa
from django.template.loader import render_to_string



from .models import Size, Category, Topping, Price_List, Item_List, Cart_List, Extra, Order, AperturaCaja, CierreCaja

# Create your views here.
def index(request):
	if not request.user.is_authenticated:
		return render(request, "orders/login.html", {"message": None})
	context = {
		"categories" : Category.objects.exclude(name="Topping").all(),
		"items" : Item_List.objects.all(),
		"toppings" : Topping.objects.all(),
		"extras" : Extra.objects.all(), 
		"sizes" : Size.objects.all(),
		"user" : request.user
	}
	return render(request, "orders/index.html", context)
    # return HttpResponse("Project 3: TODO")

def login_view(request):

    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
    	return render(request, "orders/login.html", {"message": "Invalid credentials."})
	# else:
	# return render(request, "orders/login.html")


def logout_view(request):
    logout(request)
    return render(request, "orders/login.html", {"message": "Logged out."})

def signup_view(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			login(request, user)
			return HttpResponseRedirect(reverse("index"))
		else:
			for msg in form.error_messages:
				print(form.error_messages[msg])
				return render (request = request,
                  template_name = "orders/signup.html",
                  context={"form":form})
	
	form = UserCreationForm        
	return render(request = request,
                  template_name = "orders/signup.html",
                  context={"form":form})

def cart_view(request):
	
	if request.method == "POST":
		item_id = request.POST.get("item_id")
		toppings = request.POST.getlist("topping_id")
		extras = request.POST.getlist("extra_id")
		size = request.POST.get("size_id")
		user = request.user

		p = Item_List.objects.get(pk=item_id)
		price_id = p.base_price_id.id

		# Calculate Price:

		# Calculate topping quantity
		count_topping = 0
		for topping in toppings: 
			count_topping+=1
		# Calculate extra quantity
		count_extra = 0
		for extra in extras: 
			count_extra+=1


		topping_price = Price_List.objects.get(name="Topping")
		extra_price = Price_List.objects.get(name="Extra")
		item = Price_List.objects.get(pk=price_id)


		# if large option selected
		if size and int(size) == 7:
			total_price = item.base_price + item.large_supp + count_topping*topping_price.large_supp + count_extra*extra_price.base_price
		else:
			total_price = item.base_price + count_topping*topping_price.base_price + count_extra*extra_price.base_price

		# Add new item to cart
		if size == None:
			new_item = Cart_List(user_id=user, item_id=Item_List.objects.get(pk = item_id), size=None, calculated_price=total_price)
		else:
			new_item = Cart_List(user_id=user, item_id=Item_List.objects.get(pk = item_id), size=Size.objects.get(pk = size), calculated_price=total_price)

		# add item to cart
		new_item.save()

		# add toppping and extras to item
		for topping in toppings: 
			new_item.toppings.add(topping)
		for extra in extras: 
			new_item.extra.add(extra)
		# return HttpResponseRedirect(reverse("cart"))
		messages.success(request, "¡Comida agregada al carrito!")
		return HttpResponseRedirect(reverse("index"))
		# return render(request, "orders/index.html", {"message": "Meal added to cart!"})

	else:
		try:
			cart = Cart_List.objects.filter(user_id=request.user, is_current=True)
		except Cart_List.DoesNotExist:
			raise Http404("Cart does not exist")
		
		total_price = cart.aggregate(Sum('calculated_price'))['calculated_price__sum']

		cart_ordered = Cart_List.objects.filter(user_id=request.user, is_current=False)

		context = {
		"cart_items" : cart,
		"total_price": total_price,
		"cart_items_ordered" : cart_ordered,
		}

		return render(request, "orders/cart.html", context)

def topping_view(request, cart_id):
	# view topping from cart

	try:
		pizza = Cart_List.objects.get(pk=cart_id)
	except Cart.DoesNotExist:
		raise Http404("Pizza not in Cart or does not include topping")
	context = {
		"toppings" : pizza.toppings.all()
		}
	return render(request, "orders/topping.html", context)


def order_view(request):
	# place an order

	if request.method == "POST":
		user = request.user
		items = request.POST.getlist("cart_id")
		print(items)

		new_order = Order(user_id=user, complete=False)
		new_order.save()

		todo = []
		total_price = 0
		for item in items:
			cart_item = Cart_List.objects.get(id=item)
			new_order.cart_id.add(cart_item)
			total_price += cart_item.calculated_price
			todo.append(str(cart_item))
		new_order.precio_total = total_price
		new_order.contenido = "\n".join(todo)
		new_order.save()





		# set current attribute to False 
		cart = Cart_List.objects.filter(user_id=request.user)
		for item in cart:
			item.is_current=False
			item.save()
		messages.success(request,"Se ha ralizado el pedido con éxito!")
		return HttpResponseRedirect(reverse("index"))
		# Obtener los elementos relacionados con la orden
		#order_items = new_order.cart_id.all()
		#order_total_price = sum(item.calculated_price for item in order_items)

        # Pasar los elementos relacionados con la orden como un contexto separado
		#context = {
            #"order_items": order_items,
            #"order_total_price": order_total_price,
        #}

		#return render(request, "orders/cart.html", context)
		
	else:
		cart_items = Cart_List.objects.filter(user_id=request.user, is_current=True)
		total_price = sum(item.calculated_price for item in cart_items)
		return render(request, "orders/cart.html", {"cart_items": cart_items, "total_price": total_price})

def removefromcart_view(request, cart_id):
	# view topping from cart

	item_toremove = Cart_List.objects.get(pk=cart_id)
	item_toremove.delete()
	messages.info(request,"El item ha sido removido de la Carta.")
	return HttpResponseRedirect(reverse("cart"))


def apertura_caja_view(request):
    most = AperturaCaja.objects.all()
    return render(request, "orders/apert.html", {"mostrar": most})


@login_required
def agregar_monto(request):
    monto = request.POST['monto']
    usuario = request.user
    fecha_ingreso = timezone.now()
    caja_num = request.POST['caja_num']

    curso = AperturaCaja.objects.create(usuario=usuario, monto=monto, fecha_ingreso=fecha_ingreso, caja_num=caja_num)
    messages.success(request, 'Apertura de caja con exito!') 
    return redirect("/")

def ventas_view(request):
    context = {
		"most" : Order.objects.all(),
        "mostr" : Cart_List.objects.all()
	}
    return render(request, "orders/ventas.html", context)  

@receiver(pre_save, sender=Order)
def asignar_numero_orden(sender, instance, **kwargs):
    if not instance.order_number:  # Si no se ha asignado un número de orden
        last_order = Order.objects.last()  # Obtener la última orden
        if last_order:
            instance.order_number = last_order.order_number + 1  # Asignar el siguiente número de orden
        else:
            instance.order_number = 1  # Si no hay órdenes anteriores, comenzar desde 1

#def ordenes_cart(request):
    #mostr = Cart_List.objects.all()
    #return render(request, "orders/ventas.html", {"mostr": mostr})

def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    order_items = order.cart_id.all()
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_detail.html', context)


def eliminarOrden(request, order_number):
	curso = Order.objects.get(pk=order_number)
	curso.delete()

	messages.success(request, 'Se elimino la orden!')
	return redirect("/")


def pagarOrden(request, order_number):
	pagar = Order.objects.get(order_number=order_number)
	pagar.complete = True
	pagar.save()

	messages.success(request, 'Orden Enviada')
	return redirect("/")

def mesas_view(request):
    context = {
		"orden" : Order.objects.all(),
        "lista" : Cart_List.objects.all()
	}
    return render(request, "orders/mesas.html", context)

def facturas_view(request):
    context = {
		"morder" : Order.objects.all(),
        "mcart" : Cart_List.objects.all()
	}
    return render(request, "orders/facturas.html", context)

def convert_to_pdf(request):
    # Carga el archivo html que deseas convertir
    template = 'orders/facturas.html'
    context = {'morder': request.user.order_set.all()}
    html_content = render_to_string(template, context)

    # Crea un HttpResponse con el tipo de contenido 'application/pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="output.pdf"'

    # Convierte el archivo html en un archivo pdf utilizando xhtml2pdf
    pisa_status = pisa.CreatePDF(
        html_content,
        dest=response,
        encoding='UTF-8'
    )

    # Si la conversión fue exitosa, devuelve el archivo pdf
    if pisa_status.err:
        return HttpResponse('Error al convertir el archivo html a pdf: ' + str(pisa_status.err))
    else:
        return response