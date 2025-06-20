# ==============================================================================
#           NUEVO CONTENIDO PARA: backend/main.py (Preparado para API)
# ==============================================================================

# --- 0. IMPORTACIONES ---
from models import Nodo, Tuberia
import calculos_hidraulicos as ch
import networkx as nx

# ¡Nuevas importaciones para nuestra API!
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- LA FUNCIÓN PRINCIPAL QUE HACE TODO EL TRABAJO ---
# Hemos metido toda nuestra lógica aquí. Ahora recibe los datos como parámetros.
def analizar_red(datos_nodos, datos_tuberias):
    """
    Esta función recibe los datos de la red, realiza todos los cálculos
    y devuelve un diccionario con los resultados.
    """
    print(">>> Analizando red recibida...")
    
    # 1. CREAMOS LAS PIEZAS a partir de los datos recibidos
    nodos = {n_data['id']: Nodo(n_data['id'], n_data['elevacion'], n_data.get('demanda', 0)) for n_data in datos_nodos}
    tuberias = {t_data['id']: Tuberia(t_data['id'], t_data['nodo_inicio'], t_data['nodo_fin'], t_data['longitud'], t_data['diametro'], t_data['material']) for t_data in datos_tuberias}
    
    # 2. CÁLCULO DE CAUDALES
    G = nx.DiGraph()
    for t in tuberias.values():
        G.add_edge(t.nodo_inicio, t.nodo_fin, data=t)

    caudales_lps = {t_id: 0.0 for t_id in tuberias}
    demandas_lps = {n_id: n.demanda for n_id, n in nodos.items()}
    nodos_en_orden_inverso = reversed(list(nx.topological_sort(G)))

    nodo_fuente_id = None
    for nodo_id in nodos_en_orden_inverso:
        if not list(G.predecessors(nodo_id)):
            nodo_fuente_id = nodo_id
        
        caudal_saliente_total = demandas_lps[nodo_id]
        for tuberia_saliente_id in G.successors(nodo_id):
            tuberia_obj = G.edges[nodo_id, tuberia_saliente_id]['data']
            caudal_saliente_total += caudales_lps[tuberia_obj.id]
        
        predecesores = list(G.predecessors(nodo_id))
        if predecesores:
            nodo_anterior_id = predecesores[0]
            tuberia_entrante = G.edges[nodo_anterior_id, nodo_id]['data']
            caudales_lps[tuberia_entrante.id] = caudal_saliente_total

    for t_id, t in tuberias.items():
        t.caudal_calculado_m3s = caudales_lps[t_id] / 1000

    # 3. CÁLCULO DE PÉRDIDAS
    for t in tuberias.values():
        if t.caudal_calculado_m3s > 0:
            t.velocidad = ch.calcular_velocidad(t.caudal_calculado_m3s, t.diametro)
            t.reynolds = ch.calcular_reynolds(t.velocidad, t.diametro)
            t.factor_friccion = ch.calcular_factor_friccion(t.reynolds, t.rugosidad_e, t.diametro)
            t.perdida_friccion_hf = ch.calcular_perdida_friccion_hf(t.factor_friccion, t.longitud, t.diametro, t.velocidad)
            
    # 4. ENCONTRAR RUTA CRÍTICA
    nodos_finales_ids = [n_id for n_id, n in nodos.items() if n.demanda > 0]
    rutas_analizadas = []

    for nodo_final_id in nodos_finales_ids:
        ruta_nodos = next(nx.all_simple_paths(G, source=nodo_fuente_id, target=nodo_final_id))
        perdida_friccion_total_ruta = 0
        for i in range(len(ruta_nodos) - 1):
            tuberia_en_camino = G.edges[ruta_nodos[i], ruta_nodos[i+1]]['data']
            perdida_friccion_total_ruta += tuberia_en_camino.perdida_friccion_hf
        
        perdida_estatica = nodos[nodo_final_id].elevacion - nodos[nodo_fuente_id].elevacion
        carga_total_ruta = perdida_friccion_total_ruta + perdida_estatica
        rutas_analizadas.append({"ruta_str": " -> ".join(ruta_nodos), "carga_total_H": carga_total_ruta})

    ruta_critica_info = max(rutas_analizadas, key=lambda x: x["carga_total_H"])
    
    caudal_total_bomba_lps = sum(demandas_lps.values())

    # 5. PREPARAR DICCIONARIO DE RESULTADOS PARA DEVOLVER
    resultados = {
        "bomba_requerido": {
            "caudal_lps": caudal_total_bomba_lps,
            "carga_m": ruta_critica_info["carga_total_H"],
            "ruta_critica": ruta_critica_info["ruta_str"]
        },
        "resultados_tuberias": [
            {
                "id": t.id,
                "caudal_lps": t.caudal_calculado_m3s * 1000,
                "velocidad_ms": t.velocidad,
                "perdida_hf_m": t.perdida_friccion_hf
            } for t in tuberias.values()
        ]
    }
    
    print(">>> Análisis completado. Devolviendo resultados.")
    return resultados


# --- CREACIÓN DE LA API CON FLASK ---
# Creamos la aplicación servidor
app = Flask(__name__)
CORS(app) 

# Definimos una "ruta" o "endpoint".
# Cuando alguien visite "nuestra-web.com/api/analyze", esta función se ejecutará.
@app.route('/api/analyze', methods=['POST'])
def endpoint_analizar():
    # 1. Recibimos los datos que nos envía el frontend (la interfaz de usuario)
    print("\n>>> Petición recibida en /api/analyze")
    datos_recibidos = request.json
    
    # Extraemos los datos de nodos y tuberías
    datos_nodos = datos_recibidos.get('nodos', [])
    datos_tuberias = datos_recibidos.get('tuberias', [])
    
    # 2. Llamamos a nuestra función de cálculo principal
    resultados_calculados = analizar_red(datos_nodos, datos_tuberias)
    
    # 3. Devolvemos los resultados en formato JSON para que el frontend los entienda
    return jsonify(resultados_calculados)


# --- PUNTO DE ENTRADA PARA EJECUTAR EL SERVIDOR ---
# Esto hace que cuando ejecutemos "python backend/main.py", el servidor se inicie.
if __name__ == '__main__':
    print("Iniciando servidor de cálculo de PipeNet Pro...")
    # El host='0.0.0.0' permite que otras máquinas en la red (o el frontend) se conecten.
app.run(host='0.0.0.0', port=5000, debug=False)