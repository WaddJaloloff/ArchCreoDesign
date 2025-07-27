from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.



class Kategoriyalar(models.Model):
    Nomi = models.CharField(max_length=50, unique=True)
    rasmni = models.ImageField(upload_to='kategoriyalar/')
    def __str__(self):
        return self.Nomi

    

class Loyihalar(models.Model):
    Nomi = models.CharField(max_length=100)
    Tavsifi = models.TextField()
    Kategoriyasi = models.ForeignKey(Kategoriyalar, on_delete=models.SET_NULL, null=True)
    Rasm_1 = models.ImageField(upload_to='rasmlar/')
    Rasm_2 = models.ImageField(upload_to='rasmlar/', blank=True, null=True)
    Rasm_3 = models.ImageField(upload_to='rasmlar/', blank=True, null=True)
    Rasm_4 = models.ImageField(upload_to='rasmlar/', blank=True, null=True)
    Rasm_5 = models.ImageField(upload_to='rasmlar/', blank=True, null=True)
    Rasm_6 = models.ImageField(upload_to='rasmlar/', blank=True, null=True)
    Active = models.BooleanField(default=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Nomi

    class Meta:
        # Har bir kategoriya ichida Nomi unikal bo‘lishi shart
        unique_together = ('Nomi', 'Kategoriyasi')
        
    def clean(self):
        if Loyihalar.objects.exclude(pk=self.pk).filter(Nomi=self.Nomi, Kategoriyasi=self.Kategoriyasi).exists():
            raise ValidationError("Bu nomdagi loyiha ushbu kategoriyada allaqachon mavjud. Boshqa nomdan foydalaning!")

    def __str__(self):
        return self.Nomi

class telegram_user(models.Model):
    user_id = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} ({self.username})"