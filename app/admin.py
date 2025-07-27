from django.contrib import admin
from .models import Loyihalar, Kategoriyalar, telegram_user



class LoyihalarAdmin(admin.ModelAdmin):
    list_display = ('Nomi', 'Kategoriyasi', 'Active', 'CreatedAt', 'UpdatedAt')
    search_fields = ('Nomi', 'Kategoriyasi')
    list_filter = ('Active', 'Kategoriyasi')

class telegram_userAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'first_name', 'telefon')
    search_fields = ('user_id', 'username', 'first_name')
    list_filter = ('first_name',)


admin.site.register(telegram_user, telegram_userAdmin)
admin.site.register(Loyihalar, LoyihalarAdmin)
admin.site.register(Kategoriyalar)