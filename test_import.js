const fetch = require('node-fetch');

(async () => {
  const loginRes = await fetch('http://localhost:3000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'coordinador', password: 'coordinador123' })
  });
  console.log("Login:", loginRes.status);
  const cookies = loginRes.headers.raw()['set-cookie'];
  const cookieStr = cookies ? cookies.map(c => c.split(';')[0]).join('; ') : '';
  const csrfMatch = cookieStr.match(/csrftoken=([^;]+)/);
  const csrf = csrfMatch ? csrfMatch[1] : '';

  const tplRes = await fetch('http://localhost:3000/api/alumnos/plantilla/', {
    headers: { 'Cookie': cookieStr }
  });
  console.log("Template:", tplRes.status);
  const fs = require('fs');
  const buffer = await tplRes.buffer();
  fs.writeFileSync('plantilla.xlsx', buffer);

  const FormData = require('form-data');
  const fd = new FormData();
  fd.append('archivo', fs.createReadStream('plantilla.xlsx'));
  fd.append('programa_educativo', '1');

  const headers = fd.getHeaders();
  headers['Cookie'] = cookieStr;
  headers['X-CSRFToken'] = csrf;

  const upRes = await fetch('http://localhost:3000/api/alumnos/importar_excel/', {
    method: 'POST',
    headers: headers,
    body: fd
  });
  const upText = await upRes.text();
  console.log("Upload:", upRes.status, upText);
})();
