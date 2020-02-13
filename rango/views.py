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
from rango.forms import UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from datetime import datetime


def index(request):
    # Constructs a dictiobjectsonary to pass to the template engine as its context
    # Note the key boldmessage matches to {{boldmessage}} in the template!
    category_list = Category.objects.order_by("-likes")[:5]
    page_list = Page.objects.order_by("-views")[:5]

    context_dict = {"boldmessage": "Crunchy, creamy, cookie, candy, cupcake!",
                    "categories": category_list,
                    "pages": page_list,
                    }

    visitor_cookie_handler(request)
    # obtain our response object early so we can add cookie info
    response = render(request, "rango/index.html", context=context_dict)

    # return response back to the user updating any cookies that need changed
    return response


def about(request):
    context_dict = {"boldmessage": "Hey I'm not rango I'm about"}

    # this is to test the cookie
    visitor_cookie_handler(request)
    context_dict["visits"] = request.session["visits"]

    return render(request, "rango/about.html", context=context_dict)


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
    if request.user.is_authenticated:
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
    else:
        return redirect(reverse('rango:login'))


def add_page(request, category_name_slug):
    if request.user.is_authenticated:
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
    else:
        return redirect(reverse('rango:login'))


def register(request):
    # A boolean value for telling the template
    # whether the registration was successful
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False

    if request.method == "POST":
        # attempts to grab the information the raw form info
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # save the users data into the database
            user = user_form.save()

            # now we hash the password with the set_password method
            # once hashed we can update the user object
            user.set_password(user.password)
            user.save()

            # now sort out the user profile instance
            # since we need to set the user attribute ourselves
            # we set commit=False this delays saving the model
            # until we 're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            # did the user provide a profile pic
            # if so we need to get it form the input form and
            # put it the userProfile model
            if "picture" in request.FILES:
                profile.picture = request.FILES["picture"]

            # now we save the userProfile model instance
            profile.save()

            # update our variable to indicate that the template
            # registration was successful
            registered = True
        else:
            # Invalid from or forms - mistake or something else?
            # print problems to the terminal
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two MdoelForm instances
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # render the template depneding on the context
    return render(request, "rango/register.html", context={"user_form": user_form, "profile_form": profile_form,
                                                           "registered": registered})


def user_login(request):
    # if the requets is a http request try to pull out the relevant info
    if request.method == "POST":
        # gather the username and password provided by the user
        # returns None if the value does not exist.
        username = request.POST.get("username")
        password = request.POST.get("password")
        # uses Django's machinery to attempt to see if the username/password
        # combination is valid - a user object is returned if it is
        user = authenticate(username=username, password=password)

        # if we have a user object the details are correct.
        # if none pythons way of representing the absence of a value
        if user:
            # is the account active or has it been disabled
            if user.is_active:
                # if the account is valid and active we can log the user in
                # we'll send the uer back to the homepage.
                login(request, user)
                return redirect(reverse("rango:index"))
            else:
                # An inactive account was used - no logging in !
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details we're provided. so we cant log the user in
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied")
    # This scenario would most lilly be a HTTP get.
    else:
        # No context variables to pass to the template hence the
        # blank dict object
        return render(request, "rango/login.html")


@login_required
def restricted(request):
    return render(request, "rango/restricted.html")


@login_required
def user_logout(request):
    # since we know the user is logged in we can just log them out
    logout(request)
    # take the user back to the homepage
    return redirect(reverse("rango:index"))


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, "visits", "1"))

    last_visit_cookie = get_server_side_cookie(request, "last_visit", str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")

    # if its been more than a day since the last visit...
    if(datetime.now() - last_visit_time).days > 0:
        visits += 1
        # Update the last visit cookie now that we have updated the count _
        request.session["last_visit"] = str(datetime.now())
    else:
        # set the last visit cookie
        request.session["last_visit"] = last_visit_cookie

    # Update/set the visits cookie
    request.session["visits"] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

