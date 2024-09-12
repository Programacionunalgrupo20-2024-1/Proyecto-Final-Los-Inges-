from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import programa  # Aquí importamos tu archivo programa.py

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r"C:\Users\Danie\OneDrive\Documentos\DANIEL\9NO\PROGRAMACION\Proyecto-Final-Los-Inges-\uploads"

scheduler = BackgroundScheduler()
scheduler.start()

# Función para eliminar archivos antiguos
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted {file_path}")

# Clase para manejar el diseño de vigas
class BeamDesign:
    def __init__(self, file_path):
        self.data = pd.read_csv(file_path)

    def process_data(self):
        # Retorna los nombres de las columnas del DataFrame
        return list(self.data.columns)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/vigas', methods=['GET', 'POST'])
def vigas():
    if request.method == 'POST':
        # Obtener datos del formulario
        file = request.files.get('file')

        # Si ya se subió un archivo CSV, procesarlo
        if file and file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Procesar el archivo CSV y obtener las columnas
            beam_design = BeamDesign(file_path)
            columnas = beam_design.process_data()

            # Guardar el archivo temporalmente y programar su eliminación
            run_time = datetime.now() + timedelta(seconds=30)  # Guardar archivo por 5 minutos
            scheduler.add_job(delete_file, 'date', run_date=run_time, args=[file_path])

            # Obtener los datos del formulario
            tipo_concreto, b, h, recub, fc, fyt, fy, phi_cortante, phi_momento, Es, gamma, R = programa.input_parametros(request.form)

            # Calcular áreas mínimas de cortante y momento
            Av_min, As_min = programa.calcular_areas_minimas(b, h, recub, fc, fy, fyt)

            # Mantener los valores ingresados en el formulario
            form_data = {
                'tipo_concreto': request.form['tipo_concreto'],
                'b': request.form['b'],
                'h': request.form['h'],
                'recub': request.form['recub'],
                'fc': request.form['fc'],
                'fyt': request.form['fyt'],
                'R': request.form['R'],
                'Av_min': round(Av_min * 1000**2, 2),  # Mostrar área mínima de cortante
                'As_min': round(As_min * 1000**2, 2)   # Mostrar área mínima de momento
            }

            # Renderizar el formulario con las columnas del CSV y los valores previos
            return render_template('vigas_columnas.html', columnas=columnas, form_data=form_data, file_path=file_path)

    return render_template('vigas.html')

@app.route('/procesar_columnas', methods=['POST'])
def procesar_columnas():
    # Obtener los datos del formulario
    file_path = request.form['file_path']
    x_col = request.form['x_col']
    momento_col = request.form['momento_col']
    cortante_col = request.form['cortante_col']
    numero_barra_cortante = int(request.form['numero_barra_cortante'])
    numero_barra_momento = int(request.form['numero_barra_momento'])

    # Cargar el CSV con las columnas seleccionadas
    df = pd.read_csv(file_path)
    df_seleccionado, x_col_normalized = programa.seleccionar_columnas(file_path, x_col, momento_col, cortante_col)

    # Obtener los parámetros de diseño desde el formulario
    tipo_concreto, b, h, recub, fc, fyt, fy, phi_cortante, phi_momento, Es, gamma, R = programa.input_parametros(request.form)

    # Ejecutar el proceso de cálculo y obtener la ruta del gráfico
    resultados, graph_path = programa.ejecutar_proceso(
        file_path, df_seleccionado, numero_barra_cortante, numero_barra_momento,
        tipo_concreto, b, h, recub, fc, fyt, fy, phi_cortante, phi_momento, Es, gamma, R, x_col_normalized
    )

    # Renderizar la página de resultados y pasar la ruta del gráfico
    return render_template('vigas_resultados.html', resultados=resultados, graph_path=graph_path)




# Ruta para la página de columnas (si se desea agregar)
@app.route('/columnas')
def columnas():
    return render_template('columnas.html')

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
