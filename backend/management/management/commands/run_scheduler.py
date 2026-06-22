import time
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Runs the debt checker scheduler daily at midnight"

    def handle(self, *args, **options):
        self.stdout.write("Scheduler started. Running initial debt check...")
        
        while True:
            try:
                call_command("check_debts")
            except Exception as e:
                self.stderr.write(f"Error executing check_debts command: {e}")
            
            # Calculate sleep seconds until next midnight
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            next_run = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
            sleep_seconds = (next_run - now).total_seconds()
            
            self.stdout.write(f"Next debt check scheduled at {next_run}. Sleeping for {sleep_seconds:.1f} seconds...")
            time.sleep(sleep_seconds)
