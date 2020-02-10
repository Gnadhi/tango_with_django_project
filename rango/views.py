from django.shortcuts import render

from django.http import HttpResponse

# Import the Category Model
from rango.models import Category

from rango.models import Page

# For the forms
from rango.forms import CategoryForm
from rango.forms import PageForm
from django.shortcuts import redirect
from django.urls import reverse


def index(request):
    # Constructs a dictiobjectsonary to pass to the template engine as its context
    # Note the key boldmessage matches to {{boldmessage}} in the template!
    category_list = Category.objects.order_by("-likes")[:5]
    page_list = Page.objects.order_by("-views")[:5]

    context_dict = {"boldmessage": "Crunchy, creamy, cookie, candy, cupcake!",
                    "categories": category_list,
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


def add_category(request):
    form = CategoryForm()

    # A HTTP post ?
    if request.method == "POST":
        form = CategoryForm(request.POST)

        # have we been provided with a valid form ?
        if form.is_valid():
            # save new category in database.
            form.save(commit=True)
            # Now that the category is saved we confirm this.
            # for now just redirect the user back to the index view.
            return redirect("/rango/")
        else:
            # The supplied form contains errors
            print(form.errors)

    # Will handle the bad form, new form, or no form supplied case
    # render the form with error message (if any)
    return render(request, "rango/add_category.html", {"form": form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # You can not add a page to a Category that does not exist....
    if category is None:
        return redirect("/rango/")

    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse("rango:show_category", kwargs={"category_name_slug": category_name_slug}))

        else:
            print(form.errors)

    context_dict = {"forms": form, "category": category}
    return render(request, "rango/add_page.html", context=context_dict)
