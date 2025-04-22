from flask import Flask, render_template, request, redirect, url_for
import os
import time
from datetime import datetime
import numpy as np
import base64
import uuid

from PIL import Image
from predict import predict_digit

app = Flask(__name__)

# Configuración para subir archivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limitar a 2MB

# Asegurarse de que el directorio de subidas exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_and_preprocess_image(file_path):
    """Carga y preprocesa una imagen para la predicción"""
    # Esta función se puede personalizar según las necesidades del modelo
    # Por ejemplo, para MNIST, normalmente se necesita convertir a escala de grises y redimensionar a 28x28
    try:
        img = Image.open(file_path).convert('L')  # Convertir a escala de grises
        img = img.resize((28, 28))  # Redimensionar a 28x28 para MNIST
        img_array = np.array(img)
        img_array = img_array / 255.0  # Normalizar entre 0 y 1
        return img_array
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return None


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', current_year=datetime.now().year)


@app.route('/predict', methods=['POST'])
def predict():
    # Verificar si hay un archivo en la solicitud
    if 'image' not in request.files:
        return redirect(url_for('index'))

    file = request.files['image']

    # Si el usuario no selecciona un archivo
    if file.filename == '':
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        # Generar un nombre de archivo único para evitar colisiones
        unique_filename = f"{uuid.uuid4().hex}_{int(time.time())}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        # Obtener predicción
        digit, confidence = predict_digit(file_path)

        if digit is not None:
            # Redondear la confianza a 2 decimales
            confidence = round(confidence, 2)

            return render_template(
                'index.html',
                prediction=digit,
                confidence=confidence,
                filename=unique_filename,
                current_year=datetime.now().year
            )

    # En caso de error
    return render_template('index.html', error="No se pudo procesar la imagen", current_year=datetime.now().year)


@app.route('/predict_drawing', methods=['POST'])
def predict_drawing():
    """Manejar predicción de dígito dibujado en el canvas"""
    if 'canvas_data' not in request.form:
        return redirect(url_for('index'))

    try:
        # Obtener datos del canvas en formato base64
        canvas_data = request.form['canvas_data']

        # Extraer la parte de datos de la imagen (eliminar el prefijo "data:image/png;base64,")
        image_data = canvas_data.split(',')[1]

        # Decodificar datos base64
        binary_data = base64.b64decode(image_data)

        # Crear un nombre de archivo único
        unique_filename = f"drawing_{uuid.uuid4().hex}.png"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # Guardar la imagen
        with open(file_path, 'wb') as f:
            f.write(binary_data)

        # Obtener predicción (usando la misma función que para imágenes subidas)
        digit, confidence = predict_digit(file_path)

        if digit is not None:
            # Redondear la confianza a 2 decimales
            confidence = round(confidence, 2)

            return render_template(
                'index.html',
                prediction=digit,
                confidence=confidence,
                filename=unique_filename,
                current_year=datetime.now().year
            )

    except Exception as e:
        print(f"Error al procesar el dibujo: {e}")

    # En caso de error
    return render_template('index.html', error="No se pudo procesar el dibujo", current_year=datetime.now().year)


# Manejador de error para archivos demasiado grandes
@app.errorhandler(413)
def too_large(e):
    return render_template('index.html', error="El archivo es demasiado grande (máximo 2MB)",
                           current_year=datetime.now().year)


if __name__ == '__main__':
    app.run(debug=True)