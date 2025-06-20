# ==============================================================================
#        CÓDIGO FINAL Y COMPLETO PARA: backend/main.py (con accesorios)
# ==============================================================================

# --- 0. IMPORTACIONES ---
from models import Nodo, Tuberia
import calculos_hidraulicos as ch
import networkx as nx
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- FUNCIÓN DE CÁLCULO PRINCIPAL ---
def analizar_red(datos_nodos, datos_tuberias):
    """
    Esta función recibe los datos de la red, realiza todos los cálculos
    y devuelve un diccionario con los resultados.
    """
    try:
        print(">>> [ANALIZANDO] Paso 1: Creando objetos desde los datos...")
        # Leemos los datos que envía el frontend, incluyendo la lista de accesorios
        nodos = {n_data['id']: Nodo(n_data['id'], n_data['elevacion'], n_data.get('demanda', 0)) for n_data in datos_nodos}
        tuberias = {t_data['id']: Tuberia(t_data['id'], t_data['nodo_inicio'], t_data['nodo_fin'], t_data['longitud'], t_data['diametro'], t_data['material'], t_data.get('accesorios', [])) for t_data in datos_tuberias}
        
        print(">>> [ANALIZANDO] Paso 2: Calculando caudales...")
        G = nx.DiGraph()
        for t in tuberias.values():
            G.add_edge(t.nodo_inicio, t.nodo_fin, data=t)

        caudales_lps = {t_id: 0.0 for t_id in tuberias}
        demandas_lps = {n_id: n.demanda for n_id, n in nodos.items()}
        nodos_en_orden_inverso = reversed(list(nx.topological_sort(G)))

        nodo_fuente_id = None
        for nodo_id in nodos_en_orden_inverso:
            # Identificamos el nodo fuente (el que no tiene tuberías de entrada)
            if not list(G.predecessors(nodo_id)):
                nodo_fuente_id = nodo_id
            
            caudal_saliente_total = demandas_lps.get(nodo_id, 0)
            for tuberia_saliente_id in G.successors(nodo_id):
                tuberia_obj = G.edges[nodo_id, tuberia_saliente_id]['data']
                caudal_saliente_total += caudales_lps.get(tuberia_obj.id, 0)
            
            predecesores = list(G.predecessors(nodo_id))
            if predecesores:
                nodo_anterior_id = predecesores[0]
                tuberia_entrante = G.edges[nodo_anterior_id, nodo_id]['data']
                caudales_lps[tuberia_entrante.id] = caudal_saliente_total

        for t_id, t in tuberias.items():
            t.caudal_calculado_m3s = caudales_lps.get(t_id, 0) / 1000

        print(">>> [ANALIZANDO] Paso 3: Calculando pérdidas totales (fricción + locales)...")
        for t in tuberias.values():
            if t.caudal_calculado_m3s > 0:
                t.velocidad = ch.calcular_velocidad(t.caudal_calculado_m3s, t.diametro)
                t.reynolds = ch.calcular_reynolds(t.velocidad, t.diametro)
                t.factor_friccion = ch.calcular_factor_friccion(t.reynolds, t.rugosidad_e, t.diametro)
                t.perdida_friccion_hf = ch.calcular_perdida_friccion_hf(t.factor_friccion, t.longitud, t.diametro, t.velocidad)
                
                # Calculamos las pérdidas locales usando la nueva función
                t.perdida_locales_hl = ch.calcular_perdida_locales_hl(t.accesorios, t.velocidad)
                
                # La pérdida total es la suma de ambas
                t.perdida_total = t.perdida_friccion_hf + t.perdida_locales_hl
                
        print(">>> [ANALIZANDO] Paso 4: Encontrando ruta crítica...")
        nodos_finales_ids = [n_id for n_id, n in nodos.items() if n.demanda > 0]
        rutas_analizadas = []

        if not nodo_fuente_id:
            raise ValueError("No se pudo identificar un nodo fuente en la red.")

        for nodo_final_id in nodos_finales_ids:
            if nx.has_path(G, source=nodo_fuente_id, target=nodo_final_id):
                ruta_nodos = next(nx.all_simple_paths(G, source=nodo_fuente_id, target=nodo_final_id))
                
                perdida_total_ruta = 0
                for i in range(len(ruta_nodos) - 1):
                    tuberia_en_camino = G.edges[ruta_nodos[i], ruta_nodos[i+1]]['data']
                    # Usamos la pérdida TOTAL de la tubería para el cálculo
                    perdida_total_ruta += tuberia_en_camino.perdida_total
                
                perdida_estatica = nodos[nodo_final_id].elevacion - nodos[nodo_fuente_id].elevacion
                carga_total_ruta = perdida_total_ruta + perdida_estatica
                rutas_analizadas.append({"ruta_str": " -> ".join(ruta_nodos), "carga_total_H": carga_total_ruta})

        if not rutas_analizadas:
            raise ValueError("No se encontraron rutas válidas a los puntos de demanda.")

        ruta_critica_info = max(rutas_analizadas, key=lambda x: x["carga_total_H"])
        caudal_total_bomba_lps = sum(demandas_lps.values())

        print(">>> [ANALIZANDO] Paso 5: Preparando resultados...")
        resultados = {
            "bomba_requerido": {"caudal_lps": caudal_total_bomba_lps, "carga_m": ruta_critica_info["carga_total_H"], "ruta_critica": ruta_critica_info["ruta_str"]},
            "resultados_tuberias": [
                {
                    "id": t.id,
                    "caudal_lps": t.caudal_calculado_m3s * 1000,
                    "velocidad_ms": t.velocidad,
                    "perdida_hf_m": t.perdida_friccion_hf,
                    "perdida_hl_m": t.perdida_locales_hl,
                    "perdida_total_m": t.perdida_total
                } for t in tuberias.values()
            ]
        }
        return resultados

    except Exception as e:
        print(f"\n!!!!!! ERROR INTERNO EN EL CÁLCULO: {e} !!!!!!\n")
        return {"error": str(e)}

# --- API CON FLASK ---
app = Flask(__name__)
CORS(app)

@app.route('/api/analyze', methods=['POST'])
def endpoint_analizar():
    print("\n>>> Petición recibida en /api/analyze")
    datos_recibidos = request.json
    datos_nodos = datos_recibidos.get('nodos', [])
    datos_tuberias = datos_recibidos.get('tuberias', [])
    
    resultados_calculados = analizar_red(datos_nodos, datos_tuberias)
    
    if "error" in resultados_calculados:
        return jsonify(resultados_calculados), 500
        
    return jsonify(resultados_calculados)

# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    # Usamos debug=False para compatibilidad con el despliegue
    # Para desarrollo local, puedes cambiarlo a True si lo necesitas.
    app.run(host='0.0.0.0', port=5000, debug=False)