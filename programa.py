import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os

# Diccionario de áreas de barras en mm²
barras = {
    2: 32,
    3: 71,
    4: 129,
    5: 199,
    6: 284,
    7: 387,
    8: 510,
    9: 645,
    10: 819,
    11: 1006,
    14: 1452,
    18: 2581
}

# Función para recibir los parámetros de entrada del usuario
# Modificar input_parametros() para obtener los datos desde el formulario POST de Flask
def input_parametros(request_form):
    """
    Recibe los parámetros desde el formulario HTML usando request.form en Flask.
    """
    tipo_concreto = request_form['tipo_concreto'].strip().lower()
    b = float(request_form['b'])
    h = float(request_form['h'])
    recub = float(request_form['recub'])
    fc = float(request_form['fc'])
    fyt = float(request_form['fyt'])
    fy = float(fyt)
    phi_cortante = 0.75
    phi_momento = 0.9
    Es = 200000  # Módulo de elasticidad del acero (en MPa)
    gamma = 0.85
    R = float(request_form['R'])
    
    return tipo_concreto, b, h, recub, fc, fyt, fy, phi_cortante, phi_momento, Es, gamma, R

# Función para leer y seleccionar columnas del CSV
def seleccionar_columnas(csv_path, x_col, momento_col, cortante_col):
    """
    Lee el archivo CSV y selecciona las columnas de interés.
    """
    df = pd.read_csv(csv_path)

    # Asegurarnos de que estamos usando los nombres tal como están en el CSV
    columnas_df = {col.lower(): col for col in df.columns}

    # Normalizar las columnas ingresadas por el usuario (convertir a minúsculas)
    x_col_normalized = columnas_df.get(x_col.lower())
    momento_col_normalized = columnas_df.get(momento_col.lower())
    cortante_col_normalized = columnas_df.get(cortante_col.lower())

    # Validar que se encontraron las columnas
    if x_col_normalized is None:
        raise KeyError(f"Columna X '{x_col}' no encontrada.")
    if momento_col_normalized is None:
        raise KeyError(f"Columna Momento '{momento_col}' no encontrada.")
    if cortante_col_normalized is None:
        raise KeyError(f"Columna Cortante '{cortante_col}' no encontrada.")

    # Extraer las columnas selec# Función para leer y seleccionar columnas del CSV
# Función para leer y seleccionar columnas del CSV
def seleccionar_columnas(csv_path, x_col, momento_col, cortante_col):
    """
    Lee el archivo CSV y selecciona las columnas de interés.
    """
    df = pd.read_csv(csv_path)

    # Normalizamos los nombres de todas las columnas a minúsculas
    df.columns = df.columns.str.lower()

    # Normalizamos las columnas seleccionadas
    x_col_normalized = x_col.lower()
    momento_col_normalized = momento_col.lower()
    cortante_col_normalized = cortante_col.lower()

    # Depuración: imprimir los nombres de las columnas seleccionadas
    print(f"Columnas seleccionadas: X = {x_col_normalized}, Momento = {momento_col_normalized}, Cortante = {cortante_col_normalized}")

    # Extraer las columnas seleccionadas
    x = df[x_col_normalized].values
    momento = df[momento_col_normalized].values
    cortante = df[cortante_col_normalized].values
    
    # Crear un DataFrame con las columnas seleccionadas
    selected_df = pd.DataFrame({
        'x': x,
        'momento': momento,
        'cortante': cortante
    })
    
    return selected_df, x_col_normalized





def procesar_datos(df, x_col, rango=2):
    """
    Agrupa los datos de Momento y Cortante en intervalos de longitud `rango` metros.
    """
    # Depuración: imprimir la columna de X que estamos usando
    print(f"Usando la columna {x_col} para procesar los datos")

    momento_reducido = {}
    cortante_reducido = {}
    
    # Encontrar el mínimo y máximo de la coordenada X
    min_x = df[x_col].min()
    max_x = df[x_col].max()

    # Agrupar los datos en intervalos
    current_x1 = min_x
    while current_x1 < max_x:
        current_x2 = current_x1 + rango
        
        # Filtrar los datos en el intervalo actual
        datos_intervalo = df[(df[x_col] >= current_x1) & (df[x_col] < current_x2)]
        
        if not datos_intervalo.empty:
            # Obtener los máximos valores de momento y cortante en el intervalo
            max_momento = np.abs(datos_intervalo['momento']).max()
            max_cortante = np.abs(datos_intervalo['cortante']).max()
            
            # Guardar los resultados en los diccionarios
            key = f"Entre {current_x1:.1f} y {current_x2:.1f}"
            momento_reducido[key] = max_momento
            cortante_reducido[key] = max_cortante
        
        current_x1 = current_x2
    
    return momento_reducido, cortante_reducido



