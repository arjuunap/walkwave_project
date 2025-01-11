from django.db import models
from account_app.models import User

class Coupon(models.Model):
    name = models.CharField(max_length=100, unique=True) 
    discount = models.DecimalField(max_digits=5, decimal_places=2) 
    minimum_price = models.DecimalField(max_digits=10, decimal_places=2)  
    expiry_date = models.DateField() 
    count = models.PositiveIntegerField(default=1)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.discount}%"
    

class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)  # Tracks when the coupon was used

    def __str__(self):
        return f"{self.user.username} used {self.coupon.name}"