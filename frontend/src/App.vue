<!-- ==============================================================================
     CÓDIGO COMPLETO Y FINAL PARA: frontend/src/App.vue (con Guardar/Cargar)
============================================================================== -->
<script setup>
import { ref } from 'vue';
import axios from 'axios';

// --- DATOS DE LA RED ---
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

const listaAccesoriosDisponibles = [
    "Válvula de compuerta abierta", "Válvula de bola abierta", "Válvula de retención (check)",
    "Codo 90°", "Codo 45°", "Tee (paso directo)", "Tee (ramal)", "Entrada normal", "Salida de tubería",
];

// --- VARIABLES DE ESTADO ---
const resultados = ref(null);
const isLoading = ref(false);
const errorMessage = ref(null);

// --- FUNCIÓN DE CÁLCULO ---
async function calcularRed() {
  isLoading.value = true;
  resultados.value = null;
  errorMessage.value = null;
  const payload = { nodos: nodos.value, tuberias: tuberias.value };
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
    const response = await axios.post(`${apiUrl}/api/analyze`, payload);
    resultados.value = response.data;
  } catch (error) {
    console.error("Error al calcular la red:", error);
    if (error.response) {
      errorMessage.value = `Error del servidor: ${error.response.data.error || error.message}`;
    } else {
      errorMessage.value = "No se pudo conectar con el servidor de cálculo. ¿Está funcionando el backend?";
    }
  } finally {
    isLoading.value = false;
  }
}

// --- FUNCIONES PARA MANEJAR FILAS ---
function agregarNodo() {
  const nuevoId = `N-${nodos.value.length + 1}`;
  nodos.value.push({ id: nuevoId, elevacion: 0, demanda: 0 });
}

function eliminarNodo(index) {
  if (nodos.value.length > 1) {
    nodos.value.splice(index, 1);
  }
}

function agregarTuberia() {
  const nuevoId = `T-${tuberias.value.length + 1}`;
  tuberias.value.push({ id: nuevoId, nodo_inicio: '', nodo_fin: '', longitud: 10, diametro: 50, material: 'PVC', accesorios: [] });
}

function eliminarTuberia(index) {
  if (tuberias.value.length > 1) {
    tuberias.value.splice(index, 1);
  }
}

// --- ¡NUEVO! FUNCIONES PARA GUARDAR Y CARGAR PROYECTOS ---
function guardarProyecto() {
  // 1. Creamos un objeto que contiene el estado actual de la red.
  const datosProyecto = {
    nodos: nodos.value,
    tuberias: tuberias.value,
  };

  // 2. Convertimos el objeto a un string de texto en formato JSON.
  const datosString = JSON.stringify(datosProyecto, null, 2); // null, 2 para que el JSON se vea bonito.

  // 3. Creamos un "Blob", que es como un archivo en la memoria del navegador.
  const blob = new Blob([datosString], { type: 'application/json' });

  // 4. Creamos un enlace de descarga temporal y lo "clickeamos" con código.
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'proyecto_pipenet.json'; // Nombre del archivo que se descargará.
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function cargarProyecto(event) {
  const archivo = event.target.files[0];
  if (!archivo) {
    return;
  }

  // Usamos FileReader para leer el contenido del archivo seleccionado.
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const datosCargados = JSON.parse(e.target.result);
      // Validamos que el archivo tenga la estructura que esperamos.
      if (datosCargados.nodos && datosCargados.tuberias) {
        nodos.value = datosCargados.nodos;
        tuberias.value = datosCargados.tuberias;
        errorMessage.value = null; // Limpiamos errores anteriores.
        resultados.value = null; // Limpiamos resultados anteriores.
      } else {
        alert("El archivo no tiene el formato de proyecto de PipeNet Pro correcto.");
      }
    } catch (error) {
      alert("Error al leer el archivo. Asegúrese de que es un archivo .json válido.");
    }
  };
  reader.readAsText(archivo);
}

