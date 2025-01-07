from django.shortcuts import render,redirect , get_object_or_404
from brand.models import Brand
from category.models import Category
from .models import Product, ProductVariant ,ProductImages
from django.core.files.base import ContentFile
import base64
from django.contrib import messages
import uuid
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required
import re
import os
from django.db.models import Q



@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def product_list(request):
    products = Product.objects.filter(is_delete = False).order_by('id')
    
    return render(request, 'admin_side/product_list.html', {'products': products})




@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def add_product(request):
    form_data = {
        "name": "",
        "product_category": "",
        "product_brand": "",
        "price": "",
        "offer_price": "",
        "product_description": "",
        "thumbnail": None,
        "variants": [
            {"size": "", "stock": "", "is_active": True},
        ],
    }
    errors = {}
    allowed_extention = ['jpg', 'jpeg', 'png', 'webp','avif']

    if request.method == "POST":
        form_data["name"] = request.POST.get("name", "").strip()
        form_data["product_category"] = request.POST.get("product_category", "")
        form_data["product_brand"] = request.POST.get("product_brand", "")
        form_data["price"] = request.POST.get("price", "").strip()
        form_data["offer_price"] = request.POST.get("offer_price", "").strip()
        form_data["product_description"] = request.POST.get("product_description", "").strip()

        cropped_thumbnail_data = request.POST.get("cropped_thumbnail", "")
        if not cropped_thumbnail_data:
            errors["thumbnail"] = "please select a thumbnail"

        elif cropped_thumbnail_data:
            try:
                format, imgstr = cropped_thumbnail_data.split(";base64,")
                extention = format.split("/")[-1].lower()
                
                if extention not in allowed_extention:
                    errors["thumbnail"] = f"Invalid file type '{extention}'. Allowed types: {', '.join(allowed_extention)}."
                else:
                    thumbnail_file = ContentFile(base64.b64decode(imgstr), name=f"thumbnail.{extention}")
                    form_data["thumbnail"] = thumbnail_file
            except ValueError:
                errors["thumbnail"] = "Invalid cropped thumbnail data."


        variant_sizes = request.POST.getlist("variant_size[]")
        variant_stocks = request.POST.getlist("variant_stock[]")
        variant_is_active = request.POST.getlist("variant_is_active[]")

        form_data["variants"] = [
            {
                "size": size.strip(),
                "stock": stock.strip(),
                "is_active": is_active == "1",
            }
            for size, stock, is_active in zip(variant_sizes, variant_stocks, variant_is_active)
        ]
        
        if not form_data["name"]:
            errors["name"] = "Product name is required."
        else:
            if not re.match(r'^[a-zA-Z0-9\s]+$', form_data["name"]):
                errors["name"] = "Product name  not contain special characters."
            elif Product.objects.filter(name=form_data["name"]).exists():
                errors["name"] = "A product with this name already exists."


        if not form_data["product_category"]:
            errors["product_category"] = "Product category is required."
        if not form_data["product_brand"]:
            errors["product_brand"] = "Product brand is required."
        if not form_data["price"]:
            errors["price"] = "Product price is required."
        else:
            try:
                form_data["price"] = float(form_data["price"])
                if form_data["price"] <= 0:
                    errors["price"] = "Price must be greater than zero."
            except ValueError:
                errors["price"] = "Invalid price format."


        if form_data["offer_price"]:
            try:
                form_data["offer_price"] = float(form_data["offer_price"])
                if form_data["offer_price"] >= form_data["price"]:
                    errors["offer_price"] = "Offer price should be less than the original price."
            except ValueError:
                errors["offer_price"] = "Invalid offer price format."
    

        for variant in form_data["variants"]:
            size = variant.get("size") 

           
            if not size:
                errors["variant_size"] = "Size is required for variant"
                continue  

            try:
                size = int(size)
            except ValueError:
                errors["variant_size"] = "Size must be a number for variant."
                continue 

            
            if size < 5:
                errors["variant_size"] = "Size should be greater than or equal to 5 for variant "
            elif size > 11:
                errors["variant_size"] = "Size should not be greater than 11 for variant "



                    
            if not variant["stock"]:
                errors["variant_stock"] = "Stock is required for variant ."
                       
            else:
                try:
                    stock = int(variant["stock"])
                    if stock < 0:
                        errors["variant_stock"] = "Stock must be non-negative for variant "
                    elif stock>1000:
                        errors["variant_stock"] = "Stock must be less than 100"
                
                except ValueError:
                    errors["variant_stock"] = "Invalid stock value for variant "

        if errors:
            categories = Category.objects.filter(is_active=True)
            brands = Brand.objects.filter(is_active=True, is_deleted=False)
            return render(request, "admin_side/add_product.html", {
                "form_data": form_data,
                "errors": errors,
                "categories": categories,
                "brands": brands
            })

        
        product = Product.objects.create(
            name=form_data["name"],
            product_description=form_data["product_description"],
            product_category_id=form_data["product_category"],
            product_brand_id=form_data["product_brand"],
            price=form_data["price"],
            offer_price=form_data["offer_price"] if form_data["offer_price"] else None,
            thumbnail=form_data["thumbnail"],
            is_active=True,
        )

        
        for variant in form_data["variants"]:
            ProductVariant.objects.create(
                product=product,
                size=variant["size"],
                variant_stock=variant["stock"],
                variant_status=variant["is_active"],
            )

        return redirect("product:add_images_for_product", id=product.id)

    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True, is_deleted=False)
    return render(request, "admin_side/add_product.html", {
        "form_data": form_data,
        "errors": errors,
        "categories": categories,
        "brands": brands
    })



