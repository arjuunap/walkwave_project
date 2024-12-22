from django.db import models
from category.models import Category
from brand.models import Brand

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=50,unique=True)
    product_description = models.TextField()
    product_category = models.ForeignKey(Category, on_delete=models.SET_NULL ,null= True)
    product_brand =models.ForeignKey(Brand , on_delete= models.SET_NULL,null=True)
    price = models.DecimalField(max_digits= 8,decimal_places=2)
    offer_price = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    thumbnail = models.ImageField(upload_to='thumbnail_images',null=True,blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    def percentage_discount(self):
        if self.offer_price and self.offer_price<self.price:
            return int(((self.price- self.offer_price)/ self.price) * 100)
        return 0
    
    def __str__(self):
        return self.name
    


class ProductVariant(models.Model):
    product = models.ForeignKey( Product , on_delete=models.CASCADE ,related_name='variants')
    size = models.CharField(max_length=8, null= True, blank=True)
    variant_stock = models.PositiveIntegerField(default=0)
    variant_status = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.product.name} -Size :{self.size}"
    

class ProductImages(models.Model):
    product = models.ForeignKey(Product ,on_delete=models.CASCADE ,related_name='images')
    image = models.ImageField(upload_to='product_images',blank=True,null= True)

    def __str__(self):
        return f"Image for {self.product.name}"
