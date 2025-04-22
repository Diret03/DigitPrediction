from tensorflow import keras
import numpy as np
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Cargar el modelo al iniciar la aplicación
model = None
try:
    model = keras.models.load_model('./models/model_Mnist_LeNet.keras')
    print("¡Modelo cargado correctamente!")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")


def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """
    Preprocesa la imagen para que coincida con el formato MNIST:
    - Conversión a escala de grises
    - Redimensionamiento a 28x28
    - Normalización a [0,1]
    - Inversión si es necesario (dígito blanco sobre fondo negro)
    - Reshape a (1, 28, 28, 1)
    """
    # Cargar y convertir a escala de grises
    img = Image.open(image_path).convert('L')

    # Redimensionar a 28x28
    img = img.resize((28, 28))

    # Convertir a array numpy
    img_array = np.array(img, dtype=np.float32)

    # Normalizar a [0,1]
    img_array = img_array / 255.0

    # Invertir si la imagen es un dígito negro sobre fondo blanco
    # Comprobar si el fondo es brillante (blanco)
    if np.mean(img_array) > 0.5:
        img_array = 1 - img_array

    # Reshape para entrada del modelo
    img_array = img_array.reshape(1, 28, 28, 1)

    return img_array


def predict_digit(image_path):
    """
    Predice el dígito a partir de la ruta de la imagen utilizando el modelo cargado
    """
    if model is None:
        return None, 0

    try:
        # Preprocesar la imagen
        processed_img = preprocess_image(image_path)

        # Realizar predicción
        prediction = model.predict(processed_img, verbose=0)
        predicted_digit = np.argmax(prediction)
        confidence = float(np.max(prediction) * 100)  # Convertir a float para evitar problemas con np.float32

        return predicted_digit, confidence
    except Exception as e:
        print(f"Error en la predicción: {e}")
        return None, 0