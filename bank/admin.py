from django.contrib import admin

# Register your models here.
from bank.models import Account, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'credit')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'destination', 'amount', 'tid')
