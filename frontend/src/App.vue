<!-- ==============================================================================
     CÓDIGO COMPLETO Y ACTUALIZADO PARA: frontend/src/App.vue (con accesorios)
============================================================================== -->
<script setup>
import { ref } from 'vue';
import axios from 'axios';

// --- 1. DATOS DE LA RED ---
// Datos de ejemplo actualizados para incluir la lista de accesorios.
const nodos = ref([
  { id: 'Bomba', elevacion: 100, demanda: 0 },
  { id: 'Union', elevacion: 102, demanda: 0 },
  { id: 'Rociador1', elevacion: 105, demanda: 15 },
  { id: 'Rociador2', elevacion: 104, demanda: 20 },
]);

const tuberias = ref([
  { id: 'T1', nodo_inicio: 'Bomba', nodo_fin: 'Union', longitud: 50, diametro: 75, material: 'Acero', accesorios: ['Entrada normal', 'Válvula de compuerta abierta'] },
  { id: 'T2', nodo_inicio: 'Union', nodo_fin: 'Rociador1', longitud: 30, diametro: 50, material: 'PVC', accesorios: ['Tee (paso directo)', 'Codo 90°', 'Salida de tubería'] },
  { id: 'T3', nodo_inicio: 'Union', nodo_fin: 'Rociador2', longitud: 40, diametro: 50, material: 'PVC', accesorios: ['Tee (ramal)', 'Codo 90°', 'Salida de tubería'] },
]);

// Lista de todos los accesorios disponibles que mostraremos en la interfaz.
const listaAccesoriosDisponibles = [
    "Válvula de compuerta abierta",
    "Válvula de bola abierta",
    "Válvula de retención (check)",
    "Codo 90°",
    "Codo 45°",
    "Tee (paso directo)",
    "Tee (ramal)",
    "Entrada normal",
    "Salida de tubería",
];

// --- 2. VARIABLES PARA GUARDAR LOS RESULTADOS ---
const resultados = ref(null);
const isLoading = ref(false);
const errorMessage = ref(null);

