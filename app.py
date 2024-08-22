import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import math

# Funciones de diseño

def diseño_flexion_viga(bw, bf=None, h=None, hf=None, d=None, Mu=None, fc=None, fy=None, tipo_viga='rectangular', gamma=0.9):
    if tipo_viga == 'T':
        As = (0.90 * d - math.sqrt(0.81 * d**2 - 1.8 * Mu / (gamma * fc * bf))) / (0.90 * fy)
        a = As * fy / (gamma * fc * bf)
        if a <= hf:
            return {"Area de Acero As": As}
        else:
            As1 = (0.85 * fc * hf * (bf - bw)) / fy
            Mn1 = gamma * As1 * fy * (d - hf / 2)
            Mn2 = Mu - Mn1
            As2 = (0.90 * d - math.sqrt(0.81 * d**2 - 1.8 * Mn2 / (gamma * fc * bw))) / (0.90 * fy)
            As_total = As1 + As2
            return {"Area de Acero As": As_total}
    
    elif tipo_viga == 'rectangular':
        ro_b = (gamma * 0.85 * (fc / fy) * (0.003 / (0.003 + (fy / 200000))))
        ro_max = 0.75 * ro_b
        As_max = ro_max * bw * d
        phi_Mmax = gamma * As_max * fy * (d - (As_max * fy) / (2 * gamma * fc * bw))
        As_min = max(math.sqrt(fc) * bw * d / (4 * fy), (1.4 * bw * d) / fy)
        if Mu > phi_Mmax:
            M2 = (Mu - phi_Mmax) / 0.9
            As2 = M2 / (fy * (d - hf))
            As = As_max + As2
        else:
            As = max(0.9 * d - math.sqrt(0.81 * d**2 - (1.8 * Mu) / (gamma * fc * bw)) / (0.9 * fy), As_min)
        return {"Area de Acero As": As}

    elif tipo_viga == 'H':
        I = (bw * h**3) / 12 - (bf * hf**3) / 12
        c = h / 2
        sigma_flexion = Mu * c / I
        As = Mu / (fy * c)
        return {"Esfuerzo de Flexión": sigma_flexion, "Area de Acero As": As}

def diseño_cortante_T(bw, d, fc, fy, Vu, d_estribo, recub, Nu, phi=0.75, fy_limite=420):
    lambda_factor = 0.7 if fy > fy_limite else 1.0
    ro_v = Nu / (bw * d)
    Ag = bw * (d + recub)
    Vc = phi * 0.66 * lambda_factor * ro_v**(1/3) * math.sqrt(fc) * Ag
    if Vu > phi * Vc:
        necesita_estribos = True
        Vs = (Vu - phi * Vc) / phi
        Av = (d_estribo**2) * math.pi / 4
        s = min(d / 2, Vs / (0.33 * math.sqrt(fc) * bw * d))
    else:
        necesita_estribos = False
        Av = 0
        s = 0
    return {
        "Necesita_estribos": necesita_estribos,
        "Area de Estribos Av": Av,
        "Separacion s": s
    }

def diseño_torsion_T(bw, bf, h, hf, Vu, Tu, fc, fy, recub, phi=0.75, lambda_factor=1.0):
    d = h - recub
    Acp = bw * h + (bf - bw) * hf
    Pcp = 2 * (bw + h)
    Tth = phi * 0.083 * lambda_factor * math.sqrt(fc) * Acp
    if Tu > Tth:
        necesita_refuerzo_torsion = True
        theta = math.radians(45)
        Aoh = (bw - 2 * recub) * (h - 2 * recub)
        Ao = 0.85 * Aoh
        Ph = 2 * (bw - 2 * recub) + 2 * (h - 2 * recub)
        At = Tu * Ph / (phi * 2 * Ao * fy * math.tan(theta))
        Av = (Vu / bw * d) + (Tu * Ph / (1.7 * Ao * math.sqrt(fc)))
        s_max = min(Ph / 8, 0.3)
        if Av / s_max >= 0.062 * math.sqrt(fc) * bw / fy:
            As_transversal = Av / s_max
            spacing_s = s_max
        else:
            As_transversal = 0.062 * math.sqrt(fc) * bw / fy
            spacing_s = d / 4
    else:
        necesita_refuerzo_torsion = False
        As_transversal = 0
        spacing_s = 0
    return {
        "Necesita refuerzo a torsion": necesita_refuerzo_torsion,
        "Area de Acero As": As_transversal,
        "Espaciamiento s": spacing_s
    }