@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def add_images_for_product(request, id):
    errors = {}
    max_image = 4
    
    allowed_extensions = ['jpg', 'jpeg', 'png', 'webp','avif']

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        images = request.FILES.getlist("images")
        cropped_images = request.POST.getlist("cropped_images[]")

        cropped_images = [img for img in cropped_images if img.strip()]

        total_images = len(images) + len(cropped_images)
        if total_images < 3:
            errors["global"] = f'You must upload at least 3 images. Currently {total_images} images.'
        
        if total_images > max_image:
            errors["global"] = f'You can upload a maximum of {max_image} images.'

        for image in images:
            
            ext = os.path.splitext(image.name)[1].lower().replace('.', '')
            if ext not in allowed_extensions:
                errors["images"] = f'Invalid file type for {image.name}.'

        if not errors:
            try:
                for cropped_image in cropped_images:
                    try:
                        format, imgstr = cropped_image.split(";base64,")
                        ext = format.split("/")[-1]
                        
                        filename = f"cropped_{product.id}_{uuid.uuid4()}.{ext}"
                        
                        image_data = ContentFile(base64.b64decode(imgstr), name=filename)
                        ProductImages.objects.create(product=product, image=image_data)
                    except Exception as e:
                        errors["cropped_images"] = f'Error processing cropped image: {str(e)}'
                        break

                
                if not errors:
                    for image in images:
                        ProductImages.objects.create(product=product, image=image)

                    messages.success(request, 'Images uploaded successfully.')
                    return redirect("product:product_list")  

            except Exception as e:
                errors["global"] = 'An unexpected error occurred'

    return render(request, "admin_side/add_images_for_product.html", {
        "product": product,
        "errors": errors,
    })







