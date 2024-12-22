from django.db import models

# Create your models here.


class Brand(models.Model):
    name= models.CharField(max_length=255,unique=True)
    description = models.TextField(blank=True,null=True)
    logo=models.ImageField(upload_to='brand_logos/',blank=True,null=True)
    created_on= models.DateTimeField(auto_now_add=True)
    is_deleted=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)


    def __str__(self):
        return self.name
    
