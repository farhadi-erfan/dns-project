from django.contrib import admin

# Register your models here.
from blockchain.models import Delegation, Exchange


@admin.register(Delegation)
class DelegationAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'time')


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount')
