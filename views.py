from django.shortcuts import render, redirect
from django.contrib import messages

import bcrypt


from .models import User, Category, Dish

def login_reg_page(request):
    return render(request, 'login_reg.html')

def create_user(request):
    potential_users = User.objects.filter(email = request.POST['email'])

    if len(potential_users) != 0:
        messages.error(request, "User with that email already exists!")
        return redirect('/')

    errors = User.objects.basic_validator(request.POST)

    if len(errors) > 0:
        for key, val in errors.items():
            messages.error(request, val)
        return redirect('/')

    hashed_pw = bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt()).decode()

    new_user = User.objects.create(
        first_name = request.POST['first_name'],
        last_name = request.POST['last_name'],
        email = request.POST['email'],
        password = hashed_pw,
    )

    request.session['user_id'] = new_user.id

    return redirect('/dashboard')

def login(request):
    potential_users = User.objects.filter(email = request.POST['email'])

    if len(potential_users) == 0:
        messages.error(request, "Please check your email and password.")
        return redirect('/')

    user = potential_users[0]

    if not bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
        messages.error(request, "Please check your email and password.")
        return redirect('/')

    request.session['user_id'] = user.id

    return redirect('/dashboard')

def logout(request):
    if 'user_id' not in request.session:
        messages.error(request, "You are not logged in!")
        return redirect('/')

    request.session.clear()

    return redirect('/')

def dashboard_page(request):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')
        
    current_user = User.objects.get(id=request.session['user_id'])
    current_user_added_dishes = current_user.added_dishes.all()
    all_dishes = Dish.objects.exclude(id__in=current_user_added_dishes)

    context = {
        'current_user': current_user,
        'all_dishes': all_dishes,
        'users_added_dishes': current_user_added_dishes,
    }

    return render(request, 'dashboard.html', context)

def add_dish_page(request):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')
        
    current_user = User.objects.get(id=request.session['user_id'])
    category_options = Category.objects.all().order_by('-created_at')

    context = {
        'current_user': current_user,
        'category_options': category_options
    }

    return render(request, 'add_dish.html', context)

def create_dish(request):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])

    dish_errors = Dish.objects.basic_validator(request.POST)

    if len(Category.objects.filter(category = request.POST['category_text'])) != 0:
        messages.error(request, "The category you typed already exists. Please use that.")
        return redirect('/dishes/add')

    if len(dish_errors) > 0:
        for key, val in dish_errors.items():
            messages.error(request, val)
        return redirect('/dishes/add')

    new_dish = Dish.objects.create(
        title = request.POST['title'],
        description = request.POST['description'],
        created_by_user = current_user,
    )

    if request.POST['category_text'] != "":
        new_category = Category.objects.create(category = request.POST['category_text'])
        new_dish.categories.add(new_category)

    if request.POST.getlist('category') != []:
        for category_id in request.POST.getlist('category'):
            category = Category.objects.get(id = category_id)
            category.dishes.add(new_dish)

    return redirect('/dashboard')

def edit_dish_page(request, dish_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_dish = Dish.objects.get(id = dish_id)
    all_categories = Category.objects.all()

    if current_dish.created_by_user != current_user:
        messages.error(request, "This is not your dish silly goose. So you can't edit it")
        return redirect('/dashboard')

    context = {
        "current_user": current_user,
        "current_dish": current_dish,
        "all_categories": all_categories,
    }

    return render(request, 'edit_dish.html', context)

def update_dish(request, dish_id):
    if 'user_id' not in request.session:
        messages.error(request, "Log in Please!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_dish = Dish.objects.get(id = dish_id)

    if len(Category.objects.filter(category = request.POST['category_text'])) != 0:
        messages.error(request, "You already have this catergory, you don't need it again.")
        return redirect(f'/dishes/{dish_id}/edit')

    if current_dish.created_by_user != current_user:
        messages.error(request, "This dish doesn't belong to you, Honey. You can't edit it!")
        return redirect('/dashboard')

    dish_errors = Dish.objects.basic_validator(request.POST)

    if len(dish_errors) > 0:
        for key, val in dish_errors.items():
            messages.error(request, val)
        return redirect(f'/dishes/{dish_id}/edit')

    for category in Category.objects.exclude(id__in = request.POST.getlist('category')):
        current_dish.categories.remove(category)

    if request.POST['category_text'] != "":
        new_category = Category.objects.create(category = request.POST['category_text'])
        current_dish.categories.add(new_category)

    for category_id in request.POST.getlist('category'):
        category = Category.objects.get(id = category_id)
        category.dishes.add(current_dish)

    

    current_dish.title = request.POST['title']
    current_dish.description = request.POST['description']
    current_dish.save()

    return redirect('/dashboard')

def view_dish_page(request, dish_id):
    if 'user_id' not in request.session:
        messages.error(request, "You have to be logged in")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_dish = Dish.objects.get(id = dish_id)
    all_categories = Category.objects.all().order_by('category')

    current_user_added_dishes = current_user.added_dishes.all()
    all_dishes = Dish.objects.exclude(id__in=current_user_added_dishes)

    category_empty = True

    if len(current_dish.categories.all()) != 0:
        category_empty = False

    context = {
        'current_user': current_user,
        'all_dishes': all_dishes,
        'current_user_added_dishes': current_user_added_dishes,
        'current_dish': current_dish,
        'all_categories': all_categories,
        'category_empty': category_empty
    }

    return render(request, 'view_dish.html', context)

def delete_dish(request, dish_id):
    if 'user_id' not in request.session:
        messages.error(request, "Please, login.")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_dish = Dish.objects.get(id = dish_id)

    if current_dish.created_by_user != current_user:
        messages.error(request, "You can't remove it because this is not your dish")
        return redirect('/dashboard')

    current_dish.delete()

    return redirect('/dashboard')

def add_dish_to_user(request, dish_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_dish = Dish.objects.get(id = dish_id)

    current_user.added_dishes.add(current_dish)

    return redirect('/dashboard')

def remove_dish_from_user(request, dish_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_dish = Dish.objects.get(id = dish_id)

    current_user.added_dishes.remove(current_dish)

    return redirect('/dashboard')

def done_dish(request, dish_id):
    if 'user_id' not in request.session:
        messages.error(request, "You have to be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_dish = Dish.objects.get(id = dish_id)

    if current_user not in current_dish.added_users.all():
        messages.error(request, "You can not add this dish, it belongs to someone else.")
        return redirect('/dashboard')

    current_dish.delete()

    return redirect('/dashboard')