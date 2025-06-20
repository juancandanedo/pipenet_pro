# ==============================================================================
#        CONTENIDO COMPLETO Y FINAL PARA: backend/main.py (FASE 1)
# ==============================================================================

# --- 0. IMPORTACIONES ---
from models import Nodo, Tuberia
import calculos_hidraulicos as ch
import networkx as nx

# --- 1. CREAMOS NUESTRAS PIEZAS ---
print("Paso 1: Creando las piezas de nuestra red...")
nodo_bomba = Nodo(id_nodo="Bomba", elevacion=100)
nodo_union = Nodo(id_nodo="Union", elevacion=102)
nodo_rociador1 = Nodo(id_nodo="Rociador1", elevacion=105, demanda=15.0)
nodo_rociador2 = Nodo(id_nodo="Rociador2", elevacion=104, demanda=20.0)

tuberia1 = Tuberia(id_tuberia="T1", nodo_inicio=nodo_bomba, nodo_fin=nodo_union, longitud_m=50, diametro_mm=75, material="Acero")
tuberia2 = Tuberia(id_tuberia="T2", nodo_inicio=nodo_union, nodo_fin=nodo_rociador1, longitud_m=30, diametro_mm=50, material="PVC")
tuberia3 = Tuberia(id_tuberia="T3", nodo_inicio=nodo_union, nodo_fin=nodo_rociador2, longitud_m=40, diametro_mm=50, material="PVC")

# Guardamos los objetos en diccionarios para encontrarlos fácilmente por su ID
nodos = {n.id: n for n in [nodo_bomba, nodo_union, nodo_rociador1, nodo_rociador2]}
tuberias = {t.id: t for t in [tuberia1, tuberia2, tuberia3]}

# --- 2. CÁLCULO DE CAUDALES ---
print("\nPaso 2: Calculando los caudales...")
G = nx.DiGraph()
for t in tuberias.values():
    G.add_edge(t.nodo_inicio.id, t.nodo_fin.id, data=t)

caudales_lps = {t_id: 0.0 for t_id in tuberias}
demandas_lps = {n_id: n.demanda for n_id, n in nodos.items()}

nodos_en_orden_inverso = reversed(list(nx.topological_sort(G)))

for nodo_id in nodos_en_orden_inverso:
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

print("¡Caudales calculados!")

# --- 3. CÁLCULO DE PÉRDIDAS DE ENERGÍA ---
print("\nPaso 3: Calculando las pérdidas por fricción...")
for t in tuberias.values():
    if t.caudal_calculado_m3s > 0:
        t.velocidad = ch.calcular_velocidad(t.caudal_calculado_m3s, t.diametro)
        t.reynolds = ch.calcular_reynolds(t.velocidad, t.diametro)
        t.factor_friccion = ch.calcular_factor_friccion(t.reynolds, t.rugosidad_e, t.diametro)
        t.perdida_friccion_hf = ch.calcular_perdida_friccion_hf(t.factor_friccion, t.longitud, t.diametro, t.velocidad)
print("¡Pérdidas calculadas!")

# --- 4. MOSTRAR RESULTADOS INTERMEDIOS ---
print("\n--- RESULTADOS DETALLADOS POR TUBERÍA ---")
for t in tuberias.values():
    print(t)

# --- 5. ¡NUEVO! ENCONTRAR LA RUTA CRÍTICA ---
print("\n--- PASO FINAL: ANÁLISIS DEL SISTEMA Y RUTA CRÍTICA ---")

# Identificamos el inicio y los finales de la red
nodo_inicial_id = "Bomba"
nodos_finales_ids = ["Rociador1", "Rociador2"]
rutas_analizadas = []

# Analizamos cada ruta desde la bomba hasta cada rociador
for nodo_final_id in nodos_finales_ids:
    # `networkx` nos da el camino de nodos
    ruta_nodos = next(nx.all_simple_paths(G, source=nodo_inicial_id, target=nodo_final_id))
    
    perdida_friccion_total_ruta = 0
    tuberias_en_ruta = []
    
    # Recorremos el camino para sumar las pérdidas de sus tuberías
    for i in range(len(ruta_nodos) - 1):
        nodo_a = ruta_nodos[i]
        nodo_b = ruta_nodos[i+1]
        tuberia_en_camino = G.edges[nodo_a, nodo_b]['data']
        perdida_friccion_total_ruta += tuberia_en_camino.perdida_friccion_hf
        tuberias_en_ruta.append(tuberia_en_camino.id)
    
    # Calculamos la altura que hay que subir
    nodo_inicio = nodos[nodo_inicial_id]
    nodo_final = nodos[nodo_final_id]
    perdida_estatica = nodo_final.elevacion - nodo_inicio.elevacion
    
    # La carga total es la suma de la fricción más la altura a subir
    carga_total_ruta = perdida_friccion_total_ruta + perdida_estatica
    
    # Guardamos los resultados de esta ruta
    rutas_analizadas.append({
        "ruta": " -> ".join(ruta_nodos),
        "tuberias": tuberias_en_ruta,
        "perdida_friccion": perdida_friccion_total_ruta,
        "perdida_estatica": perdida_estatica,
        "carga_total_H": carga_total_ruta
    })

# Buscamos la ruta con la mayor carga total
ruta_critica = max(rutas_analizadas, key=lambda x: x["carga_total_H"])

# Obtenemos el caudal total que debe mover la bomba
caudal_total_bomba_lps = tuberias["T1"].caudal_calculado_m3s * 1000

print("\n--- ESPECIFICACIÓN DEL SISTEMA DE BOMBEO ---")
print(f"\nCaudal total requerido en la bomba (Q): {caudal_total_bomba_lps:.2f} l/s")
print(f"\nLa ruta crítica (la más desfavorable) es: {ruta_critica['ruta']}")
print(f"  - Pérdida por fricción en esta ruta: {ruta_critica['perdida_friccion']:.2f} m")
print(f"  - Altura a vencer (estática): {ruta_critica['perdida_estatica']:.2f} m")
print("--------------------------------------------------")
print(f"CARGA DINÁMICA TOTAL REQUERIDA (H): {ruta_critica['carga_total_H']:.2f} m")
print("--------------------------------------------------")
print("\n¡Debes seleccionar una bomba que pueda entregar "
      f"{caudal_total_bomba_lps:.2f} l/s a una presión equivalente a {ruta_critica['carga_total_H']:.2f} metros de altura!")