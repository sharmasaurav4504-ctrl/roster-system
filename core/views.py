import csv
import io
import pandas as pd
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import Employee, Roster, LeaveRequest, SwapRequest
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        emp_id = request.POST.get('emp_id')
        password = request.POST.get('password')
        
        try:
            if role == 'Agent':
                # Use guest account if no ID provided
                username = emp_id.lower() if emp_id else 'agent_guest'
                try:
                    user = User.objects.get(username=username)
                    login(request, user)
                    return redirect('dashboard')
                except User.DoesNotExist:
                    messages.error(request, "Agent account not found.")
            else:
                # Use default role account if no specific employee selected
                username = emp_id.lower() if emp_id else ('wfm' if role == 'WFM' else 'sup')
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid password.")
        except Exception as e:
            messages.error(request, "Login failed.")
                
    employees = Employee.objects.all().order_by('name')
    return render(request, 'core/login.html', {'employees': employees})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    # Safely get employee profile
    employee = getattr(request.user, 'employee_profile', None)
    
    # If no profile, use a dummy one for the session (prevents crashing)
    if not employee:
        employee = type('obj', (object,), {
            'name': 'Guest Agent' if request.user.username == 'agent_guest' else 'System Admin',
            'emp_id': 'GUEST' if request.user.username == 'agent_guest' else 'ADMIN',
            'role_type': 'Agent' if request.user.username == 'agent_guest' else ('WFM' if request.user.is_superuser else 'Guest')
        })
    
    # Get unique dates from Roster to build horizontal header
    dates = list(Roster.objects.order_by('date').values_list('date', flat=True).distinct())
    
    # Capture filters
    f_role = request.GET.get('role')
    f_pms = request.GET.get('pms')
    f_manager = request.GET.get('manager')
    f_view = request.GET.get('view', 'all')
    f_page = int(request.GET.get('page', 0))
    
    # Show all employees who have at least one roster entry
    employees = Employee.objects.filter(rosters__isnull=False).distinct()
    
    # Apply View Range Filter (Week / Month) with Pagination
    total_dates = len(dates)
    view_label = ""
    has_next = False
    
    if dates and f_view != 'all':
        today = datetime.now().date()
        
        if f_view == 'week':
            weeks = []
            week_map = {}
            for d in dates:
                w_key = d.isocalendar()[:2]
                if w_key not in week_map:
                    week_map[w_key] = []
                    weeks.append(w_key)
                week_map[w_key].append(d)
                
            total_pages = len(weeks)
            
            if 'page' not in request.GET:
                today_w_key = today.isocalendar()[:2]
                if today_w_key in weeks:
                    f_page = weeks.index(today_w_key)
                else:
                    closest_d = min(dates, key=lambda x: abs(x - today))
                    f_page = weeks.index(closest_d.isocalendar()[:2])
            
            f_page = max(0, min(f_page, total_pages - 1))
            dates = week_map[weeks[f_page]]
            
            start_of_week = dates[0] - timedelta(days=dates[0].weekday())
            view_label = f"Week of {start_of_week.strftime('%a, %d %b %Y')}"
            has_next = f_page < total_pages - 1
            
        elif f_view == 'month':
            months = []
            month_map = {}
            for d in dates:
                m_key = (d.year, d.month)
                if m_key not in month_map:
                    month_map[m_key] = []
                    months.append(m_key)
                month_map[m_key].append(d)
                
            total_pages = len(months)
            
            if 'page' not in request.GET:
                today_m_key = (today.year, today.month)
                if today_m_key in months:
                    f_page = months.index(today_m_key)
                else:
                    closest_d = min(dates, key=lambda x: abs(x - today))
                    f_page = months.index((closest_d.year, closest_d.month))
            
            f_page = max(0, min(f_page, total_pages - 1))
            dates = month_map[months[f_page]]
            
            view_label = f"{dates[0].strftime('%B %Y')}"
            has_next = f_page < total_pages - 1
    else:
        f_page = 0
    
    if f_role: employees = employees.filter(role_type=f_role)
    if f_pms: employees = employees.filter(pms=f_pms)
    if f_manager: employees = employees.filter(manager=f_manager)
    
    # Get options for filters
    roles = Employee.objects.filter(rosters__isnull=False).values_list('role_type', flat=True).distinct()
    pms_list = Employee.objects.filter(rosters__isnull=False).values_list('pms', flat=True).distinct()
    managers = Employee.objects.filter(rosters__isnull=False).values_list('manager', flat=True).distinct()
    
    roster_data = []
    for emp in employees:
        emp_roster = {
            'emp': emp,
            'shifts': {r.date: r.shift_code for r in emp.rosters.all()}
        }
        roster_data.append(emp_roster)
    
    context = {
        'employee': employee,
        'dates': dates,
        'roster_data': roster_data,
        'shift_choices': [c[0] for c in Roster.SHIFT_CODES],
        'roles': roles,
        'pms_list': pms_list,
        'managers': managers,
        'f_role': f_role,
        'f_pms': f_pms,
        'f_manager': f_manager,
        'f_view': f_view,
        'f_page': f_page,
        'view_label': view_label,
        'has_next': has_next,
        'total_dates': total_dates,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def upload_roster(request):
    if request.user.employee_profile.role_type != 'WFM':
        messages.error(request, "Only WFM has upload rights.")
        return redirect('dashboard')
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        try:
            # Detect file type
            file_name = csv_file.name.lower()
            if file_name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(csv_file)
            else:
                # Try multiple common encodings
                encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'utf-16']
                df = None
                last_error = ""
                for enc in encodings:
                    try:
                        csv_file.seek(0)
                        content = csv_file.read().decode(enc)
                        text_stream = io.StringIO(content)
                        df = pd.read_csv(text_stream, sep=None, engine='python', on_bad_lines='skip')
                        break
                    except Exception as e:
                        last_error = str(e)
                        continue
            
            if df is None:
                raise ValueError(f"Could not parse file. Last error: {last_error}")
            
            # Expected format: EMP ID, Name, Role, PMS, Manager, [Date Columns...]
            # Standard headers check
            required_headers = ['EMP ID', 'Name', 'Role', 'PMS', 'Manager']
            if not all(h in df.columns for h in required_headers):
                messages.error(request, "Missing required headers.")
                return redirect('dashboard')
            
            date_cols = [col for col in df.columns if col not in required_headers]
            
            Roster.objects.all().delete()
            # Remove agents/employees who were only in the old roster
            Employee.objects.exclude(role_type__in=['WFM', 'Supervisor']).delete()
            
            for index, row in df.iterrows():
                emp_id = str(row['EMP ID'])
                # Create or Update Employee (Simplified)
                user_obj, created = User.objects.get_or_create(username=emp_id.lower())
                if created: user_obj.set_password('pass123'); user_obj.save()
                
                emp, _ = Employee.objects.get_or_create(emp_id=emp_id, defaults={
                    'user': user_obj,
                    'name': row['Name'],
                    'role_type': row['Role'],
                    'pms': row['PMS'],
                    'manager': row['Manager']
                })
                
                for d_str in date_cols:
                    try:
                        # Robust date parsing
                        date_obj = pd.to_datetime(d_str, format='mixed', errors='coerce').date()
                        if pd.isna(date_obj): continue
                        
                        if pd.isna(row[d_str]):
                            continue
                            
                        shift_val = str(row[d_str]).strip()
                        if shift_val and shift_val.lower() not in ['nan', 'none', '-', '']:
                            Roster.objects.update_or_create(
                                employee=emp, date=date_obj,
                                defaults={'shift_code': shift_val}
                            )
                    except Exception as e:
                        continue
                        
            messages.success(request, "Roster uploaded successfully.")
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            
    return redirect('dashboard')

