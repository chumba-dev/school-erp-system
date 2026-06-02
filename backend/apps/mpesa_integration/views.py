import json
import logging
from decimal import Decimal

from django.conf import settings
from django.db import transaction as db_transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_daraja.mpesa.core import MpesaClient   # <-- Correct import

from apps.core.models import Staff
from apps.finance.models import FeeInvoice, Payment, StudentCredit
from .models import MpesaTransaction

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as drf_status
from django.core.exceptions import PermissionDenied

from apps.accounts.permissions import IsBursar, IsAdmin
from apps.finance.utils import send_receipt_email_async




logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stk_push(request):
    """
    Initiate STK Push payment for an invoice.
    - Bursar/Admin: can pay any invoice (provide phone number)
    - Parent: can only pay invoices belonging to their linked student.
    """
    try:
        # Get user and check role
        user = request.user
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        invoice_id = data.get('invoice_id')

        if not phone_number or not amount or not invoice_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Validate invoice
        invoice = get_object_or_404(FeeInvoice, id=invoice_id)

        # --- Permission logic ---
        if user.role == 'bursar' or user.role == 'admin':
            # Bursar/Admin can pay any invoice
            pass
        elif user.role == 'parent':
            # Parent must have a linked student profile and that student must match the invoice's student
            if not user.student_profile:
                return JsonResponse({'error': 'Parent account not linked to any student'}, status=403)
            if invoice.student != user.student_profile:
                return JsonResponse({'error': 'You can only pay invoices for your own child'}, status=403)
        else:
            # Teachers, principals, or other roles are not allowed
            return JsonResponse({'error': 'You are not authorized to initiate payments'}, status=403)

        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]

        # Convert amount to integer (M-Pesa requirement)
        amount_int = int(float(amount))

        if invoice.status == 'paid':
            return JsonResponse({'error': 'Invoice already paid'}, status=400)

        student = invoice.student
        # If phone number not provided, try to use parent's default phone (for parent-initiated)
        if not phone_number and user.role == 'parent' and user.student_profile:
            phone_number = student.parent_phone
        if not phone_number:
            return JsonResponse({'error': 'Phone number required'}, status=400)

        target_phone = phone_number

        client = MpesaClient()
        response = client.stk_push(
            phone_number=target_phone,
            amount=amount_int,
            account_reference=f"INV{invoice.invoice_number}",
            transaction_desc=f"Payment for {invoice.invoice_number}",
            callback_url=settings.MPESA_CALLBACK_URL,
        )

        if response.response_code == '0':
            MpesaTransaction.objects.create(
                merchant_request_id=response.merchant_request_id,
                checkout_request_id=response.checkout_request_id,
                phone_number=target_phone,
                amount=Decimal(amount_int),
                invoice=invoice,
                status='pending'
            )
            return JsonResponse({
                'success': True,
                'checkout_request_id': response.checkout_request_id,
                'merchant_request_id': response.merchant_request_id
            })
        else:
            error_msg = getattr(response, 'response_description', 'STK push failed')
            logger.error(f"STK Push failed: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

    except Exception as e:
        logger.exception("STK Push error")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def mpesa_callback(request):
    """
    Callback endpoint called by Safaricom after STK Push completion.
    """
    try:
        data = json.loads(request.body)
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        merchant_request_id = stk_callback.get('MerchantRequestID')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')

        mpesa_trans = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)

        if mpesa_trans.status != 'pending':
            logger.info(f"Transaction {checkout_request_id} already processed. Status: {mpesa_trans.status}")
            return JsonResponse({'status': 'already_processed'})

        mpesa_trans.result_code = result_code
        mpesa_trans.result_desc = result_desc
        mpesa_trans.status = 'completed' if result_code == '0' else 'failed'
        mpesa_trans.save()

        if result_code == '0':
            with db_transaction.atomic():
                invoice = mpesa_trans.invoice
                amount_paid = mpesa_trans.amount

                # Create or get system staff for M-Pesa callback
                system_staff, _ = Staff.objects.get_or_create(
                    tsc_number='MPESA_SYSTEM',
                    defaults={
                        'first_name': 'Mpesa',
                        'last_name': 'System',
                        'tenure_type': 'Permanent',
                        'phone': '0000000000',
                    }
                )

                payment = Payment.objects.create(
                    transaction_reference=f"MPESA-{checkout_request_id}",
                    student=invoice.student,
                    invoice=invoice,
                    amount=amount_paid,
                    payment_method='mpesa',
                    payment_channel='stk',
                    status='completed',
                    recorded_by=system_staff,
                    notes=f"Auto from M-Pesa callback. Result: {result_desc}",
                )
                mpesa_trans.payment = payment
                mpesa_trans.save()
                

                # Update invoice paid amount and status
                invoice.paid_amount += amount_paid
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = 'paid'
                else:
                    invoice.status = 'partially_paid'
                invoice.save(update_fields=['paid_amount', 'status'])
                # Send receipt email asynchronously
                send_receipt_email_async(payment)

                # Handle overpayment (credit creation)
                old_balance = invoice.total_amount - (invoice.paid_amount - amount_paid)
                if amount_paid > old_balance:
                    excess = amount_paid - old_balance
                    StudentCredit.objects.create(
                        student=invoice.student,
                        amount=excess,
                        created_by=system_staff,
                        notes=f"Overpayment from M-Pesa transaction {checkout_request_id}",
                    )

        return JsonResponse({'status': 'success'})
    except MpesaTransaction.DoesNotExist:
        logger.error(f"Transaction not found for checkout_request_id: {checkout_request_id}")
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        logger.exception("Error processing M-Pesa callback")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def check_payment_status(request):
    checkout_request_id = request.GET.get('checkout_request_id')
    if not checkout_request_id:
        return JsonResponse({'error': 'Missing checkout_request_id'}, status=400)

    try:
        mpesa_trans = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
        response_data = {
            'status': mpesa_trans.status,
            'result_code': mpesa_trans.result_code,
            'result_desc': mpesa_trans.result_desc,
        }
        if mpesa_trans.payment:
            response_data['payment_id'] = str(mpesa_trans.payment.id)
            response_data['invoice_id'] = str(mpesa_trans.invoice.id)
        return JsonResponse(response_data)
    except MpesaTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)