import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

const customTheme = {
    dark: false,
    colors: {
        primary: '#1565C0',
        secondary: '#00897B',
        accent: '#7C4DFF',
        error: '#D32F2F',
        warning: '#F57C00',
        info: '#0288D1',
        success: '#388E3C',
        background: '#F5F7FA',
        surface: '#FFFFFF',
    },
}

const darkTheme = {
    dark: true,
    colors: {
        primary: '#42A5F5',
        secondary: '#26A69A',
        accent: '#B388FF',
        error: '#EF5350',
        warning: '#FFB74D',
        info: '#4FC3F7',
        success: '#66BB6A',
        background: '#121212',
        surface: '#1E1E1E',
    },
}

export default createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: { mdi },
    },
    theme: {
        defaultTheme: 'customTheme',
        themes: {
            customTheme,
            darkTheme,
        },
    },
    defaults: {
        VBtn: {
            variant: 'flat',
            rounded: 'lg',
        },
        VCard: {
            rounded: 'lg',
            elevation: 2,
        },
        VTextField: {
            variant: 'outlined',
            density: 'comfortable',
        },
        VSelect: {
            variant: 'outlined',
            density: 'comfortable',
        },
    },
})
