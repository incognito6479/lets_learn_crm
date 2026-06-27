import logging
from management.models import Enrollment

logger = logging.getLogger(__name__)

from celery import shared_task

@shared_task
def check_student_debts():
    """
    Checks student balances and sets status to 'debt' or 'paid'
    based on elapsed billing cycles and payments.
    This function is compatible with Celery + Beat tasks.
    """
    logger.info("Running debt check on student enrollments...")
    
    # Only process active enrollments that are currently 'enrolled'
    enrollments = Enrollment.objects.filter(is_active=True, status='enrolled')
    updated_count = 0

    for enrollment in enrollments:
        try:
            changed, expected_amount, total_paid, months_billed = enrollment.check_debt()
            if changed:
                updated_count += 1
                status_label = enrollment.payment_status.upper()
                logger.info(
                    f"Student {enrollment.student.full_name} in group '{enrollment.group.name}' "
                    f"marked as {status_label}. Expected: {expected_amount} UZS, Paid: {total_paid} UZS "
                    f"(Months billed: {months_billed})"
                )
        except Exception as e:
            logger.error(f"Error checking debt for enrollment {enrollment.id}: {e}")

    logger.info(f"Balance check complete. Updated {updated_count} enrollment(s).")
    return updated_count