# Función para cargar archivo CSV
def cargar_csv():
    archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if archivo:
        try:
            datos = pd.read_csv(archivo)
            return datos
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo CSV: {e}")
            return None

# Función para ejecutar el diseño
def ejecutar_diseno(parametros, solicitaciones=None):
    resultados = []

    if solicitaciones is None:
        # Análisis puntual
        if parametros.get('Mu') is not None:
            # Filtrar solo los argumentos relevantes para diseño_flexion_viga
            parametros_flexion = {k: parametros[k] for k in ['bw', 'bf', 'h', 'hf', 'd', 'Mu', 'fc', 'fy', 'tipo_viga']}
            resultado_flexion = diseño_flexion_viga(**parametros_flexion)
            entry_resultado_flexion.delete(0, tk.END)
            entry_resultado_flexion.insert(0, f"{resultado_flexion['Area de Acero As']:.2f} m^2")

        if parametros.get('Vu') is not None:
            # Filtrar solo los argumentos relevantes para diseño_cortante_T
            parametros_cortante = {k: parametros[k] for k in ['bw', 'd', 'fc', 'fy', 'Vu', 'd_estribo', 'recub', 'Nu']}
            resultado_cortante = diseño_cortante_T(**parametros_cortante)
            entry_resultado_cortante.delete(0, tk.END)
            entry_resultado_cortante.insert(0, f"{resultado_cortante['Area de Estribos Av']:.2f} m^2")

        if parametros.get('Tu') is not None:
            # Filtrar solo los argumentos relevantes para diseño_torsion_T
            parametros_torsion = {k: parametros[k] for k in ['bw', 'bf', 'h', 'hf', 'Vu', 'Tu', 'fc', 'fy', 'recub']}
            resultado_torsion = diseño_torsion_T(**parametros_torsion)
            entry_resultado_torsion.delete(0, tk.END)
            entry_resultado_torsion.insert(0, f"{resultado_torsion['Area de Acero As']:.2f} m^2")

    else:
        # Análisis con CSV
        for idx, fila in solicitaciones.iterrows():
            parametros_actuales = parametros.copy()
            for solicitacion in ['Mu', 'Vu', 'Tu']:
                if solicitacion in fila:
                    parametros_actuales[solicitacion] = fila[solicitacion]
            fila['Area de Acero As Flexion'] = diseño_flexion_viga(**{k: parametros_actuales[k] for k in ['bw', 'bf', 'h', 'hf', 'd', 'Mu', 'fc', 'fy', 'tipo_viga']}).get('Area de Acero As', None)
            fila['Area de Acero As Cortante'] = diseño_cortante_T(**{k: parametros_actuales[k] for k in ['bw', 'd', 'fc', 'fy', 'Vu', 'd_estribo', 'recub', 'Nu']}).get('Area de Estribos Av', None)
            fila['Area de Acero As Torsion'] = diseño_torsion_T(**{k: parametros_actuales[k] for k in ['bw', 'bf', 'h', 'hf', 'Vu', 'Tu', 'fc', 'fy', 'recub']}).get('Area de Acero As', None)
            resultados.append(fila)

        df_resultados = pd.DataFrame(resultados)
        guardar_csv(df_resultados)

# Función para guardar resultados en CSV
def guardar_csv(df_resultados):
    archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if archivo:
        df_resultados.to_csv(archivo, index=False)
        messagebox.showinfo("Guardar CSV", "Resultados guardados exitosamente.")

