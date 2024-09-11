import pandas as pd
import numpy as np

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
def input_parametros():
    """
    Solicita al usuario ingresar los parámetros de entrada, incluyendo si el concreto es liviano o no.
    """
    tipo_concreto = input("¿El concreto es liviano? (si/no): ").strip().lower()
    b = float(input("Ingrese la base de la sección (en metros): "))
    h = float(input("Ingrese la altura de la sección (en metros): "))
    recub = float(input("Ingrese el recubrimiento de concreto (en metros): "))
    fc = float(input("Ingrese la resistencia del concreto (en MPa): "))
    fyt = float(input("Ingrese la resistencia del acero (en MPa): "))
    fy = float(fyt)
    phi_cortante = 0.75
    phi_momento = 0.9
    Es = 200000  # Módulo de elasticidad del acero (en MPa)
    gamma = 0.85
    
    return tipo_concreto, b, h, recub, fc, fyt, fy, phi_cortante, phi_momento, Es, gamma

# Función para leer y seleccionar columnas del CSV
def seleccionar_columnas(csv_path):
    """
    Lee el archivo CSV y selecciona las columnas de interés.
    """
    df = pd.read_csv(csv_path)
    
    # Mostrar las columnas disponibles
    print("Columnas disponibles:", df.columns.tolist())
    
    # Solicitar al usuario que seleccione las columnas
    x_col = input("Seleccione la columna de coordenadas X: ")
    momento_col = input("Seleccione la columna de Momento: ")
    cortante_col = input("Seleccione la columna de Cortante: ")
    
    # Extraer las columnas seleccionadas
    x = df[x_col].values
    momento = df[momento_col].values
    cortante = df[cortante_col].values
    
    # Crear un DataFrame con las columnas seleccionadas
    selected_df = pd.DataFrame({
        'x': x,
        'momento': momento,
        'cortante': cortante
    })
    
    return selected_df

# Procesar los datos y agrupar en rangos
def procesar_datos(df, rango=2):
    """
    Agrupa los datos de Momento y Cortante en intervalos de longitud `rango` metros.
    """
    momento_reducido = {}
    cortante_reducido = {}
    
    # Encontrar el mínimo y máximo de la coordenada X
    min_x = df['x'].min()
    max_x = df['x'].max()

    # Agrupar los datos en intervalos
    current_x1 = min_x
    while current_x1 < max_x:
        current_x2 = current_x1 + rango
        
        # Filtrar los datos en el intervalo actual
        datos_intervalo = df[(df['x'] >= current_x1) & (df['x'] < current_x2)]
        
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

# Seleccionar barras de cortante y momento
def seleccionar_numero_barra(Av_min, As_min):
    """
    Solicita al usuario el número de barra y calcula la cantidad de barras necesarias.
    """
    numero_barra = int(input("Ingrese el número de barra para estribos de cortante: "))
    area_cortante = barras[numero_barra] * 2 / 1000**2

    while area_cortante < Av_min:
        numero_barra = int(input("El número de barra es insuficiente. Seleccione un número mayor: "))
        area_cortante = barras[numero_barra] * 2 / 1000**2

    print(f"Barra seleccionada para cortante: #{numero_barra} con área {area_cortante * 1000**2:.2f} mm²")
    
    numero_barra_momento = int(input("Ingrese el número de barra para refuerzo a momento: "))
   
    
    return numero_barra, numero_barra_momento

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

# Ejecutar el proceso completo
def ejecutar_proceso(csv_path):
    """
    Función que ejecuta el proceso completo desde la lectura del CSV hasta el cálculo de cortante y momento.
    """
    # Leer los parámetros del usuario
    tipo_concreto, b, h, recub, fc, fyt, fy, phi_cortante, phi_momento, Es, gamma = input_parametros()

    # Leer y seleccionar las columnas del CSV
    df_seleccionado = seleccionar_columnas(csv_path)

    # Procesar los datos reducidos
    momento_reducido, cortante_reducido = procesar_datos(df_seleccionado)

    # Análisis preliminar de la geometría de la sección
    Av_min, As_min = calcular_areas_minimas(b, h, recub, fc, fy, fyt)

    # Seleccionar barras de cortante y momento
    numero_barra, numero_barra_momento= seleccionar_numero_barra(Av_min, As_min)

    print("\n--- Resultados por rango ---\n")
    for rango, Mu in momento_reducido.items():
        Vu = cortante_reducido[rango]

        print(f"Rango: {rango}")
        
        # Calcular cortante
        resultado_cortante = calcular_cortante(b, h, recub, fc, fyt, Vu, phi_cortante, tipo_concreto, numero_barra)
        print(resultado_cortante)
        

        # Calcular momento
        As, Asprima = calcular_momento(b, h, recub, fc, fy, Mu, phi_momento, Es, gamma)
        print("Momento Ultimo: " + str(Mu) + " kN·m")
        

        area_momento = barras[numero_barra_momento]
        Division=(As*1000**2)/area_momento
        Division1=(Asprima*1000**2)/area_momento
        num_barras_momento = int(np.ceil(Division))
        num_barras_momento1 = int(np.ceil(Division1))
        print(f"Acero a tracción = {num_barras_momento} #{numero_barra_momento} ")
        print(f"Acero a compresión =  {num_barras_momento1} #{numero_barra_momento} ")
    
        
        print("\n")

# Ejecutar el proceso completo con el archivo CSV
csv_path = r"C:\Users\Danie\OneDrive\Documentos\DANIEL\9NO\PROGRAMACION\Proyecto-Final-Los-Inges-\csv datos.csv"
ejecutar_proceso(csv_path)
