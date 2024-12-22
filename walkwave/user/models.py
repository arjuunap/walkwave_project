from django.db import models
from account_app.models import User

# Create your models here.


class Address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, default='home')
    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    default_address = models.BooleanField(default=False) 


    def save(self, *args, **kwargs):
        if self.default_address:
            Address.objects.filter(user=self.user, default_address=True).exclude(pk=self.pk).update(default_address=False)
        super(Address, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.label} - {self.user.username}"