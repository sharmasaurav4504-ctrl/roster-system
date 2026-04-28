from django.contrib import admin
from .models import Employee, Roster, LeaveRequest, SwapRequest

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'name', 'role_type', 'manager')
    search_fields = ('emp_id', 'name')

@admin.register(Roster)
class RosterAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'shift_code')
    list_filter = ('date', 'shift_code')
    search_fields = ('employee__name', 'employee__emp_id')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'status')
    list_filter = ('status',)

@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ('from_employee', 'to_employee', 'date', 'status')
    list_filter = ('status',)
