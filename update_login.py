import re

with open('d:/Roster/RosterApp/core/templates/core/login.html', 'r') as f:
    content = f.read()

new_content = content.replace(
    '<div class="form-group" id="password-group">',
    '''<div class="form-group" id="emp-id-group" style="display:none;">
                <label for="emp_id">Employee ID</label>
                <input type="text" name="emp_id" id="emp_id" class="form-control" placeholder="e.g. AGT001">
            </div>

            <div class="form-group" id="password-group">'''
)

new_content = new_content.replace(
    "passInput.removeAttribute('required');",
    "passInput.removeAttribute('required');\n            document.getElementById('emp-id-group').style.display = 'block';\n            document.getElementById('emp_id').setAttribute('required', 'required');"
)

new_content = new_content.replace(
    "passInput.setAttribute('required', 'required');",
    "passInput.setAttribute('required', 'required');\n            document.getElementById('emp-id-group').style.display = 'none';\n            document.getElementById('emp_id').removeAttribute('required');"
)

with open('d:/Roster/RosterApp/core/templates/core/login.html', 'w') as f:
    f.write(new_content)