# Creación de la interfaz
def crear_campos_geometria(geometria_ventana, parametros):
    for widget in geometria_ventana.winfo_children():
        widget.destroy()

    tk.Label(geometria_ventana, text="Definiendo Geometría").pack(pady=5)
    
    # Campos generales para todos los tipos
    def crear_campo(label_text, default_value, key):
        tk.Label(geometria_ventana, text=label_text).pack()
        entry = tk.Entry(geometria_ventana)
        entry.pack()
        entry.insert(0, parametros.get(key, default_value))
        return entry

    entry_bw = crear_campo("Ancho del alma (bw)", 0.3, 'bw')
    entry_h = crear_campo("Altura total (h)", 0.5, 'h')
    entry_d = crear_campo("Altura útil (d)", 0.45, 'd')

    if parametros['tipo_viga'] in ['t', 'h']:
        entry_bf = crear_campo("Ancho de la mesa (bf)", 0.6, 'bf')
        entry_hf = crear_campo("Altura de la mesa (hf)", 0.1, 'hf')
    else:
        entry_bf = entry_hf = None

    def actualizar_geometria():
        parametros['bw'] = float(entry_bw.get())
        parametros['h'] = float(entry_h.get())
        parametros['d'] = float(entry_d.get())
        if entry_bf and entry_hf:
            parametros['bf'] = float(entry_bf.get())
            parametros['hf'] = float(entry_hf.get())
        geometria_ventana.destroy()

    tk.Button(geometria_ventana, text="Actualizar Geometría", command=actualizar_geometria).pack(pady=10)