@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def edit_product(request, id):
    form_data = {}

    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return redirect('product:add_product') 

    form_data["name"] = product.name
    form_data["product_category"] = product.product_category.id
    form_data["product_brand"] = product.product_brand.id
    form_data["price"] = product.price
    form_data["offer_price"] = product.offer_price if product.offer_price else ""
    form_data["product_description"] = product.product_description
    form_data["thumbnail"] = product.thumbnail

    # Get existing variants for this product
    form_data["variants"] = [
        {"size": variant.size, "stock": variant.variant_stock, "is_active": variant.variant_status}
        for variant in ProductVariant.objects.filter(product=product)
    ]

    if request.method == "POST":
        # Extract product data from POST
        form_data["name"] = request.POST.get("name", "").strip()
        form_data["product_category"] = request.POST.get("product_category", "")
        form_data["product_brand"] = request.POST.get("product_brand", "")
        form_data["price"] = request.POST.get("price", "").strip()
        form_data["offer_price"] = request.POST.get("offer_price", "").strip()
        form_data["product_description"] = request.POST.get("product_description", "").strip()

        cropped_thumbnail_data = request.POST.get("cropped_thumbnail", "")
        if cropped_thumbnail_data:
            try:
                format, imgstr = cropped_thumbnail_data.split(";base64,")
                ext = format.split("/")[-1]
                thumbnail_file = ContentFile(base64.b64decode(imgstr), name=f"thumbnail.{ext}")
                form_data["thumbnail"] = thumbnail_file
            except (ValueError, IndexError):
                messages.error(request, "Invalid cropped thumbnail data.")

        # Extract variant data from POST
        variant_sizes = request.POST.getlist("variant_size[]")
        variant_stocks = request.POST.getlist("variant_stock[]")
        variant_is_active = request.POST.getlist("variant_is_active[]")

        form_data["variants"] = [
            {
                "size": size.strip(),
                "stock": stock.strip(),
                "is_active": is_active == "1",
            }
            for size, stock, is_active in zip(variant_sizes, variant_stocks, variant_is_active)
        ]

       
        has_errors = False

        if not form_data["name"]:
            messages.error(request, "Product name is required.")
            has_errors = True

        if Product.objects.filter(name=form_data["name"]).exclude(id=product.id).exists():
            messages.error(request, "A product with this name already exists.")
            has_errors = True
        elif not re.match(r'^[a-zA-Z\s]+$', form_data["name"]):
            messages.error(request,"Product name should not contain special characters  and not numbers")
            has_errors = True
        

        if not form_data["product_category"]:
            messages.error(request, "Product category is required.")
            has_errors = True
        if not form_data["product_brand"]:
            messages.error(request, "Product brand is required.")
            has_errors = True
        if not form_data["price"]:
            messages.error(request, "Product price is required.")
            has_errors = True
        else:
            try:
                form_data["price"] = float(form_data["price"])
                if form_data["price"] <= 0:
                    messages.error(request, "Price must be greater than zero.")
                    has_errors = True
            except ValueError:
                messages.error(request, "Invalid price format.")
                has_errors = True


        if form_data["offer_price"]:
            try:
                form_data["offer_price"] = float(form_data["offer_price"])
                if form_data["offer_price"] >= form_data["price"]:
                    messages.error(request, "Offer price should be less than the original price.")
                    has_errors = True
            except ValueError:
                messages.error(request, "Invalid offer price format.")
                has_errors = True

        for i, variant in enumerate(form_data["variants"]):
            if not variant["size"]:
                messages.error(request, f"Size is required for variant {i+1}.")
                has_errors = True
            else:
                try:
                    size = int(variant["size"])
                    if size < 5:
                        messages.error(request, "Size must be at least 5 for variant.")
                        has_errors = True
                    elif size > 11:
                        messages.error(request,'Not allow greater that size 11')
                        has_errors = True
                except ValueError:
                    messages.error(request, "Size must be a number for variant ")
                    has_errors = True
            if not variant["stock"]:
                messages.error(request, f"Stock is required for variant {i+1}.")
                has_errors = True
            
            else:
                try:
                    stock = int(variant["stock"])
                    if stock < 0:
                        messages.error(request, f"Stock must be non-negative for variant {i+1}.")
                        has_errors = True
                    elif stock > 1000:
                        messages.error(request, f"Maximum stock is 1000 for variant {i+1}.")
                        has_errors = True
                except ValueError:
                    messages.error(request, f"Invalid stock value for variant {i+1}.")
                    has_errors = True

        if has_errors:
            categories = Category.objects.filter(is_active=True)
            brands = Brand.objects.filter(is_active=True, is_deleted=False)
            return render(request, "admin_side/edit_product.html", {
                "form_data": form_data,
                "categories": categories,
                "brands": brands,
                "product": product,
            })

        
        product.name = form_data["name"]
        product.product_description = form_data["product_description"]
        product.product_category_id = form_data["product_category"]
        product.product_brand_id = form_data["product_brand"]
        product.price = form_data["price"]
        product.offer_price = form_data["offer_price"] if form_data["offer_price"] else None
        product.thumbnail = form_data["thumbnail"]
        product.save()

        
        ProductVariant.objects.filter(product=product).delete()
        for variant in form_data["variants"]:
            ProductVariant.objects.create(
                product=product,
                size=variant["size"],
                variant_stock=variant["stock"],
                variant_status=variant["is_active"],
            )

        messages.success(request, "Product updated successfully.")
        return redirect("product:product_list")

    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True, is_deleted=False)
    return render(request, "admin_side/edit_product.html", {
        "form_data": form_data,
        "categories": categories,
        "brands": brands,
        "product": product,
    })




@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def product_shop(request):
    products = Product.objects.filter(is_delete=False)
    return render(request, 'user_side/shop.html',{'products':products})




#user side
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    
    available_variants = product.variants.filter(
        Q(variant_stock__gt=0) & Q(variant_status=True)
    )
    
    related_products = Product.objects.filter(product_category=product.product_category).exclude(id=product.id)
    
    return render(request, 'user_side/product-detail.html', {
        'product': product,
        'related_products': related_products,
        'available_variants': available_variants,  
    })



@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def admin_side_product_detail(request,id):
    product = get_object_or_404(Product,id=id)
    return render(request,"admin_side/admin_side_productdetail.html",{'product':product})



#for block or unblock the product
@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def product_status(request,id):
        product= get_object_or_404(Product, id=id)
        product.is_active = not product.is_active
        product.save()
        return redirect('product:product_list')

#soft delete
@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def product_soft_delete(request,id):
    product = get_object_or_404(Product ,id=id)
    product.is_delete= True
    product.save()
    return redirect('product:product_list')



@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def product_variant_list(request,id):
    product = get_object_or_404(Product, id=id, is_delete=False)
    variants = product.variants.all()  

    context = {
        'product': product,
        'variants': variants,
    }
    return render(request, 'admin_side/product_variant_list.html', context)




def edit_product_images(request, id):
    product = get_object_or_404(Product, id=id)
    images = product.images.all()

    if request.method == 'POST':
        
        if 'delete_image_id' in request.POST:
            image_id = request.POST.get('delete_image_id')
            image_to_delete = ProductImages.objects.filter(id=image_id, product=product).first()
            if image_to_delete:
                image_to_delete.delete()
                messages.success(request, "Image deleted successfully.")
            else:
                messages.error(request, "Image not found or already deleted.")
        
        if 'new_image' in request.FILES:
            new_image = request.FILES['new_image']
            ProductImages.objects.create(product=product, image=new_image)
            messages.success(request, "New image added successfully.")

        return redirect('product:edit_product_images', id=id)

    return render(request, 'admin_side/edit_product_images.html', {
        'product': product,
        'images': images,
    })




