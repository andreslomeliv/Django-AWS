from django.shortcuts import render
from django.http import  HttpResponse

# Create your views here.
def home_view(request, *args,**kwargs):
	return render(request,"noticias.html")

def grafica_view(request,*args,**kwargs):
	return render(request,"graficas.html")

def priviet_view(request,*args,**kwargs):
	return HttpResponse("<h1>Prueba del sitio</h1>")


def contact_view(request,*args,**kwargs):
	print(request.user)
	return render(request,"contact.html",{})


def about_view(request,*args,**kwargs):
	print(request.user)
	return render(request,"about.html",{})	
