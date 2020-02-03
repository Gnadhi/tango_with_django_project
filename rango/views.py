from django.shortcuts import render

from django.http import HttpResponse

# Import the Category Model
from rango.models import Category

from rango.models import Page


def index(request):
    # Constructs a dictionary to pass to the template engine as its context
    # Note the key boldmessage matches to {{boldmessage}} in the template!
    catergory_list = Category.objects.order_by("-likes")[:5]
    page_list = Page.objects.order_by("-views")[:5]

    context_dict = {"boldmessage": "Crunchy, creamy, cookie, candy, cupcake!",
                    "categories": catergory_list,
                    "pages": page_list}

    # return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return render(request, "rango/index.html", context=context_dict)


def about(request):
    conetxt_dict = {"boldmessage": "Hey I'm not rango I'm about"}

    return render(request, "rango/about.html", context=conetxt_dict)


def show_category(request, category_name_slug):
    # create a context dict which we can pass to the template rendering engine
    context_dict = {}

    try:
        # checks to see if category name slug exists with this given name
        # .get() method return one model instance or raisers an exception
        category = Category.objects.get(slug=category_name_slug)

        # retrieves all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)

        # adds our result list to the template context under name pages.
        context_dict["pages"] = pages
        # we also add the category object from the database to the context dict
        # We'll use this in the template to verify that the category exists.
        context_dict["category"] = category
    except Category.DoesNotExist:
        # we get here if we didnt find any specified category
        # dont do anything - the template will display the "no category message for us"
        context_dict["category"] = None
        context_dict["pages"] = None

    # go render the response and return it to the client
    return render(request, "rango/category.html", context=context_dict)
