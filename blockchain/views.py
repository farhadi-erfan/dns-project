# Create your views here.
import json
from datetime import datetime

from django.db.transaction import atomic
from django.http import JsonResponse

from blockchain.models import Delegation, Exchange


def delegate(request):
    body = json.loads(request.body)
    user = body['pkm']
    delegated_to = body['pkd']
    policy = body['policy']
    # TODO: verify user & bank
    if Delegation.objects.last().nonce == body['nonce']:
        return JsonResponse({
            'status': 'duplicate'
        }, status=400)
    Delegation.objects.create(user=user, delegated_to=delegated_to, amount=policy['amount'],
                              current_value=policy['amount'], count=policy['count'],
                              time=policy['time'], nonce=body['nonce'])
    return JsonResponse({
        'status': 'ok',
        'nonce': body['nonce']
    })


@atomic
def exchange(request):
    body = json.loads(request.body)
    sender = body['sender']
    receiver = body['receiver']
    value = body['value']
    # TODO: verify user & bank
    if Exchange.objects.last().nonce == body['nonce']:
        return JsonResponse({
            'status': 'duplicate'
        }, status=400)
    delegation = Delegation.objects.filter(delegated_to=sender, current_value__gte=value, count__gt=0,
                                           time__lte=datetime.now()).first()
    if not delegation:
        return JsonResponse({
            'status': 'no-delegation'
        }, status=404)
    Exchange.objects.create(sender=sender, receiver=receiver, amount=value, delegation=delegation, nonce=body['nonce'])
    delegation.amount -= value
    delegation.count -= 1
    delegation.save()
    return JsonResponse({
        'status': 'ok',
        'nonce': body['nonce']
    })
