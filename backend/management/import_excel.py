import re
import datetime
import openpyxl
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from management.models import User, Student, Group, Enrollment, Payment, Absence
from management.helpers import is_yellow_color, is_green_color, clean_phone_number, parse_enrollment_date

def run_import_excel(excel_file, month_param=None, year_param=None, price_param=None):
    if not excel_file:
        raise ValidationError("No file was uploaded.")

    # Resolve teacher name from filename
    filename = excel_file.name
    name_part = filename.rsplit('.', 1)[0]
    teacher_name = name_part.strip().replace('_', ' ').replace('-', ' ')
    
    # Get or create teacher
    username_clean = re.sub(r'[^a-zA-Z0-9_.-]', '', name_part.strip())
    if not username_clean:
        username_clean = f"teacher_{int(timezone.now().timestamp())}"
    
    username_clean = username_clean.lower()
    
    with transaction.atomic():
        teacher, created = User.objects.get_or_create(
            username=username_clean,
            defaults={
                'first_name': teacher_name,
                'role': 'teacher',
                'is_active': True
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()

        # Load workbook using openpyxl
        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
        except Exception as e:
            raise ValidationError(f"Error opening Excel file: {str(e)}")

        imported_groups = []
        total_students_imported = 0
        total_payments_imported = 0
        total_absences_imported = 0

        try:
            current_month = int(month_param or timezone.localdate().month)
        except (ValueError, TypeError):
            current_month = timezone.localdate().month

        try:
            current_year = int(year_param or timezone.localdate().year)
        except (ValueError, TypeError):
            current_year = timezone.localdate().year

        try:
            group_price = Decimal(str(price_param or '450000.00').replace(' ', '').replace(',', ''))
        except (ValueError, TypeError, Decimal.InvalidOperation):
            group_price = Decimal('450000.00')

        for sheet in wb.worksheets:
            sheet_name = sheet.title
            name_clean = sheet_name.replace(';', ':').replace(' ', '').lower()
            
            # Extract start time
            starts_at = "09:00:00"
            colon_match = re.search(r'(\d+)[:;](\d+)', sheet_name)
            if colon_match:
                hour = int(colon_match.group(1))
                minute = int(colon_match.group(2))
                starts_at = f"{hour:02d}:{minute:02d}:00"
            else:
                time_match = re.search(r'\d+', name_clean)
                if time_match:
                    num_str = time_match.group()
                    if len(num_str) == 3:
                        starts_at = f"0{num_str[0]}:{num_str[1:]}:00"
                    elif len(num_str) == 4:
                        starts_at = f"{num_str[:2]}:{num_str[2:]}:00"
                    elif len(num_str) in [1, 2]:
                        hour = int(num_str)
                        starts_at = f"{hour:02d}:00:00"

            # Extract days
            days = 'Mon-Wed-Fri'
            if any(d in name_clean for d in ['tue', 'thu', 'sat']):
                days = 'Tue-Thur-Sat'

            # Create group name
            group_name = f"{teacher_name} - {sheet_name}"
            
            # Create Group
            group = Group.objects.create(
                name=group_name,
                teacher=teacher,
                starts_at=starts_at,
                duration=90, # 1.5 h = 90 mins
                group_days_at=days,
                price=group_price,
                started_at=datetime.date(current_year, current_month, 1),
                status='ongoing'
            )
            imported_groups.append(group_name)

            # Loop through student rows starting from row 3
            for r_idx in range(3, sheet.max_row + 1):
                name_cell = sheet.cell(row=r_idx, column=2)
                name_val = name_cell.value
                if not name_val or str(name_val).strip() == "" or str(name_val).strip().upper() == "ОБЩИЙ ИТОГ":
                    break
                
                student_name = str(name_val).strip()
                
                enroll_date_val = sheet.cell(row=r_idx, column=3).value
                enrollment_date = parse_enrollment_date(enroll_date_val, current_year, current_month)
                
                # Check for yellow background color on student cell
                name_color = None
                if name_cell.fill and name_cell.fill.start_color and name_cell.fill.start_color.rgb:
                    name_color = name_cell.fill.start_color.rgb
                is_dropped = is_yellow_color(name_color)
                
                # Check for green background color on student or date cell (free enrollment)
                date_cell = sheet.cell(row=r_idx, column=3)
                date_color = None
                if date_cell.fill and date_cell.fill.start_color and date_cell.fill.start_color.rgb:
                    date_color = date_cell.fill.start_color.rgb
                is_free = is_green_color(name_color) or is_green_color(date_color)
                
                # Parse phone1 (AK / 37) and phone2 (AL / 38)
                phone1_val = sheet.cell(row=r_idx, column=37).value
                phone2_val = sheet.cell(row=r_idx, column=38).value
                
                phone1_str = clean_phone_number(phone1_val)
                if not phone1_str:
                    phone1_str = "+998900000000"
                
                phone2_str = clean_phone_number(phone2_val)

                # Find or create Student, setting/updating numbers
                student, created = Student.objects.get_or_create(
                    full_name=student_name,
                    defaults={
                        'phone1': phone1_str,
                        'phone2': phone2_str
                    }
                )
                if not created:
                    student.phone1 = phone1_str
                    if phone2_str:
                        student.phone2 = phone2_str
                    student.save()
                total_students_imported += 1

                # Create Enrollment (exclude student if yellow background detected)
                enrollment = Enrollment.objects.create(
                    student=student,
                    group=group,
                    date=enrollment_date,
                    status='dropped' if is_dropped else 'enrolled',
                    enrolled_free=is_free
                )

                # Auto-generate payments for prior months to mark them as paid (only if not free enrollment)
                if not is_free:
                    temp_year = enrollment_date.year
                    temp_month = enrollment_date.month
                    target_year = current_year
                    target_month = current_month

                    while (temp_year < target_year) or (temp_year == target_year and temp_month < target_month):
                        pay_day = min(enrollment_date.day, 28)
                        pay_date = datetime.date(temp_year, temp_month, pay_day)
                        
                        Payment.objects.create(
                            group=group,
                            student=student,
                            amount=group_price,
                            payment_method='cash',
                            status='accepted',
                            description=f"Auto-generated payment for prior month: {pay_date.strftime('%B %Y')}",
                            payment_date=timezone.make_aware(datetime.datetime.combine(pay_date, datetime.time(12, 0)))
                        )
                        total_payments_imported += 1
                        
                        # Increment month
                        if temp_month == 12:
                            temp_month = 1
                            temp_year += 1
                        else:
                            temp_month += 1

                # Col AI (35): Total paid
                if not is_free:
                    paid_val = sheet.cell(row=r_idx, column=35).value
                    try:
                        total_paid = float(paid_val or 0) * 1000
                    except (ValueError, TypeError):
                        total_paid = 0.0

                    if total_paid > 0:
                        Payment.objects.create(
                            group=group,
                            student=student,
                            amount=Decimal(str(total_paid)),
                            payment_method='cash',
                            status='accepted',
                            description="Imported total paid from Excel sheet"
                        )
                        total_payments_imported += 1

                # Col AJ (36): Debt / Overpaid
                if not is_free:
                    note_cell = sheet.cell(row=r_idx, column=36)
                    note_val = note_cell.value
                    
                    # Check color
                    color_hex = None
                    if note_cell.font and note_cell.font.color and note_cell.font.color.rgb:
                        color_hex = note_cell.font.color.rgb
                    if not color_hex and note_cell.fill and note_cell.fill.start_color and note_cell.fill.start_color.rgb:
                        color_hex = note_cell.fill.start_color.rgb
                    
                    is_green = is_green_color(color_hex)

                    if is_green and note_val:
                        try:
                            overpaid_val = float(note_val) * 1000
                        except (ValueError, TypeError):
                            overpaid_val = 0.0
                        
                        if overpaid_val > 0:
                            Payment.objects.create(
                                group=group,
                                student=student,
                                amount=Decimal(str(overpaid_val)),
                                payment_method='cash',
                                status='accepted',
                                description="Imported overpayment from Excel sheet"
                            )
                            total_payments_imported += 1

                # Recalculate enrollment debt
                enrollment.check_debt()

                # Col D (4) to AH (34): Absences
                for day_col in range(4, 35):
                    day_num = day_col - 3
                    cell_val = sheet.cell(row=r_idx, column=day_col).value
                    if cell_val and str(cell_val).strip() == "-":
                        Absence.objects.create(
                            student=student,
                            group=group,
                            teacher=teacher,
                            date=datetime.date(current_year, current_month, day_num)
                        )
                        total_absences_imported += 1

    return {
        'status': 'success',
        'imported_groups': imported_groups,
        'total_students': total_students_imported,
        'total_payments': total_payments_imported,
        'total_absences': total_absences_imported
    }
