import os
import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import pandas as pd

# Configuración de la página con temática educativa e infantil
st.set_page_config(
    page_title="¡Escuelita de Números Mágicos! 🎒✨",
    page_icon="🖍️",
    layout="wide"
)

# --- ESTILOS CSS: PIZARRA ESCOLAR Y ESTÉTICA INFANTIL ---
st.markdown("""
    <style>
    /* Importar tipografía infantil y redondeada */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&display=swap');

    /* Aplicar fuente a toda la aplicación */
    html, body, [class*="css"], p, span, label {
        font-family: 'Fredoka', cursive, sans-serif !important;
    }

    /* Fondo general alegre y colorido */
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #fef3c7 50%, #fce7f3 100%);
    }

    /* Barra lateral estilo casillero escolar */
    [data-testid="stSidebar"] {
        background-color: #fef08a;
        border-right: 4px dashed #f59e0b;
    }

    /* Títulos divertidos con relieve colorido */
    h1 {
        color: #d97706 !important;
        text-shadow: 2px 2px 0px #fde68a;
        text-align: center;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #0284c7 !important;
    }

    /* Tarjetas de pizarra escolar para los resultados */
    .pizarra-card {
        background-color: #1e293b;
        border: 6px solid #b45309;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }

    /* Botones grandes y coloridos estilo juguete */
    .stButton > button {
        background-color: #10b981 !important;
        color: white !important;
        border-radius: 25px !important;
        border: 4px solid #059669 !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        box-shadow: 0px 4px 0px #047857;
        transition: all 0.1s ease;
    }
    
    .stButton > button:hover {
        background-color: #34d399 !important;
    }

    .stButton > button:active {
        transform: translateY(4px);
        box-shadow: 0px 0px 0px #047857;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar con información amigable
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=300&auto=format&fit=crop&q=60", caption="¡Aprende jugando!")
    st.subheader("🎒 ¡Hola, Pequeño Artista!")
    st.write("1. Elige un número para practicar o dibuja libremente.")
    st.write("2. Usa el lápiz mágico para escribir el número en la pizarra.")
    st.write("3. ¡Presiona el botón para ver qué dice el Duende IA!")
    st.markdown("---")
    with st.expander("⚙️ Información para profes y papás"):
        st.write(f"**TensorFlow:** {tf.__version__}")
        st.write(f"**Keras:** {keras.__version__}")

st.title("🎒 ¡La Escuelita de los Números Mágicos! 🪄✨")
st.markdown("<p style='text-align: center; font-size: 1.3rem; color: #475569;'>¡Dibuja un número en la pizarra y descubre si la Inteligencia Artificial lo reconoce!</p>", unsafe_allow_html=True)

# Cargar modelo con mensajes amigables
@st.cache_resource
def load_mnist_model():
    model_files = ['mnist_model.keras', 'mnist_model.h5']
    for model_path in model_files:
        if os.path.exists(model_path):
            try:
                model = keras.models.load_model(model_path)
                return model
            except Exception as e:
                continue
    return None

model = load_mnist_model()

if model is None:
    st.error("🏫 ¡Uy! El maestro robot olvidó cargar su libro de números.")
    st.info("Sube el archivo `mnist_model.keras` a la raíz de tu proyecto para comenzar la clase.")
    st.stop()

# Selector de reto o modo libre
modo = st.radio(
    "🎯 ¿Cómo quieres jugar hoy?", 
    ["🎨 Modo Libre (Dibuja el número que quieras)", "🏆 ¡Reto del Número Mágico!"],
    horizontal=True
)

target_digit = None
if "Reto" in modo:
    if 'reto_actual' not in st.session_state:
        st.session_state.reto_actual = np.random.randint(0, 10)
    
    col_reto1, col_reto2 = st.columns([3, 1])
    with col_reto1:
        st.markdown(f"### 🌟 ¡Reto del día: Dibuja el número **{st.session_state.reto_actual}**! 🌟")
    with col_reto2:
        if st.button("🔄 Cambiar reto"):
            st.session_state.reto_actual = np.random.randint(0, 10)
            st.rerun()
    target_digit = st.session_state.reto_actual

# Interfaz principal de dibujo (Pizarra escolar oscura con tiza blanca)
col_canvas, col_panel = st.columns([1.2, 1], gap="large")

with col_canvas:
    st.markdown("#### 🖍️ Tu Pizarra Mágica")
    # Pizarra escolar con fondo negro/oscuro y trazo blanco/tiza
    canvas_result = st_canvas(
        fill_color="black",
        stroke_width=25,
        stroke_color="white",
        background_color="#0f172a",
        width=350,
        height=350,
        drawing_mode="freedraw",
        key="canvas_pizarra",
    )

with col_panel:
    st.markdown("#### 🕹️ ¡Panel de Control!")
    st.write("Cuando termines tu dibujo, presiona el botón verde para calificar tu obra maestra.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        predict_btn = st.button("✨ ¡Adivinar!", use_container_width=True)
    with col_b2:
        clear_btn = st.button("🧹 Borrar", use_container_width=True)
        if clear_btn:
            st.rerun()

# Lógica de predicción y feedback
if predict_btn:
    if canvas_result.image_data is not None:
        if np.max(canvas_result.image_data) == 0:
            st.warning("⚠️ ¡La pizarra está vacía! Dibuja un número primero.")
        else:
            with st.spinner("🔮 El duende inteligente está mirando tu dibujo..."):
                # Procesar imagen para el modelo MNIST
                image = Image.fromarray(
                    canvas_result.image_data.astype("uint8")
                ).convert("L")
                
                image_resized = image.resize((28, 28), Image.Resampling.LANCZOS)
                img_array = np.array(image_resized) / 255.0
                img_array = img_array.reshape(1, 28, 28, 1)
                
                # Predicción del modelo
                prediction = model.predict(img_array, verbose=0)
                digit = np.argmax(prediction)
                confidence = np.max(prediction) * 100

            # Mostrar resultados con estilo muy animado
            st.markdown("---")
            
            if target_digit is not None:
                if digit == target_digit:
                    st.balloons()
                    st.success(f"🎉 ¡WOOOOW! ¡Dibujaste exactamente el número **{target_digit}**! ¡Eres un genio total! ⭐⭐⭐")
                else:
                    st.warning(f"🤔 ¡Casi lo logras! El duende cree que dibujaste un **{digit}**, pero estábamos buscando el **{target_digit}**. ¡Inténtalo otra vez! 💪")
            else:
                if confidence > 70:
                    st.success(f"🌟 ¡Increíble! El duende mágico dice que tu número es el **{digit}** (¡Seguridad del {confidence:.0f}%!)")
                    if confidence > 90:
                        st.balloons()
                else:
                    st.info(f"🧐 Mmm... El duende cree que es un **{digit}**, pero no está muy seguro ({confidence:.0f}%). ¿Puedes hacerlo más grande o clarito?")

            # Métricas y detalles divertidos
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Número detectado", str(digit))
            with m2:
                st.metric("Seguridad del Duende", f"{confidence:.1f}%")

            # Miniaturas del dibujo procesado
            with st.expander("🔍 ¿Cómo ve el duende tu dibujo?"):
                sub_c1, sub_c2 = st.columns(2)
                with sub_c1:
                    st.write("**Tu dibujo:**")
                    st.image(canvas_result.image_data, width=150)
                with sub_c2:
                    st.write("**Vista del Duende (28x28):**")
                    st.image(image_resized, width=150)
    else:
        st.warning("⚠️ ¡Dibuja algo en la pizarra primero!")