// --- 3. LA FUNCIÓN QUE SE EJECUTARÁ AL HACER CLIC EN EL BOTÓN ---
async function calcularRed() {
  console.log("Botón 'Calcular' presionado. Enviando datos...");
  isLoading.value = true;
  resultados.value = null;
  errorMessage.value = null;

  const payload = {
    nodos: nodos.value,
    tuberias: tuberias.value,
  };

  try {
    // Usamos la variable de entorno para la URL de la API.
    // Si no existe (en desarrollo local), usa la dirección local por defecto.
    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
    const response = await axios.post(`${apiUrl}/api/analyze`, payload);
    
    // Guardamos los resultados que nos devuelve el backend.
    resultados.value = response.data;
    console.log("Resultados recibidos:", response.data);

  } catch (error) {
    // Capturamos el error y mostramos un mensaje útil.
    console.error("Error al calcular la red:", error);
    if (error.response) {
      // El backend respondió con un error (ej. 404, 500)
      errorMessage.value = `Error del servidor: ${error.response.data.error || error.message}`;
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta (problema de conexión/CORS)
      errorMessage.value = "No se pudo conectar con el servidor de cálculo. ¿Está funcionando el backend?";
    } else {
      // Otro tipo de error
      errorMessage.value = `Error en la aplicación: ${error.message}`;
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <header>
    <h1>PipeNet Pro</h1>
    <p>La Calculadora de Redes de Tuberías Definitiva</p>
  </header>

  <main>
    <div class="panel-izquierdo">
      <h2>1. Defina su Red</h2>
      
      <h3>Nodos</h3>
      <table>
        <thead>
          <tr>
            <th>ID Nodo</th>
            <th>Elevación (m)</th>
            <th>Demanda (l/s)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="nodo in nodos" :key="nodo.id">
            <td><input v-model="nodo.id" /></td>
            <td><input type="number" v-model.number="nodo.elevacion" /></td>
            <td><input type="number" v-model.number="nodo.demanda" /></td>
          </tr>
        </tbody>
      </table>

      <h3>Tuberías</h3>
      <table>
        <thead>
          <tr>
            <th>ID Tubería</th>
            <th>Nodo Inicio</th>
            <th>Nodo Fin</th>
            <th>Longitud (m)</th>
            <th>Diámetro (mm)</th>
            <th>Material</th>
            <th>Accesorios</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tuberia in tuberias" :key="tuberia.id">
            <td><input v-model="tuberia.id" /></td>
            <td><input v-model="tuberia.nodo_inicio" /></td>
            <td><input v-model="tuberia.nodo_fin" /></td>
            <td><input type="number" v-model.number="tuberia.longitud" /></td>
            <td><input type="number" v-model.number="tuberia.diametro" /></td>
            <td>
              <select v-model="tuberia.material">
                <option>Acero</option>
                <option>PVC</option>
                <option>Hierro Fundido</option>
              </select>
            </td>
            <td>
              <div class="accesorios-container">
                  <div v-for="accesorio in listaAccesoriosDisponibles" :key="accesorio">
                    <input type="checkbox" :id="`${tuberia.id}-${accesorio}`" :value="accesorio" v-model="tuberia.accesorios">
                    <label :for="`${tuberia.id}-${accesorio}`">{{ accesorio }}</label>
                  </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <button @click="calcularRed" :disabled="isLoading">
        {{ isLoading ? 'Calculando...' : 'Calcular Sistema' }}
      </button>

    </div>

    <div class="panel-derecho">
      <h2>2. Resultados del Sistema</h2>

      <div v-if="isLoading" class="mensaje">
        Conectando con el motor de cálculo...
      </div>
      
      <div v-if="errorMessage" class="mensaje error">
        {{ errorMessage }}
      </div>

      <div v-if="resultados">
        <h3>Requerimientos de Bombeo</h3>
        <div class="resultados-bomba">
          <div>
            <span>Caudal (Q)</span>
            <strong>{{ resultados.bomba_requerido.caudal_lps.toFixed(2) }} l/s</strong>
          </div>
          <div>
            <span>Carga (H)</span>
            <strong>{{ resultados.bomba_requerido.carga_m.toFixed(2) }} m</strong>
          </div>
        </div>
        <p class="ruta-critica">
          <strong>Ruta Crítica:</strong> {{ resultados.bomba_requerido.ruta_critica }}
        </p>

        <h3>Resultados por Tubería</h3>
        <table>
          <thead>
            <tr>
              <th>ID Tubería</th>
              <th>Caudal (l/s)</th>
              <th>Velocidad (m/s)</th>
              <th>Pérdida hf (m)</th>
              <th>Pérdida hl (m)</th>
              <th>Pérdida Total (m)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tuberia in resultados.resultados_tuberias" :key="tuberia.id">
              <td>{{ tuberia.id }}</td>
              <td>{{ tuberia.caudal_lps.toFixed(2) }}</td>
              <td>{{ tuberia.velocidad_ms.toFixed(2) }}</td>
              <td>{{ tuberia.perdida_hf_m.toFixed(2) }}</td>
              <td>{{ tuberia.perdida_hl_m.toFixed(2) }}</td>
              <td><strong>{{ tuberia.perdida_total_m.toFixed(2) }}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="!isLoading && !errorMessage" class="mensaje">
        Presione "Calcular Sistema" para ver los resultados.
      </div>
    </div>
  </main>
</template>

<style>
body { font-family: sans-serif; background-color: #f0f2f5; color: #333; }
#app { max-width: 1400px; margin: 0 auto; padding: 1rem; }
header { background-color: #003366; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem; }
main { display: flex; gap: 1rem; }
.panel-izquierdo, .panel-derecho { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }
h2 { color: #003366; border-bottom: 2px solid #ddd; padding-bottom: 0.5rem; margin-top: 0; }
h3 { margin-top: 1.5rem; }

table { width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 14px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
th { background-color: #f2f2f2; }
input, select { width: 100%; box-sizing: border-box; border: 1px solid #ccc; padding: 6px; border-radius: 4px; }
input[type="checkbox"] { width: auto; margin-right: 5px; }

button {
  width: 100%;
  padding: 12px;
  margin-top: 1.5rem;
  background-color: #0056b3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}
button:hover { background-color: #003366; }
button:disabled { background-color: #aaa; cursor: not-allowed; }

.mensaje { text-align: center; color: #888; padding: 2rem; }
.mensaje.error { color: #d93025; font-weight: bold; }
.resultados-bomba { display: flex; justify-content: space-around; background-color: #e6f7ff; padding: 1rem; border-radius: 8px; text-align: center; }
.resultados-bomba div { display: flex; flex-direction: column; }
.resultados-bomba span { font-size: 14px; color: #555; }
.resultados-bomba strong { font-size: 24px; color: #003366; }
.ruta-critica { margin-top: 1rem; font-style: italic; color: #555; }

.accesorios-container {
    max-height: 120px;
    overflow-y: auto;
    border: 1px solid #ccc;
    padding: 5px;
    border-radius: 4px;
    background-color: #fff;
}
.accesorios-container div {
    display: flex;
    align-items: center;
    padding: 2px 0;
}
.accesorios-container label {
    white-space: nowrap;
}
</style>