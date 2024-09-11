from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta  # Importa datetime y timedelta

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r"C:\Users\Danie\OneDrive\Documentos\DANIEL\9NO\PROGRAMACION\Proyecto-Final-Los-Inges-\uploads"

scheduler = BackgroundScheduler()
scheduler.start()

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted {file_path}")

class BeamDesign:
    def __init__(self, file_path):
        self.data = pd.read_csv(file_path)

    def process_data(self):
        # Retorna los nombres de las columnas del DataFrame
        return list(self.data.columns)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vigas', methods=['GET', 'POST'])
def vigas():
    if request.method == 'POST':
        file = request.files.get('file')

        if file and file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            beam_design = BeamDesign(file_path)
            column_names = beam_design.process_data()

            # Calcula el tiempo futuro para eliminar el archivo
            run_time = datetime.now() + timedelta(seconds=30)

            # Programa la eliminación del archivo en 60 segundos
            scheduler.add_job(delete_file, 'date', run_date=run_time, args=[file_path])

            return render_template('vigas.html', column_names=column_names)

    return render_template('vigas.html')

@app.route('/columnas')
def columnas():
    return render_template('columnas.html')

if __name__ == '__main__':
    app.run(debug=True)
