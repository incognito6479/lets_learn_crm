from django.core.management.base import BaseCommand
from management.tasks import check_student_debts

class Command(BaseCommand):
    help = 'Manually check and update student debt statuses'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting manual check of student debts...'))
        updated_count = check_student_debts()
        self.stdout.write(self.style.SUCCESS(f'Successfully checked and updated student debts. Updated count: {updated_count}'))
