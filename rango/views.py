from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    # Constructs a dictionary to pass to the template engine as its context
    # Note the key boldmessage matches to {{boldmessage}} in the template!
    context_dict = {"boldmessage": "Chunky, creamy, cookie, candy, cupcake!"}

    # return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return render(request, "rango/index.html", context = context_dict)


def about(request):
    text = """ This is a about page <br>
     <a href="/rango/"> Click here to go back to main page </a>"""
    return HttpResponse(text)
