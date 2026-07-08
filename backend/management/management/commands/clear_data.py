from django.core.management.base import BaseCommand
from django.db import transaction
from management.models import Payment, Absence, Enrollment, Group, Grade

class Command(BaseCommand):
    help = 'Delete all rows from payments, absences, grades, enrollments, and groups'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting data deletion process...'))
        try:
            with transaction.atomic():
                # Delete dependent objects first to avoid ProtectedError
                payment_count, _ = Payment.objects.all().delete()
                absence_count, _ = Absence.objects.all().delete()
                grade_count, _ = Grade.objects.all().delete()
                enrollment_count, _ = Enrollment.objects.all().delete()
                group_count, _ = Group.objects.all().delete()

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully deleted data:\n'
                    f' - {payment_count} payments\n'
                    f' - {absence_count} absences\n'
                    f' - {grade_count} grades\n'
                    f' - {enrollment_count} enrollments\n'
                    f' - {group_count} groups'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {str(e)}'))
