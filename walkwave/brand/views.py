from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Brand
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required


# List all brands
@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def brand_list(request):
    brands = Brand.objects.filter(is_deleted=False).order_by("id")
    return render(request, "admin_side/brand_list.html", {"brands": brands})


# Add brand
@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def add_brand(request):
    errors = {}
    if request.method == "POST":
        name = request.POST.get("name").strip()
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "on"
        logo = request.FILES.get("logo")

        if not name:
            errors["name"] = "Name is required"

        if Brand.objects.filter(name__iexact=name).exists():
            errors["name"] = "Name is already taken"

        if logo:
            valid_extentions = ["jpg", "jpeg", "png", "webp"]
            if not logo.name.split(".")[-1].lower() in valid_extentions:
                errors["logo"] = "Invalid logo ,only image format is allowed"

        if not errors:
            Brand.objects.create(name=name, description=description, logo=logo)
            messages.success(request, "Brand added successfully")
            return redirect("brand:brand_list")

        context = {"name": name, "description": description, "errors": errors}

        return render(request, "admin_side/add_brand.html", context)

    return render(request, "admin_side/add_brand.html")


# Block a brand
@require_POST
@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def block_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    brand.is_active = False
    brand.save()
    return redirect("brand:brand_list")


# Unblock a brand
@require_POST
@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def unblock_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    brand.is_active = True
    brand.save()
    return redirect("brand:brand_list")


# Soft delete a brand
@require_POST
@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def soft_delete_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    brand.is_deleted = True
    brand.save()
    return redirect("brand:brand_list")


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def edit_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    errors = {}
    if request.method == "POST":
        name = request.POST.get("name").strip()
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "on"
        logo = request.FILES.get("logo")

        if not name:
            errors["name"] = "Name is required"
        if Brand.objects.filter(name__iexact=name).exclude(id=id).exists():
            errors["name"] = "A brand with this name already exists"

        if not errors:
            brand.name = name
            brand.description = description
            brand.is_active = is_active
            if logo:
                brand.logo = logo
            brand.save()
            return redirect("brand:brand_list")

    return render(
        request, "admin_side/edit_brand.html", {"brand": brand, "errors": errors}
    )
