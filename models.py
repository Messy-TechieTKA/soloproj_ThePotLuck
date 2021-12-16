from django.db import models
from datetime import datetime, timedelta

import re

# Create your models here.
class UserManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}

        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        FIRST_NAME_REGEX = re.compile(r'^[a-zA-Z -]+$')
        LAST_NAME_REGEX = re.compile(r'^[a-zA-Z -]+$')

        if len(post_data['first_name']) < 2:
            errors['first_name'] = 'First name should have at least 2 characters.'
        elif not FIRST_NAME_REGEX.match(post_data['first_name']):
            errors['first_name'] = 'First name must consist of only letters'
        
        if len(post_data['last_name']) < 2:
            errors['last_name'] = 'Last name should have at least 2 characters.'
        elif not LAST_NAME_REGEX.match(post_data['last_name']):
            errors['last_name'] = 'Last name must consist of only letters and space or dash characters'
        
        if len(post_data['email']) < 1:
            errors['email'] = 'Email is required'
        elif not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = 'Please enter a valid email address'
        
        if len(post_data['password']) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        if post_data['password'] != post_data['pw_confirm']:
            errors['password'] = 'Passwords must match'

        return errors

class User(models.Model):
    first_name = models.CharField(max_length = 64)
    last_name = models.CharField(max_length = 64)
    email = models.CharField(max_length = 64)
    password = models.CharField(max_length = 64)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()

class CategoryManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}

        if len(post_data['category']) < 3:
            errors['category'] = 'Category must have at least 3 characters'

        return errors

class Category(models.Model):
    category = models.CharField(max_length = 255)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class DishManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}

        if len(post_data['title']) < 2:
            errors['title'] = 'The dish name must have at least 2 characters'
        
        if len(post_data['description']) < 3:
            errors['description'] = 'Description should have at least 3 characters.'

        return errors

class Dish(models.Model):
    title = models.CharField(max_length = 255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    created_by_user = models.ForeignKey(User, related_name = 'created_dishes', on_delete = models.CASCADE)
    added_users = models.ManyToManyField(User, related_name = 'added_dishes')

    categories = models.ManyToManyField(Category, related_name = 'dishes')

    objects = DishManager()
