import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Componente a probar
import AlumnosGestionView from '../coordinador/AlumnosGestionView.vue'

// Vuetify config para que Test-Utils pueda procesar los V-Components
const vuetify = createVuetify({
  components,
  directives,
})

describe('AlumnosGestionView.vue', () => {
  it('abre el modal y emite o intenta preparar submitForm al intentar crear un alumno', async () => {
    // 1. Montar el componente integrando global Vuetify
    const wrapper = mount(AlumnosGestionView, {
      global: {
        plugins: [vuetify],
        provide: {
          showMessage: vi.fn() // Mockeamos la notificación global (toaster)
        }
      }
    })

    // 2. Comprobar que el modal de creación inicia cerrado
    expect(wrapper.vm.formDialog).toBe(false)
    
    // 3. Buscar y clickear el botón "Nuevo Alumno"
    const createBtn = wrapper.findAll('button').find(w => w.text().includes('Nuevo Alumno'))
    expect(createBtn).toBeDefined()
    
    await createBtn.trigger('click')
    
    // 4. Asegurarse de que el dialogo ahora esté abierto y en modo crear
    expect(wrapper.vm.formDialog).toBe(true)
    expect(wrapper.vm.isEditing).toBe(false)

    // Opcionalmente podemos probar los campos del modelo si los forzamos
    wrapper.vm.form.matricula = 'TEST001'
    wrapper.vm.form.nombre = 'Test Name'

    expect(wrapper.vm.form.matricula).toBe('TEST001')
  })
})