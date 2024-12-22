from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required


# Create your views here.


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def category_list(request):
    categories = Category.objects.filter(is_deleted=False).order_by("id")
    return render(request, "admin_side/category_list.html", {"categories": categories})


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def add_category(request):
    errors = {}
    if request.method == "POST":
        name = request.POST.get("name").strip()
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "on"

        if not name:
            errors["name"] = "Name is required"
        if Category.objects.filter(name__iexact=name).exists():
            errors["name"] = "Already category is there"
        if not description:
            errors["description"] = "Description is required"

        if not errors:
            Category.objects.create(
                name=name, description=description, is_active=is_active
            )
            return redirect("category:category_list")
        context = {"name": name, "description": description, "errors": errors}
        return render(request, "admin_side/add_category.html", context)

    return render(request, "admin_side/add_category.html")


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    errors = {}
    if request.method == "POST":
        name = request.POST.get("name").strip()
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "on"

        if not name:
            errors["name"] = "Name is required"
        if Category.objects.filter(name__iexact=name).exclude(id=id).exists():
            errors["name"] = "Already category is there"

        if not errors:
            category.name = name
            category.description = description
            category.is_active = is_active
            category.save()
            return redirect("category:category_list")

    return render(
        request,
        "admin_side/edit_category.html",
        {"category": category, "errors": errors},
    )


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def block_category(request, id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=id)
        category.is_active = False
        category.save()
        return redirect("category:category_list")


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def unblock_category(request, id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=id)
        category.is_active = True
        category.save()
        return redirect("category:category_list")


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def category_soft_delete(request, id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=id)
        category.is_deleted = True
        category.save()
        return redirect("category:category_list")
