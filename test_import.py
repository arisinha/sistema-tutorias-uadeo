import requests

session = requests.Session()
login_res = session.post('http://localhost:3000/api/auth/login/', json={'username': 'coordinador', 'password': 'coordinador123'})
print("Login:", login_res.status_code, login_res.text)

# Download template
template_res = session.get('http://localhost:3000/api/alumnos/plantilla/')
print("Template:", template_res.status_code)
with open('plantilla.xlsx', 'wb') as f:
    f.write(template_res.content)

# Upload template
with open('plantilla.xlsx', 'rb') as f:
    files = {'archivo': f}
    data = {'programa_educativo': 1}
    # It might need CSRF token, let's include it
    csrf_token = session.cookies.get('csrftoken', '')
    headers = {'X-CSRFToken': csrf_token}
    res = session.post('http://localhost:3000/api/alumnos/importar_excel/', files=files, data=data, headers=headers)
    print("Upload:", res.status_code, res.text)
