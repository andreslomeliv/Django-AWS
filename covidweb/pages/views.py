from django.shortcuts import render
from django.http import  HttpResponse
# Create your views here.
def home_view(request, *args,**kwargs):
	print(request.user)
	return render(request,"grafica_pib.html",{})

def grafica_view(request,*args,**kwargs):
	return render(request,"grafica_pib.html")

def priviet_view(request,*args,**kwargs):
	print(request.user,"is being a kuk")
	return HttpResponse("<h1>priviet ma nigga welcome \n to the bonezone fuk</h1>")


def contact_view(request,*args,**kwargs):
	print(request.user)
	return render(request,"contact.html",{})


def about_view(request,*args,**kwargs):
	print(request.user)
	return render(request,"about.html",{})	