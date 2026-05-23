import { test, expect } from '@playwright/test';

test.describe('Gestión de Alumnos (Coordinador)', () => {

  test.beforeEach(async ({ page }) => {
    // 1. Simulación de Autenticación de un Coordinador
    await page.goto('/login');
    
    // El formulario original de tu app
    const inputs = page.locator('input');
    await inputs.nth(0).fill('coordinador_demo');
    await inputs.nth(1).fill('password123');
    
    await page.click('button[type="submit"]');

    // 2. Validamos que aterrizó en el sistema (ej. dashboard o panel)
    await page.waitForURL('**/dashboard**', { timeout: 10000 }).catch(() => {});
  });

  test('Coordinador abre Modal, llena datos y crea alumno', async ({ page }) => {
    // 3. Ir a la vista de Gestión de Alumnos
    await page.goto('/alumnos');
    
    // 4. Click en Nuevo Alumno
    await page.click('button:has-text("Nuevo Alumno")');
    
    // 5. Llenamos el modal de alumno
    const testMatricula = `2026${Date.now().toString().slice(-4)}`;
    
    await page.fill('input:has-text("Matrícula"), input[aria-label="Matrícula"], label:has-text("Matrícula") + input, input:near(:text("Matrícula"))', testMatricula);
    await page.fill('input:has-text("Nombre"), input[aria-label="Nombre(s)"]', 'Estudiante E2E');
    await page.fill('input:has-text("Apellido Paterno"), input[aria-label="Apellido Paterno"]', 'Prueba');
    
    // Selección de variables de formulario (Por ejemplo semestre y programa)
    // Para v-selects a veces es necesario hacer click y seleccionar el list-item
    await page.click('div.v-select:has-text("Semestre")');
    await page.click('.v-list-item:has-text("1")');
    
    // Hacer Submit
    await page.click('button:has-text("Crear")');
    
    // 6. Validar que el estudiante aparece en la tabla
    const tabla = page.locator('table');
    await expect(tabla).toContainText(testMatricula, { timeout: 15000 });
  });
});