from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def view_wallet(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions_list = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')

    per_page = 5
    paginator = Paginator(transactions_list, per_page)
    
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(request, 'user_side/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
    })