@login_required
def export_roster(request):
    # WFM and Supervisor can export
    if request.user.employee_profile.role_type not in ['WFM', 'Supervisor']:
        return HttpResponse("Unauthorized", status=403)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="roster_export.csv"'
    
    writer = csv.writer(response)
    dates = Roster.objects.order_by('date').values_list('date', flat=True).distinct()
    header = ['EMP ID', 'Name', 'Role', 'PMS', 'Manager'] + [d.strftime('%Y-%m-%d') for d in dates]
    writer.writerow(header)
    
    employees = Employee.objects.all()
    for emp in employees:
        row = [emp.emp_id, emp.name, emp.role_type, emp.pms, emp.manager]
        shifts = {r.date: r.shift_code for r in emp.rosters.all()}
        for d in dates:
            row.append(shifts.get(d, ''))
        writer.writerow(row)
        
    return response

@login_required
def update_shift(request):
    if request.user.employee_profile.role_type not in ['WFM', 'Supervisor']:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        date_str = request.POST.get('date')
        shift_code = request.POST.get('shift_code')
        
        try:
            emp = Employee.objects.get(id=emp_id)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            Roster.objects.update_or_create(
                employee=emp, date=date_obj,
                defaults={'shift_code': shift_code}
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def apply_leave(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        leave_type = request.POST.get('leave_type')
        reason = request.POST.get('reason')
        
        try:
            emp = Employee.objects.get(emp_id=emp_id)
            LeaveRequest.objects.create(
                employee=emp,
                start_date=start_date,
                end_date=end_date,
                leave_type=leave_type,
                reason=reason
            )
            messages.success(request, f"Leave request submitted for {emp.name}.")
        except Employee.DoesNotExist:
            messages.error(request, f"Error: Employee ID {emp_id} not found.")
            
    return redirect('dashboard')

@login_required
def requests_view(request):
    if request.user.employee_profile.role_type not in ['WFM', 'Supervisor']:
        return redirect('dashboard')
    
    leaves = LeaveRequest.objects.all().order_by('-created_at')
    swaps = SwapRequest.objects.all().order_by('-created_at')
    
    return render(request, 'core/requests.html', {
        'leaves': leaves,
        'swaps': swaps
    })

@login_required
def manage_leave(request, leave_id, action):
    if request.user.employee_profile.role_type not in ['WFM', 'Supervisor']:
        return HttpResponse("Unauthorized", status=403)
    
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    if action == 'approve':
        leave.status = 'Approved'
        # Logic to update roster shifts
        curr_date = leave.start_date
        while curr_date <= leave.end_date:
            roster_entry = Roster.objects.filter(employee=leave.employee, date=curr_date).first()
            if roster_entry:
                # If shift is not WO or H, change to requested leave type
                if roster_entry.shift_code not in ['WO', 'H']:
                    roster_entry.shift_code = leave.leave_type
                    roster_entry.save()
            else:
                # If no roster entry exists, create one with requested leave type
                Roster.objects.create(employee=leave.employee, date=curr_date, shift_code=leave.leave_type)
            
            curr_date += timedelta(days=1)
            
    elif action == 'reject':
        leave.status = 'Rejected'
    leave.save()
    
    messages.success(request, f"Leave {action}ed for {leave.employee.name}")
    return redirect('requests')

@login_required
def manage_swap(request, swap_id, action):
    if request.user.employee_profile.role_type not in ['WFM', 'Supervisor']:
        return HttpResponse("Unauthorized", status=403)
    
    swap = get_object_or_404(SwapRequest, id=swap_id)
    if action == 'approve':
        swap.status = 'Accepted'
    elif action == 'reject':
        swap.status = 'Rejected'
    swap.save()
    
    messages.success(request, f"Swap {action}ed between {swap.from_employee.name} and {swap.to_employee.name}")
    return redirect('requests')

