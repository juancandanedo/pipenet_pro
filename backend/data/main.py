# --- 0. IMPORTACIONES ---
# Ahora importamos también nuestras nuevas fórmulas
from models import Nodo, Tuberia
import calculos_hidraulicos as ch # ch es un apodo para "calculos_hidraulicos"
import networkx as nx

# --- 1. CREAMOS NUESTRAS PIEZAS (CON MÁS DETALLES) ---
print("Paso 1: Creando las piezas de nuestra red...")

# Creamos los nodos como antes
nodo_bomba = Nodo(id_nodo="Bomba", elevacion=100)
nodo_union = Nodo(id_nodo="Union", elevacion=102)
nodo_rociador1 = Nodo(id_nodo="Rociador1", elevacion=105, demanda=15.0) # 15 l/s
nodo_rociador2 = Nodo(id_nodo="Rociador2", elevacion=104, demanda=20.0) # 20 l/s

# Ahora creamos las tuberías con sus nuevos datos: Longitud, Diámetro en mm y Material
tuberia1 = Tuberia(id_tuberia="T1", nodo_inicio=nodo_bomba, nodo_fin=nodo_union, longitud_m=50, diametro_mm=75, material="Acero")
tuberia2 = Tuberia(id_tuberia="T2", nodo_inicio=nodo_union, nodo_fin=nodo_rociador1, longitud_m=30, diametro_mm=50, material="PVC")
tuberia3 = Tuberia(id_tuberia="T3", nodo_inicio=nodo_union, nodo_fin=nodo_rociador2, longitud_m=40, diametro_mm=50, material="PVC")

nodos = [nodo_bomba, nodo_union, nodo_rociador1, nodo_rociador2]
tuberias = [tuberia1, tuberia2, tuberia3]

# --- 2. CÁLCULO DE CAUDALES (ESTO NO CAMBIA) ---
print("\nPaso 2: Calculando los caudales...")
G = nx.DiGraph()
for t in tuberias:
    G.add_edge(t.nodo_inicio.id, t.nodo_fin.id, data=t)

caudales_lps = {t.id: 0.0 for t in tuberias}
demandas_lps = {n.id: n.demanda for n in nodos}

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

for t in tuberias:
    # Guardamos el caudal en la unidad correcta (m³/s)
    t.caudal_calculado_m3s = caudales_lps[t.id] / 1000

print("¡Caudales calculados!")

# --- 3. ¡NUEVO! CÁLCULO DE PÉRDIDAS DE ENERGÍA ---
print("\nPaso 3: Calculando las pérdidas por fricción...")

for t in tuberias:
    # Solo calculamos si hay agua pasando por la tubería
    if t.caudal_calculado_m3s > 0:
        # Usamos nuestras fórmulas una por una. ¡Como una receta de cocina!
        # 1. Calcular velocidad
        t.velocidad = ch.calcular_velocidad(t.caudal_calculado_m3s, t.diametro)
        
        # 2. Calcular Reynolds
        t.reynolds = ch.calcular_reynolds(t.velocidad, t.diametro)
        
        # 3. Calcular factor de fricción
        t.factor_friccion = ch.calcular_factor_friccion(t.reynolds, t.rugosidad_e, t.diametro)
        
        # 4. Calcular pérdida hf
        t.perdida_friccion_hf = ch.calcular_perdida_friccion_hf(t.factor_friccion, t.longitud, t.diametro, t.velocidad)

print("¡Pérdidas calculadas!")

# --- 4. MOSTRAR RESULTADOS FINALES ---
print("\n--- RESULTADOS FINALES DETALLADOS ---")
for t in tuberias:
    print(t)