// ¡NUEVO! Una referencia al input de archivo oculto.
const inputFile = ref(null);

function triggerCargarProyecto() {
  // Esta función simula un clic en el input de archivo, que está oculto.
  inputFile.value.click();
}
</script>

<template>
  <header>
    <h1>PipeNet Pro</h1>
    <p>La Calculadora de Redes de Tuberías Definitiva</p>
  </header>

  <main>
    <div class="panel-izquierdo">
      <div class="panel-header">
        <h2>1. Defina su Red</h2>
        <!-- ¡NUEVO! Botones de Guardar/Cargar -->
        <div class="acciones-proyecto">
          <button @click="guardarProyecto" class="btn-accion">Guardar Proyecto</button>
          <button @click="triggerCargarProyecto" class="btn-accion">Cargar Proyecto</button>
          <!-- Input de archivo real, pero oculto. Lo activamos con el botón de arriba. -->
          <input type="file" ref="inputFile" @change="cargarProyecto" accept=".json" style="display: none;" />
        </div>
      </div>
      
      <h3>Nodos</h3>
      <table>
        <thead>
          <tr>
            <th>ID Nodo</th> <th>Elevación (m)</th> <th>Demanda (l/s)</th> <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(nodo, index) in nodos" :key="`nodo-${index}`">
            <td><input v-model="nodo.id" /></td>
            <td><input type="number" v-model.number="nodo.elevacion" /></td>
            <td><input type="number" v-model.number="nodo.demanda" /></td>
            <td><button @click="eliminarNodo(index)" class="btn-eliminar" title="Eliminar fila">-</button></td>
          </tr>
        </tbody>
      </table>
      <button @click="agregarNodo" class="btn-agregar">+ Añadir Nodo</button>

      <h3>Tuberías</h3>
      <table>
        <thead>
          <tr>
            <th>ID Tubería</th> <th>Nodo Inicio</th> <th>Nodo Fin</th> <th>Longitud (m)</th>
            <th>Diámetro (mm)</th> <th>Material</th> <th>Accesorios</th> <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(tuberia, index) in tuberias" :key="`tuberia-${index}`">
            <td><input v-model="tuberia.id" /></td>
            <td><input v-model="tuberia.nodo_inicio" /></td>
            <td><input v-model="tuberia.nodo_fin" /></td>
            <td><input type="number" v-model.number="tuberia.longitud" /></td>
            <td><input type="number" v-model.number="tuberia.diametro" /></td>
            <td>
              <select v-model="tuberia.material">
                <option>Acero</option> <option>PVC</option> <option>Hierro Fundido</option>
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
            <td><button @click="eliminarTuberia(index)" class="btn-eliminar" title="Eliminar fila">-</button></td>
          </tr>
        </tbody>
      </table>
      <button @click="agregarTuberia" class="btn-agregar">+ Añadir Tubería</button>
      
      <button @click="calcularRed" :disabled="isLoading" class="btn-principal">
        {{ isLoading ? 'Calculando...' : 'Calcular Sistema' }}
      </button>
    </div>

    <div class="panel-derecho">
      <h2>2. Resultados del Sistema</h2>
      <div v-if="isLoading" class="mensaje">Conectando con el motor de cálculo...</div>
      <div v-if="errorMessage" class="mensaje error">{{ errorMessage }}</div>
      <div v-if="resultados">
        <h3>Requerimientos de Bombeo</h3>
        <div class="resultados-bomba">
          <div><span>Caudal (Q)</span><strong>{{ resultados.bomba_requerido.caudal_lps.toFixed(2) }} l/s</strong></div>
          <div><span>Carga (H)</span><strong>{{ resultados.bomba_requerido.carga_m.toFixed(2) }} m</strong></div>
        </div>
        <p class="ruta-critica"><strong>Ruta Crítica:</strong> {{ resultados.bomba_requerido.ruta_critica }}</p>
        <h3>Resultados por Tubería</h3>
        <table>
          <thead>
            <tr>
              <th>ID Tubería</th><th>Caudal (l/s)</th><th>Velocidad (m/s)</th><th>Pérdida hf (m)</th><th>Pérdida hl (m)</th><th>Pérdida Total (m)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tuberia in resultados.resultados_tuberias" :key="tuberia.id">
              <td>{{ tuberia.id }}</td><td>{{ tuberia.caudal_lps.toFixed(2) }}</td><td>{{ tuberia.velocidad_ms.toFixed(2) }}</td><td>{{ tuberia.perdida_hf_m.toFixed(2) }}</td><td>{{ tuberia.perdida_hl_m.toFixed(2) }}</td><td><strong>{{ tuberia.perdida_total_m.toFixed(2) }}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!isLoading && !errorMessage" class="mensaje">Presione "Calcular Sistema" para ver los resultados.</div>
    </div>
  </main>
