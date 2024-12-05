# Panel Domotico Virtual con Streamlit
# 
# Documentación disponible en:
# https://docs.streamlit.io/develop/quick-reference/cheat-sheet
# https://docs.streamlit.io/develop/api-reference
#

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

@st.cache_data
def calculate_correlation(data):
    return data.corr()

#--- session_state init
if "toggle_outside" not in st.session_state:
    st.session_state.toggle_inside = 0
if "toggle_inside" not in st.session_state:
    st.session_state.toggle_inside = 0

#--- page config
st.set_page_config(
    page_title="Dashboard",
    page_icon="🌐",
    initial_sidebar_state="collapsed"
    )

#--- Dataset
domotic_data = load_data("assets/domotics_dataset_november2024_103r.csv")
data_sample = domotic_data.sample(n=1)
temperature_sample = data_sample["temperature"].values[0]
humidity_sample = data_sample["humidity"].values[0]
timestamp_sample = data_sample["timestamp"].values[0]

#-- Gráficos de tipo gauge
fig1 = go.Figure(
    data=[
            go.Indicator(
                mode="gauge+number",
                value=humidity_sample,
                title={'text': "Humedad"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "blue"}
                },
                number={
                        'valueformat': ".1f",
                        'suffix': " %"
                    }
            )
        ],
    layout={
        "width":400, 
        "height":300
        }
)

fig2 = go.Figure(
    data=[
            go.Indicator(
                domain = {'x': [0, 1], 'y': [0, 1]},
                value = temperature_sample,
                mode = "gauge+number+delta",
                title = {'text': "Temperatura"},
                delta = {'reference': 25},
                gauge = {'axis': {'range': [-15, 75]},
                            'steps' : [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [-15, 0], 'color': "cyan"}],
                            'threshold' : {'line': {'color': "red", 'width': 4}, 
                            'thickness': 0.75, 'value': 40
                            }
                        },
                number={
                        'valueformat': ".1f",
                        'suffix': " °C"
                    }
                    )
                ],
    layout={
        "width":400, 
        "height":300
        }
)

#--- App Layout
st.title("Los datos que nos rodean")
st.write("#### Uso de datos en aplicaciones domóticas 🚀")
tab1, tab2, tab3 = st.tabs(["Control", "Visualización de datos", "Dataset"])

with tab1:
    
    with st.container(border=True):

        st.write("##### Control de iluminación")
        col1, col2, col3 = st.columns(3, gap="medium", vertical_alignment="center")

    with col3:
        with st.container(border=True):
            brightness_in = st.slider("Nivel de brillo - Interior", 0, 255, 50)
        with st.container(border=True):
            brightness_out = st.slider("Nivel de brillo - Exterior", 0, 255, 25)

    with col1:
        st.session_state.toggle_inside = st.toggle("Luces Interior")
        if (st.session_state.toggle_inside):
            st.image("./assets/lamp_on.svg", width=50)
        else:
            st.image("./assets/lamp_off.svg", width=50)
        st.write("🔆 Nivel de brillo:", brightness_in)

    with col2:
        st.session_state.toggle_outside = st.toggle("Luces Exterior")
        if (st.session_state.toggle_outside):
            st.image("./assets/lamp_on.svg", width=50)
        else:
            st.image("./assets/lamp_off.svg", width=50)
        st.write("🔆 Nivel de brillo:", brightness_out)

    with st.container(border=True):
        st.write("##### Control de temperatura")
        col4, col5 = st.columns([2, 1], gap="large")
        
        with col4:
            st.write("🌡️ Temperatura actual:", temperature_sample, "°C")
            temperature_set = st.slider("Temperatura deseada", 0, 50, 24)
            data = pd.DataFrame({"Set": [temperature_set],
                                "Actual": [temperature_sample]})

        with col5:
            st.bar_chart(data, stack="normalize", width=150, height=200, 
            use_container_width=False, color=["#FF0000", "#0000FF"])

with tab2:
    
    with st.container(border=True):

        st.write(f"##### Humedad / Temperatura ({timestamp_sample})")
        col6, col7 = st.columns(2)

        with col6:
            st.plotly_chart(fig1, use_container_width=True)

        with col7:
            st.plotly_chart(fig2, use_container_width=True)

    with st.container(border=True):        

        st.write("##### Humedad / Temperatura Histórico")
        temperature_max = domotic_data["temperature"].max()
        temperature_min = domotic_data["temperature"].min()
        humidity_max = domotic_data["humidity"].max()
        humidity_min = domotic_data["humidity"].min()

        data_amount = st.select_slider("Seleccione la cantidad de datos a graficar:", options=[
                        50, 100, 200, 400, 800, 1600, 3200], value=(100))
        chart_data = domotic_data.iloc[0:data_amount, [0, 1, 2]]
        st.line_chart(chart_data, x="timestamp", y=["temperature", "humidity"])
    
        st.write(f"🥵 La temperatura máxima registrada en noviembre fue de {temperature_max} °C.")
        st.write(f"🥶 La temperatura mínima registrada en noviembre fue de {temperature_min} °C.")
        st.write(f"☔ La humedad máxima registrada en noviembre fue de {humidity_max} %.")
        st.write(f"💧 La humedad mínima registrada en noviembre fue de {humidity_min} %.")

    with st.container(border=True):

        correlation_data = domotic_data.iloc[:, 1:7]
        correlation_matrix = calculate_correlation(correlation_data)

        fig = go.Figure(
            data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale="spectral",
                zmin=-1, zmax=1,
                colorbar=dict(title="Correlación")
            )
        )

        # Agregar título y diseño
        fig.update_layout(
            title="Matriz de Correlación - Consumo Eléctrico",
            xaxis_title="Variables",
            yaxis_title="Variables",
            width=600,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write("##### Correlación de datos")
        st.markdown(''' - Valores cercanos a `1.0`: **correlación positiva fuerte.**\n    - Ejemplo: `electric_consumption` y `temperature` (`0.951`) -> Mayor temperatura está asociada con un mayor consumo eléctrico.\n - Valores cercanos a `-1.0`: **correlación negativa fuerte.**\n    - Ejemplo: `electric_consumption` y `humidity` (`-0.881`) -> Más humedad podría reducir el consumo eléctrico.\n - Valores cercanos a `0`: **correlación débil o inexistente**.
        ''')

with tab3:
    st.text("A continuación se muestra el dataset utilizado para esta aplicación.\nAclaración: los datos fueron generados por una IA.")
    options = ["Clima", "Seguridad", "Consumo eléctrico", "Todos los campos"]
    selection = st.segmented_control(
            "Filtrar:", options, default="Todos los campos", 
            selection_mode="single"
            )

    match selection:
        case "Clima":
            selection = ["timestamp", "temperature", "humidity"]
        case "Seguridad":
            selection = ["timestamp", "pir_sensor", "door_opening", "gases"]
        case "Consumo eléctrico":
            selection = ["timestamp", "electric_consumption"]    
        case "Todos los campos":
            selection = ["timestamp", "temperature", "humidity", "pir_sensor", 
                "door_opening", "gases", "electric_consumption"]
    
    st.write(domotic_data[selection])

#--- Sidebar
st.sidebar.title("session_state")
st.sidebar.write("toggle_inside: ", st.session_state.toggle_inside)
st.sidebar.write("toggle_outside: ", st.session_state.toggle_outside)