def graficar_resultados(df_seleccionado):
    """
    Función para graficar solo los valores originales de momento y cortante.
    Se guarda el gráfico como archivo PNG en la carpeta 'static'.
    """
    # Extraer los valores originales
    x = df_seleccionado['x'].values
    momento_original = df_seleccionado['momento'].values
    cortante_original = df_seleccionado['cortante'].values

    # Crear el gráfico para los valores originales (momento y cortante)
    plt.figure(figsize=(10, 6))
    plt.plot(x, momento_original, label='Momento Original', linestyle='-')
    plt.plot(x, cortante_original, label='Cortante Original', linestyle='-')
    plt.title('Valores Originales de Momento y Cortante')
    plt.xlabel('Distancia (m)')
    plt.ylabel('Valores')
    plt.legend()
    plt.grid(True)

    # Guardar el gráfico en la carpeta 'static'
    graph_path = os.path.join("static", 'momento_cortante_original.png')
    plt.savefig(graph_path)
    plt.close()

    # Asegurarse de retornar siempre la ruta de la imagen
    return graph_path

# Calcular áreas mínimas de cortante y momento
def calcular_areas_minimas(b, h, recub, fc, fy, fyt):
    """
    Calcula las áreas mínimas requeridas para cortante y momento.
    """
    d = h - recub  # Altura útil
    
    # Área mínima de cortante
    s_max = d / 2
    Av_min1 = 1 / 16 * (fc ** 0.5) * b * s_max / fyt
    Av_min2 = 0.35 * b * s_max / fyt
    Av_min = max(Av_min1, Av_min2)

    # Área mínima de momento
    As_min1 = (fc ** 0.5) / (4 * fy) * b * d
    As_min2 = 1.4 * b * d / fy
    As_min = max(As_min1, As_min2)

    print(f"Área mínima para cortante (Av_min): {round(Av_min * 1000**2, 0)} mm²")
    print(f"Área mínima para momento (As_min): {round(As_min * 1000**2, 0)} mm²")
    
    return Av_min, As_min

def seleccionar_numero_barra(Av_min, numero_barra_cortante, numero_barra_momento):
    """
    Verifica que el número de barra seleccionado para cortante cumpla con el área mínima requerida.
    """
    # Calcular el área para el cortante
    area_cortante = barras[numero_barra_cortante] * 2 / 1000**2

    # Verificar si el área de cortante cumple con el mínimo Av_min
    if area_cortante < Av_min:
        raise ValueError(f"El número de barra #{numero_barra_cortante} no cumple con el área mínima requerida para cortante.")

    print(f"Barra seleccionada para cortante: #{numero_barra_cortante} con área {area_cortante * 1000**2:.2f} mm²")
    print(f"Barra seleccionada para momento: #{numero_barra_momento}")

    return numero_barra_cortante, numero_barra_momento


# Calcular diseño a cortante
def calcular_cortante(b, h, recub, fc, fyt, Vu, phi, tipo_concreto, numero):
    """
    Función para calcular el diseño a cortante con refuerzos de acero siguiendo la lógica proporcionada.
    """
    d = h - recub  # Altura útil
    lambda_ = 0.75 if tipo_concreto == "si" else 1  # Si el concreto es liviano o no
    s_max = d / 2  # Espaciamiento máximo
    
    # Calcular el área mínima de refuerzo
    Av_min1 = 1 / 16 * (fc ** 0.5) * b * s_max / fyt
    Av_min2 = 0.35 * b * s_max / fyt
    Av_min = max(Av_min1, Av_min2)

    # Obtener el área de la barra seleccionada y calcular el área resistente
    Area = barras[numero]
    Area_resistente = Area * 2 / 1000**2  # Para estribos dobles

    print(f"Solicitación a cortante: {Vu} kN")
    Vu=Vu/1000
    # Calcular la capacidad de cortante del concreto
    Vc = fc ** 0.5 / 6 * b * d * lambda_
    Vc_phi = phi * Vc
    print("Separacion maxima [m]: " + str(round(s_max,2)))
    Vmax=phi*(1/6*fc**0.5*b*d+2/3*fc**0.5*b*d)
    if Vu>Vmax:
        return "Aumentar seccion"
    else:

        # Caso: el concreto resiste sin refuerzo
        if Vc_phi*0.5>=Vu:
            print("El concreto resiste sin refuerzo")
        elif Vu<Vc_phi:
            print("Se requieren estribo minimos")
            while Av_min>Area_resistente:
                print("Escoger un numero mas grande")
                numero=int(input("Introduzca nuevo numero: "))
                Area=barras[numero]
                Area_resistente=Area*2
                s=s_max
        else:
            if Vu<=0.33*fc**0.5*b*d:
                s=phi*Area_resistente*fyt*d/(Vu-Vc_phi)
                
                if s>d/2:
                    if numero==2:
                        s=s_max
                    else:
                        print("Se puede y debe disminuir la designacion del acero para no sobrereforzar")
            else:
                s=phi*Area_resistente*fyt*d/(Vu-Vc_phi)
                
                if s>d/4:
                    print("Se puede y debe disminuir la designacion del acero para no sobrereforzar")
                elif s<=0.03:
                    print("Aumentar la designacion de la barra")


        return "Estribos #" + str(numero) + " cada " + str(round(s,2)) + " m"

