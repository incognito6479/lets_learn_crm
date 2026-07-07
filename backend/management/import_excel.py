import re
import datetime
import openpyxl
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from management.models import User, Student, Group, Enrollment, Payment, Absence
from management.helpers import is_yellow_color, is_green_color, is_red_color, clean_phone_number, parse_enrollment_date

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
                    phone1 =  phone1_str,
                    defaults={
                        'phone2': phone2_str
                    }
                )
                if not created:
                    student.phone1 = phone1_str
                    if phone2_str:
                        student.phone2 = phone2_str
                    student.save()
                total_students_imported += 1

                # Find or create Enrollment (exclude student if yellow background detected)
                enrollment, enrolled_created = Enrollment.objects.get_or_create(
                    student=student,
                    group=group,
                    defaults={
                        'date': enrollment_date,
                        'status': 'dropped' if is_dropped else 'enrolled',
                        'enrolled_free': is_free
                    }
                )
                if not enrolled_created:
                    enrollment.date = enrollment_date
                    enrollment.status = 'dropped' if is_dropped else 'enrolled'
                    enrollment.enrolled_free = is_free
                    enrollment.save()

                # Read total paid current month from Col AI (35)
                total_paid_current = 0.0
                if not is_free:
                    paid_val = sheet.cell(row=r_idx, column=35).value
                    try:
                        val = float(paid_val or 0)
                        total_paid_current = val * 1000 if val < 10000 else val
                    except (ValueError, TypeError):
                        total_paid_current = 0.0

                # Check Col AJ (36) for red debt value or green overpayment
                debt_val = 0.0
                overpaid_val = 0.0
                note_cell = sheet.cell(row=r_idx, column=36)
                note_val = note_cell.value
                
                # Check color of note cell
                color_hex = None
                if note_cell.font and note_cell.font.color and note_cell.font.color.rgb:
                    color_hex = note_cell.font.color.rgb
                if not color_hex and note_cell.fill and note_cell.fill.start_color and note_cell.fill.start_color.rgb:
                    color_hex = note_cell.fill.start_color.rgb

                is_red = is_red_color(color_hex)
                is_green = is_green_color(color_hex)

                if not is_free and note_val is not None and str(note_val).strip() != "":
                    if is_red:
                        try:
                            val = float(note_val)
                            debt_val = val * 1000 if val < 10000 else val
                        except (ValueError, TypeError):
                            debt_val = 0.0
                    elif is_green:
                        try:
                            val = float(note_val)
                            overpaid_val = val * 1000 if val < 10000 else val
                        except (ValueError, TypeError):
                            overpaid_val = 0.0

                # Auto-generate payments for prior months to mark them as paid (only if not free enrollment)
                if not is_free:
                    temp_year = enrollment_date.year
                    temp_month = enrollment_date.month
                    target_year = current_year
                    target_month = current_month

                    # Count how many prior months we have
                    prior_months_dates = []
                    while (temp_year < target_year) or (temp_year == target_year and temp_month < target_month):
                        prior_months_dates.append((temp_year, temp_month))
                        if temp_month == 12:
                            temp_month = 1
                            temp_year += 1
                        else:
                            temp_month += 1

                    # Expected amount in total (prior months + current month)
                    expected_amount = (len(prior_months_dates) + 1) * group_price
                    # We want total paid to be: expected_amount - debt_val
                    # So the amount to pay for prior months is: expected_amount - debt_val - total_paid_current
                    prior_paid_amount = float(expected_amount) - debt_val - total_paid_current

                    # Distribute prior_paid_amount across the prior months
                    for p_year, p_month in prior_months_dates:
                        pay_amount = 0.0
                        if prior_paid_amount >= float(group_price):
                            pay_amount = float(group_price)
                            prior_paid_amount -= float(group_price)
                        elif prior_paid_amount > 0:
                            pay_amount = prior_paid_amount
                            prior_paid_amount = 0.0
                        
                        if pay_amount > 0:
                            pay_day = min(enrollment_date.day, 28)
                            pay_date = datetime.date(p_year, p_month, pay_day)
                            Payment.objects.create(
                                group=group,
                                student=student,
                                amount=Decimal(str(pay_amount)),
                                payment_method='cash',
                                status='accepted',
                                description=f"Auto-generated payment for prior month: {pay_date.strftime('%B %Y')}",
                                payment_date=timezone.make_aware(datetime.datetime.combine(pay_date, datetime.time(12, 0)))
                            )
                            total_payments_imported += 1

                # Create current month payment from Col AI (35)
                if not is_free and total_paid_current > 0:
                    Payment.objects.create(
                        group=group,
                        student=student,
                        amount=Decimal(str(total_paid_current)),
                        payment_method='cash',
                        status='accepted',
                        description="Imported total paid from Excel sheet"
                    )
                    total_payments_imported += 1

                # Create overpayment payment from Col AJ (36)
                if not is_free and overpaid_val > 0:
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
