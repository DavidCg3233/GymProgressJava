import { createApp } from 'vue'

import App from './App.vue'
import { iniciarSincronizacion } from './estado/sesion.js'
import './estilos/base.css'

createApp(App).mount('#app')

// Envía lo pendiente al volver la señal o al volver a la app (RF-006-16).
iniciarSincronizacion()

// Pide al navegador que no borre los datos del celular por falta de espacio (RNF-006-06).
navigator.storage?.persist?.()