def crear_interfaz():
    root = tk.Tk()
    root.title("Diseño de Vigas")
    root.geometry("500x500")  # Tamaño de la ventana

    global entry_resultado_flexion, entry_resultado_cortante, entry_resultado_torsion
    global datos_cargados, etiqueta_geometria, geometria_seleccionada
    datos_cargados = None  # Variable para almacenar el archivo CSV cargado
    geometria_seleccionada = tk.StringVar(value="Rectangular")
    parametros = {
        'bw': 0.3,
        'bf': 0.6,
        'h': 0.5,
        'hf': 0.1,
        'd': 0.45,
        'Mu': None,
        'Vu': None,
        'Tu': None,
        'fc': 25,
        'fy': 420,
        'd_estribo': 0.01,
        'recub': 0.04,
        'Nu': 300,
        'tipo_viga': 'rectangular'
    }

    def actualizar_etiqueta_geometria(event):
        parametros['tipo_viga'] = geometria_seleccionada.get().lower()
        etiqueta_geometria.config(text=f"Geometría Definida: {geometria_seleccionada.get()}")

    # Menú desplegable para seleccionar geometría
    tk.Label(root, text="Seleccione la geometría:").grid(row=0, column=0, padx=5, pady=5, columnspan=3)
    opciones_geometria = ['Rectangular', 'T', 'H']
    combo_geometria = ttk.Combobox(root, values=opciones_geometria, state="readonly", textvariable=geometria_seleccionada)
    combo_geometria.grid(row=1, column=0, padx=5, pady=5, columnspan=3)
    combo_geometria.bind("<<ComboboxSelected>>", actualizar_etiqueta_geometria)

    # Etiqueta para mostrar la geometría seleccionada
    etiqueta_geometria = tk.Label(root, text="Geometría: Rectangular")
    etiqueta_geometria.grid(row=2, column=0, padx=5, pady=5, columnspan=3)

    # Botón para definir parámetros geométricos
    tk.Button(root, text="Definir Parámetros Geométricos", command=lambda: crear_campos_geometria(tk.Toplevel(root), parametros)).grid(row=3, column=0, padx=5, pady=5, columnspan=3)

    # Creación del frame para las entradas de solicitaciones y resultados
    frame = tk.Frame(root)
    frame.grid(row=4, column=0, padx=10, pady=10, columnspan=3)

    # Columnas de solicitaciones
    tk.Label(frame, text="Solicitación de Flexión (Mu):").grid(row=0, column=0)
    tk.Label(frame, text="Solicitación de Cortante (Vu):").grid(row=0, column=1)
    tk.Label(frame, text="Solicitación de Torsión (Tu):").grid(row=0, column=2)

    entry_flexion = tk.Entry(frame)
    entry_flexion.grid(row=1, column=0)
    entry_cortante = tk.Entry(frame)
    entry_cortante.grid(row=1, column=1)
    entry_torsion = tk.Entry(frame)
    entry_torsion.grid(row=1, column=2)

    # Resultados de solicitaciones puntuales
    tk.Label(frame, text="Resultado Área Flexión:").grid(row=2, column=0)
    tk.Label(frame, text="Resultado Área Cortante:").grid(row=2, column=1)
    tk.Label(frame, text="Resultado Área Torsión:").grid(row=2, column=2)

    entry_resultado_flexion = tk.Entry(frame)
    entry_resultado_flexion.grid(row=3, column=0)
    entry_resultado_cortante = tk.Entry(frame)
    entry_resultado_cortante.grid(row=3, column=1)
    entry_resultado_torsion = tk.Entry(frame)
    entry_resultado_torsion.grid(row=3, column=2)

    # Menús desplegables para seleccionar las columnas del CSV
    columna_flexion = tk.StringVar()
    columna_cortante = tk.StringVar()
    columna_torsion = tk.StringVar()

    tk.Label(frame, text="Columna Flexión:").grid(row=4, column=0)
    tk.Label(frame, text="Columna Cortante:").grid(row=4, column=1)
    tk.Label(frame, text="Columna Torsión:").grid(row=4, column=2)

    combo_flexion = ttk.Combobox(frame, textvariable=columna_flexion)
    combo_flexion.grid(row=5, column=0)
    combo_cortante = ttk.Combobox(frame, textvariable=columna_cortante)
    combo_cortante.grid(row=5, column=1)
    combo_torsion = ttk.Combobox(frame, textvariable=columna_torsion)
    combo_torsion.grid(row=5, column=2)

    def cargar_y_configurar_csv():
        global datos_cargados
        datos_cargados = cargar_csv()
        if datos_cargados is not None:
            columnas = datos_cargados.columns.tolist()
            combo_flexion['values'] = columnas
            combo_cortante['values'] = columnas
            combo_torsion['values'] = columnas

    def ejecutar_con_solicitacion_unica():
        parametros['Mu'] = float(entry_flexion.get()) if entry_flexion.get() else None
        parametros['Vu'] = float(entry_cortante.get()) if entry_cortante.get() else None
        parametros['Tu'] = float(entry_torsion.get()) if entry_torsion.get() else None
        ejecutar_diseno(parametros)

    def ejecutar_con_csv():
        global datos_cargados
        if datos_cargados is None:
            messagebox.showerror("Error", "Debe cargar un archivo CSV primero.")
            return

        solicitaciones = pd.DataFrame()
        if columna_flexion.get():
            solicitaciones['Mu'] = datos_cargados[columna_flexion.get()]
        if columna_cortante.get():
            solicitaciones['Vu'] = datos_cargados[columna_cortante.get()]
        if columna_torsion.get():
            solicitaciones['Tu'] = datos_cargados[columna_torsion.get()]
        ejecutar_diseno(parametros, solicitaciones)

    # Botón para cargar archivos CSV y configurar menús desplegables
    tk.Button(root, text="Cargar CSV", command=cargar_y_configurar_csv).grid(row=6, column=0, padx=5, pady=5, columnspan=3, sticky="n")
    # Botón para ejecutar diseño con solicitaciones puntuales
    tk.Button(root, text="Ejecutar Diseño (Solicitaciones Puntuales)", command=ejecutar_con_solicitacion_unica).grid(row=7, column=0, padx=5, pady=5, columnspan=3, sticky="n")
    # Botón para ejecutar diseño con CSV
    tk.Button(root, text="Ejecutar Diseño con CSV", command=ejecutar_con_csv).grid(row=8, column=0, padx=5, pady=5, columnspan=3, sticky="n")

    root.mainloop()

# Iniciar la interfaz
crear_interfaz()