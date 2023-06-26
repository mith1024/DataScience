#---------------------IMPORT THE LIBRARIES--------------------------------
import warnings 
warnings.filterwarnings('ignore')
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
def find_critical_path(df):
    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_node(row['Nombre actividad'], duration=row['Duración'])

    for _, row in df.iterrows():
        predecesores = row['Predecesores']
        if predecesores:
            predecesores = predecesores.split(',')
            for predecesor in predecesores:
                G.add_edge(predecesor, row['Nombre actividad'], weight=0)

    earliest_start = {}
    earliest_finish = {}
    for node in nx.topological_sort(G):
        duration = G.nodes[node]['duration']
        es = max([earliest_finish.get(pred, 0) for pred in G.predecessors(node)], default=0)
        ef = es + duration
        earliest_start[node] = es
        earliest_finish[node] = ef

    latest_start = {}
    latest_finish = {}
    for node in reversed(list(nx.topological_sort(G))):
        duration = G.nodes[node]['duration']
        lf = min([latest_start.get(succ, earliest_finish[succ]) for succ in G.successors(node)], default=earliest_finish[node])
        ls = lf - duration
        latest_start[node] = ls
        latest_finish[node] = lf

    duration_project = max(earliest_finish.values())

    critical_path = []
    for node in G.nodes:
        if earliest_start[node] == latest_start[node] and earliest_finish[node] == latest_finish[node]:
            critical_path.append(node)

    return critical_path
def draw_pert_graph(df):
    # Crear el gráfico dirigido acíclico (DAG)
    G = nx.DiGraph()

    # Crear los nodos del gráfico con sus duraciones
    node_data = {}
    for _, row in df.iterrows():
        node_data[row['Nombre actividad']] = {'duration': row['Duración']}
    G.add_nodes_from(node_data.items())

    # Crear las aristas del gráfico
    for _, row in df.iterrows():
        predecesores = row['Predecesores']
        if predecesores:
            predecesores = predecesores.split(',')
            for predecesor in predecesores:
                duration = node_data[predecesor]['duration']
                G.add_edge(predecesor, row['Nombre actividad'], weight=duration)

    # Calcular los tiempos tempranos (early start, early finish)
    earliest_start = {}
    earliest_finish = {}
    for node in nx.topological_sort(G):
        duration = G.nodes[node]['duration']
        es = max([earliest_finish.get(pred, 0) for pred in G.predecessors(node)], default=0)
        ef = es + duration
        earliest_start[node] = es
        earliest_finish[node] = ef

    # Calcular los tiempos tardíos (late start, late finish)
    latest_start = {}
    latest_finish = {}
    for node in reversed(list(nx.topological_sort(G))):
        duration = G.nodes[node]['duration']
        lf = min([latest_start.get(succ, earliest_finish[succ]) for succ in G.successors(node)], default=earliest_finish[node])
        ls = lf - duration
        latest_start[node] = ls
        latest_finish[node] = lf

    # Calcular la duración total del proyecto
    duration_project = max(earliest_finish.values())

    # Crear el DataFrame de resultados
    result_df = pd.DataFrame(columns=['Nombre actividad', 'Duración', 'Tiempos Tempranos', 'Tiempos Tardíos'])

    # Agregar los resultados al DataFrame
    start_times = []
    end_times = []
    for node in sorted(G.nodes):
        es = earliest_start[node]
        ef = earliest_finish[node]
        ls = latest_start[node]
        lf = latest_finish[node]
        duration = G.nodes[node]['duration']
        result_df.loc[len(result_df)] = [node, duration, f"{es}|{ef}", f"{ls}|{lf}"]
        start_times.append(es)
        end_times.append(ef)

    # Agregar las columnas de "Inicio" y "Fin" al DataFrame de resultados
    result_df['Inicio'] = start_times
    result_df['Fin'] = end_times


    def generar_grafico_PERT():
        # Dibujar el gráfico PERT
        pos = nx.shell_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=200, node_color='lightblue')
        nx.draw_networkx_labels(G, pos)

        # Dibujar las aristas del gráfico, resaltando la ruta crítica en rojo
        for edge in G.edges:
            u, v = edge
            duration = G.edges[u, v]['weight']
            destination_earliest_start = earliest_start[v]
            if duration + earliest_start[u] == destination_earliest_start:
                nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], arrows=True, edge_color='red')
            else:
                nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], arrows=True, edge_color='blue')

        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.title("Diagrama PERT")
        plt.axis('off')

        # Devolver la figura en lugar de mostrarla directamente
        return plt.gcf()
    figura_pert = generar_grafico_PERT()
    return result_df,duration_project,figura_pert
