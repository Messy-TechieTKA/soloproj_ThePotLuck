from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_reg_page),
    path('create_user', views.create_user),
    path('login',views.login),
    path('logout', views.logout),
    path('dashboard', views.dashboard_page),
    path('dishes/add', views.add_dish_page),
    path('dishes/create', views.create_dish),
    path('dishes/<int:dish_id>/edit', views.edit_dish_page),
    path('dishes/<int:dish_id>/update', views.update_dish),
    path('dishes/<int:dish_id>', views.view_dish_page),
    path('dishes/<int:dish_id>/delete', views.delete_dish),
    path('dishes/<int:dish_id>/add-to-user', views.add_dish_to_user),
    path('dishes/<int:dish_id>/remove-from-user', views.remove_dish_from_user),
    path('dishes/<int:dish_id>/done', views.done_dish)
]