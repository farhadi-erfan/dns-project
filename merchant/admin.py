from django.contrib import admin

# Register your models here.
from merchant.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'amount', 'status')
