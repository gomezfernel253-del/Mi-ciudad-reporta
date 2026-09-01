import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Mapa Ciudadano - Arauca", layout="wide")

# Inicialización de la base de datos en sesión
if 'reportes' not in st.session_state:
    st.session_state.reportes = []

st.title("🗺️ Mapa Inteligente de Problemas Ciudadanos - Arauca")

# Selección de Rol en la barra lateral
rol = st.sidebar.radio("Selecciona tu Rol:", ["Ciudadano (Reportar)", "Administrador (Autoridad)"])

# Coordenadas predeterminadas centradas en Arauca, Colombia
LAT_DEFAULT = 7.0847
LNG_DEFAULT = -70.7591

# ---------------------------------------------------------
# MÓDULO CIUDADANO (REPORTAR Y VISUALIZAR)
# ---------------------------------------------------------
if rol == "Ciudadano (Reportar)":
    st.subheader("📍 Realizar un Nuevo Reporte")
    st.write("Haz clic en el mapa para seleccionar la ubicación exacta del problema:")
    
    # Crear el mapa interactivo de Arauca
    m = folium.Map(location=[LAT_DEFAULT, LNG_DEFAULT], zoom_start=14)
    
    # Renderizar marcadores de reportes existentes
    for r in st.session_state.reportes:
        color = "red" if r['estado'] == "Reportado" else "orange" if r['estado'] == "En proceso" else "green"
        folium.Marker(
            [r['lat'], r['lng']],
            popup=f"<b>{r['categoria']}</b><br>{r['descripcion']}<br><b>Estado:</b> {r['estado']}",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)
        
    map_data = st_folium(m, width=700, height=420)
    
    # Formulario para registrar la incidencia
    with st.form("form_reporte"):
        col1, col2 = st.columns(2)
        with col1:
            lat = map_data['last_clicked']['lat'] if map_data and map_data['last_clicked'] else LAT_DEFAULT
            lng = map_data['last_clicked']['lng'] if map_data and map_data['last_clicked'] else LNG_DEFAULT
            st.text(f"Coordenadas seleccionadas: {lat:.5f}, {lng:.5f}")
            categoria = st.selectbox("Categoría del Problema:", ["Baches/Vías", "Alumbrado Público", "Basura/Aseo", "Seguridad", "Otro"])
        
        with col2:
            descripcion = st.text_area("Descripción del problema:")
            foto = st.file_uploader("Adjuntar fotografía (Opcional)", type=["jpg", "png", "jpeg"])
            
        submitted = st.form_submit_button("Enviar Reporte")
        
        if submitted:
            nuevo_reporte = {
                "id": len(st.session_state.reportes) + 1,
                "lat": lat,
                "lng": lng,
                "categoria": categoria,
                "descripcion": descripcion,
                "estado": "Reportado",
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.reportes.append(nuevo_reporte)
            st.success("¡Reporte enviado exitosamente! Las autoridades revisarán la incidencia.")

# ---------------------------------------------------------
# MÓDULO ADMINISTRADOR (CAMBIO DE ESTADO PROTEGIDO)
# ---------------------------------------------------------
else:
    st.subheader("🔒 Panel de Administración y Seguimiento")
    password = st.text_input("Ingresa la clave de Administrador:", type="password")
    
    if password == "admin123":
        st.success("Acceso concedido.")
        
        if len(st.session_state.reportes) == 0:
            st.info("No hay reportes registrados aún.")
        else:
            df = pd.DataFrame(st.session_state.reportes)
            st.dataframe(df)
            
            st.markdown("---")
            st.write("### Actualizar Estado de Reporte")
            id_reporte = st.number_input("ID del reporte a modificar:", min_value=1, max_value=len(st.session_state.reportes), step=1)
            nuevo_estado = st.selectbox("Nuevo Estado:", ["Reportado", "En proceso", "Solucionado"])
            
            if st.button("Actualizar Estado"):
                for r in st.session_state.reportes:
                    if r['id'] == id_reporte:
                        r['estado'] = nuevo_estado
                        st.success(f"El reporte #{id_reporte} cambió a estado: {nuevo_estado}")
                        st.rerun()
    elif password != "":
        st.error("Contraseña incorrecta. Los ciudadanos no tienen permiso para cambiar el estado.")