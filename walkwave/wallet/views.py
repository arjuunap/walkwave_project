from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction

@login_required
def view_wallet(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)  # Unpack the tuple
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')  # Use the wallet instance

    return render(request, 'user_side/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
    })