# Calcular diseño a momento con tracción y compresión
def calcular_momento(b, h, recub, fc, fy, Mu, phi, Es, gamma):
    """
    Función para calcular el diseño a momento y obtener el acero a tensión y compresión (si se requiere).
    """
    d = h - recub
    dprima = recub
    # Parámetro beta en función de fc
    if fc <= 28:
        beta = 0.85
    elif fc >= 55:
        beta = 0.65
    else:
        beta = 0.85 - (0.05 * (fc - 28)) / 7
    eps_u = 0.003
    eps_y = fy / Es

    # Cálculo de acero máximo
    rho_max = gamma * beta * fc / fy * (eps_u / (eps_u + 0.005))
    As_max = rho_max * b * d
    Mmax_phi = phi * As_max * fy * (d - (As_max * fy) / (2 * gamma * fc * b))

    # Cálculo de acero mínimo
    As_min1 = fc ** 0.5 / (4 * fy) * b * d
    As_min2 = 1.4 * b * d / fy
    As_min = max(As_min1, As_min2)

    
    Mu=Mu/1000
    if Mu > Mmax_phi:
        M2 = (Mu - Mmax_phi) / phi
        As2 = M2 / (fy * (d - dprima))
        As = As_max + As2
        Asprima = As2

        # Comprobación de equilibrio
        rho_y = gamma * fc / fy * beta * eps_u / (eps_u + fy / Es) * dprima / d + Asprima / (b * d)
        rho = As / (b * d)

        if rho < rho_y:
            a = (As - Asprima) * fy / (gamma * fc * b)
            c = a / beta
            fsprima = eps_u * Es * (c - dprima) / c
            Asprima = Asprima * fy / fsprima
           
    else:
        print("No usa acero a compresión")
        As = max(As_min, (0.9 * d - (0.81 * d ** 2 - 1.8 * Mu / (gamma * fc * b)) ** 0.5) / (0.9 * fy / (gamma * fc * b)))
        Asprima = 0
        
    
    return As, Asprima


# Ejecutar el proceso completo para Flask
def ejecutar_proceso(file_path, df_seleccionado, numero_barra_cortante, numero_barra_momento, 
                     tipo_concreto, b, h, recub, fc, fyt, fy, phi_cortante, phi_momento, 
                     Es, gamma, R, x_col):
    
    # Procesar los datos seleccionados
    momento_reducido, cortante_reducido = procesar_datos(df_seleccionado, x_col, rango=R)

    # Análisis preliminar de la geometría de la sección
    Av_min, As_min = calcular_areas_minimas(b, h, recub, fc, fy, fyt)

    # Obtener el área de las barras seleccionadas
    area_barra_cortante = barras[numero_barra_cortante]
    area_barra_momento = barras[numero_barra_momento]

    print(f"Usando barra #{numero_barra_cortante} con área {area_barra_cortante} mm² para cortante y barra #{numero_barra_momento} con área {area_barra_momento} mm² para momento")

    print("\n--- Resultados por rango ---\n")
    resultados = []
    for rango, Mu in momento_reducido.items():
        Vu = cortante_reducido[rango]

        print(f"Rango: {rango}")
        
        # Calcular cortante con el número de barra seleccionado
        resultado_cortante = calcular_cortante(b, h, recub, fc, fyt, Vu, phi_cortante, tipo_concreto, numero_barra_cortante)
        print(resultado_cortante)
        
        # Calcular momento con el número de barra seleccionado
        As, Asprima = calcular_momento(b, h, recub, fc, fy, Mu, phi_momento, Es, gamma)
        print("Momento Último: " + str(Mu) + " kN·m")

        # Mostrar el número de barras de tracción y compresión con su área
        num_barras_traccion = int(np.ceil((As * 1000**2) / area_barra_momento))
        num_barras_compresion = int(np.ceil((Asprima * 1000**2) / area_barra_momento))

        print(f"Acero a tracción = {num_barras_traccion} #{numero_barra_momento} con área {area_barra_momento} mm²")
        print(f"Acero a compresión = {num_barras_compresion} #{numero_barra_momento} con área {area_barra_momento} mm²")

        # Guardar los resultados en una lista para enviarlos a la plantilla HTML
        resultados.append({
            "rango": rango,
            "Vu": Vu,
            "resultado_cortante": resultado_cortante,
            "Mu": Mu,
            "num_barras_traccion": num_barras_traccion,
            "numero_barra_momento": numero_barra_momento,  # Añadimos el área aquí
            "num_barras_compresion": num_barras_compresion,
            "numero_barra_momento": numero_barra_momento  # Añadimos el área aquí también
        })
    
    # Guardar el gráfico de los valores originales y obtener la ruta
    graph_path = graficar_resultados(df_seleccionado)
    
    return resultados, graph_path


