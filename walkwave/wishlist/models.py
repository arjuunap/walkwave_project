from django.db import models
from account_app.models import User
from product.models import Product

# Create your models here.


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE ,related_name='wishlist')
    product = models.ForeignKey(Product , on_delete = models.CASCADE ,related_name= 'wishlist')
    added_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user', 'product') 

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
