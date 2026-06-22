from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from management.models import Enrollment, Payment

class Command(BaseCommand):
    help = "Checks student balances and sets status to debt if total paid is less than elapsed billing cycles"

    def handle(self, *args, **options):
        self.stdout.write("Running debt check on student enrollments...")
        
        # Only process active enrollments that are currently 'enrolled'
        enrollments = Enrollment.objects.filter(is_active=True, status='enrolled')
        updated_count = 0

        for enrollment in enrollments:
            changed, expected_amount, total_paid, months_billed = enrollment.check_debt()
            if changed:
                updated_count += 1
                status_label = enrollment.payment_status.upper()
                msg = f"Student {enrollment.student.full_name} in group '{enrollment.group.name}' marked as {status_label}. Expected: {expected_amount} UZS, Paid: {total_paid} UZS (Months billed: {months_billed})"
                if enrollment.payment_status == 'debt':
                    self.stdout.write(self.style.WARNING(msg))
                else:
                    self.stdout.write(self.style.SUCCESS(msg))
                    
        self.stdout.write(f"Balance check complete. Updated {updated_count} enrollment(s).")