</template>

<style>
body { font-family: sans-serif; background-color: #f0f2f5; color: #333; }
#app { max-width: 1400px; margin: 0 auto; padding: 1rem; }
header { background-color: #003366; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem; }
main { display: flex; align-items: flex-start; gap: 1rem; }
.panel-izquierdo, .panel-derecho { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }
.panel-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ddd; padding-bottom: 0.5rem; }
.panel-header h2 { border-bottom: none; padding-bottom: 0; margin: 0; }
.acciones-proyecto { display: flex; gap: 0.5rem; }
h3 { margin-top: 1.5rem; }

table { width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 14px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: middle; }
th { background-color: #f2f2f2; }
input, select { width: 100%; box-sizing: border-box; border: 1px solid #ccc; padding: 6px; border-radius: 4px; }
input[type="checkbox"] { width: auto; margin-right: 5px; }

.btn-principal {
  width: 100%; padding: 12px; margin-top: 2rem; background-color: #0056b3;
  color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer;
  transition: background-color 0.2s;
}
.btn-principal:hover { background-color: #003366; }
.btn-principal:disabled { background-color: #aaa; cursor: not-allowed; }

.btn-agregar {
  width: 100%; padding: 8px; margin-top: 0.5rem; background-color: #e7f3ff;
  color: #0056b3; border: 1px dashed #0056b3; border-radius: 4px;
  cursor: pointer; transition: background-color 0.2s;
}
.btn-agregar:hover { background-color: #d0e7ff; }

.btn-eliminar {
  background-color: #ff4d4f; color: white; border: none;
  border-radius: 50%; width: 24px; height: 24px;
  font-weight: bold; font-size: 16px; line-height: 24px;
  cursor: pointer; transition: background-color 0.2s; display: block; margin: 0 auto;
}
.btn-eliminar:hover { background-color: #d9363e; }

.btn-accion {
  padding: 8px 12px; background-color: #6c757d; color: white;
  border: none; border-radius: 4px; cursor: pointer;
  font-size: 14px; transition: background-color 0.2s;
}
.btn-accion:hover { background-color: #5a6268; }

.mensaje { text-align: center; color: #888; padding: 2rem; }
.mensaje.error { color: #d93025; font-weight: bold; }
.resultados-bomba { display: flex; justify-content: space-around; background-color: #e6f7ff; padding: 1rem; border-radius: 8px; text-align: center; }
.resultados-bomba div { display: flex; flex-direction: column; }
.resultados-bomba span { font-size: 14px; color: #555; }
.resultados-bomba strong { font-size: 24px; color: #003366; }
.ruta-critica { margin-top: 1rem; font-style: italic; color: #555; }

.accesorios-container { max-height: 120px; overflow-y: auto; border: 1px solid #ccc; padding: 5px; border-radius: 4px; background-color: #fff; }
.accesorios-container div { display: flex; align-items: center; padding: 2px 0; }
.accesorios-container label { white-space: nowrap; }
</style>