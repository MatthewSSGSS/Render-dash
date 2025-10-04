import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import numpy as np

# Inicializar la aplicación Dash
app = dash.Dash(__name__)
app.title = "Análisis Aptitud - La Guajira"

# Configuración para Render
server = app.server

# Cargar y preparar datos con manejo de errores
try:
    df = pd.read_csv("datos_guajira.csv")
    print("CSV cargado exitosamente!")
    print(f"Columnas: {df.columns.tolist()}")
    print(f"Forma del dataset: {df.shape}")
    
    # Limpiar y preparar datos 
    df["Código municipio"] = df["Código municipio"].astype(str).str.zfill(5)
    df["Código departamento"] = df["Código departamento"].astype(str).str.zfill(2)
    df['Área (ha)'] = df['Área (ha)'].astype(str).str.replace(',', '').astype(float)
    
except Exception as e:
    print(f"Error cargando CSV: {e}")
    # Datos de ejemplo como fallback
    df = pd.DataFrame({
        'Municipio': ['Riohacha', 'Maicao', 'Uribia', 'Manaure', 'Albania'],
        'Aptitud': ['Aptitud alta', 'Aptitud media', 'Aptitud baja', 'No apta', 'Aptitud media'],
        'Área (ha)': [15000, 12000, 8000, 5000, 9000],
        'Código municipio': ['44001', '44002', '44003', '44004', '44005'],
        'Código departamento': ['44', '44', '44', '44', '44']
    })
    print("Usando datos de ejemplo")

# Crear datos simplificados para el mapa 
def crear_datos_mapa():
    # Coordenadas aproximadas de municipios de La Guajira
    coordenadas = {
        'Riohacha': [11.5444, -72.9072],
        'Maicao': [11.3778, -72.2389],
        'Uribia': [11.7139, -72.2658],
        'Manaure': [11.7750, -72.4444],
        'Albania': [11.1600, -72.5917],
        'Barrancas': [10.9575, -72.7958],
        'Fonseca': [10.8861, -72.8486],
        'San Juan': [10.7711, -72.9603],
        'Villanueva': [10.6053, -72.9800],
        'Urumita': [10.5589, -73.0153]
    }
    
    # Agregar coordenadas al DataFrame
    df_mapa = df.copy()
    df_mapa['Latitud'] = df_mapa['Municipio'].map(lambda x: coordenadas.get(x, [11.3, -72.5])[0])
    df_mapa['Longitud'] = df_mapa['Municipio'].map(lambda x: coordenadas.get(x, [11.3, -72.5])[1])
    
    return df_mapa

df_mapa = crear_datos_mapa()

# Calcular métricas
total_municipios = df['Municipio'].nunique()
total_area = df['Área (ha)'].sum()
aptitud_counts = df['Aptitud'].value_counts()

# Colores
colores = {
    'No apta': '#FF6B6B',
    'Aptitud baja': '#FFD166', 
    'Aptitud media': '#06D6A0',
    'Aptitud alta': '#118AB2'
}

# Layout simple y estable
app.layout = html.Div([
    html.H1("🌱 Aptitud para Producción Bovina - La Guajira", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
    
    # Métricas
    html.Div([
        html.Div([
            html.H3(f"{total_municipios}", style={'color': '#2c3e50', 'margin': '0'}),
            html.P("Municipios", style={'margin': '0', 'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '15px', 'flex': '1'}),
        
        html.Div([
            html.H3(f"{total_area:,.0f} ha", style={'color': '#2c3e50', 'margin': '0'}),
            html.P("Área total", style={'margin': '0', 'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '15px', 'flex': '1'}),
        
        html.Div([
            html.H3(f"{len(aptitud_counts)}", style={'color': '#2c3e50', 'margin': '0'}),
            html.P("Categorías", style={'margin': '0', 'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '15px', 'flex': '1'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px', 'backgroundColor': '#ecf0f1', 'padding': '10px', 'borderRadius': '8px'}),
    
    # Filtro
    html.Div([
        dcc.Dropdown(
            id='filtro-aptitud',
            options=[{'label': 'Todas las zonas', 'value': 'all'}] + 
                    [{'label': aptitud, 'value': aptitud} for aptitud in sorted(df['Aptitud'].unique())],
            value='all',
            style={'width': '50%', 'margin': 'auto'},
            clearable=False
        )
    ], style={'marginBottom': '30px'}),
    
    # Mapa Interactivo
    html.Div([
        html.H3("Mapa Interactivo de La Guajira"),
        dcc.Graph(id='mapa-interactivo')
    ], style={'marginBottom': '30px', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Gráfico de áreas
    html.Div([
        html.H3("Áreas por Tipo de Aptitud"),
        dcc.Graph(id='grafico-areas')
    ], style={'marginBottom': '30px', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Gráfico de distribución
    html.Div([
        html.H3("Distribución por Aptitud"),
        dcc.Graph(id='grafico-torta')
    ], style={'marginBottom': '30px', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Tabla de datos
    html.Div([
        html.H3("Datos por Municipio"),
        html.Div(id='tabla-datos')
    ], style={'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# Callbacks optimizados
@app.callback(
    [Output('mapa-interactivo', 'figure'),
     Output('grafico-areas', 'figure'),
     Output('grafico-torta', 'figure'),
     Output('tabla-datos', 'children')],
    Input('filtro-aptitud', 'value')
)
def actualizar_dashboard(filtro):
    try:
        print(f"Callback ejecutado - Filtro: {filtro}")
        
        # Filtrar datos
        if filtro == 'all':
            datos_filtrados = df_mapa
            datos_originales = df
        else:
            datos_filtrados = df_mapa[df_mapa['Aptitud'] == filtro]
            datos_originales = df[df['Aptitud'] == filtro]
        
        print(f"Datos filtrados: {len(datos_filtrados)} filas")
        
        # 1. MAPA INTERACTIVO
        if not datos_filtrados.empty:
            fig_mapa = px.scatter_mapbox(
                datos_filtrados,
                lat="Latitud",
                lon="Longitud",
                hover_name="Municipio",
                hover_data={
                    "Aptitud": True, 
                    "Área (ha)": ':,.0f',
                    "Latitud": False,
                    "Longitud": False
                },
                color="Aptitud",
                size="Área (ha)",
                size_max=15,
                zoom=7,
                height=400,
                color_discrete_map=colores
            )
            fig_mapa.update_layout(
                mapbox_style="open-street-map",
                mapbox=dict(center=dict(lat=11.3, lon=-72.5)),
                margin={"r": 0, "t": 30, "l": 0, "b": 0}
            )
        else:
            fig_mapa = px.scatter_mapbox(title="No hay datos para mostrar")
            fig_mapa.update_layout(mapbox_style="open-street-map")
        
        # 2. GRÁFICO DE ÁREAS
        if not datos_originales.empty:
            datos_agrupados = datos_originales.groupby('Aptitud')['Área (ha)'].sum().reset_index()
            fig_areas = px.bar(
                datos_agrupados,
                x='Aptitud',
                y='Área (ha)',
                color='Aptitud',
                color_discrete_map=colores,
                title=""
            )
            fig_areas.update_layout(showlegend=False)
        else:
            fig_areas = px.bar(title="No hay datos para mostrar")
        
        # 3. GRÁFICO DE TORTA
        if not datos_originales.empty and len(datos_originales) > 0:
            fig_torta = px.pie(
                datos_originales,
                names='Aptitud',
                values='Área (ha)',
                color='Aptitud',
                color_discrete_map=colores,
                height=300
            )
        else:
            fig_torta = px.pie(names=['Sin datos'], values=[1], height=300)
        
        # 4. TABLA DE DATOS
        if not datos_originales.empty:
            tabla = html.Table([
                html.Thead(
                    html.Tr([html.Th("Municipio"), html.Th("Aptitud"), html.Th("Área (ha)")])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row['Municipio']),
                        html.Td(row['Aptitud']),
                        html.Td(f"{row['Área (ha)']:,.0f}")
                    ]) for _, row in datos_originales.head(20).iterrows()  # Limitar a 20 filas
                ])
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})
        else:
            tabla = html.P("No hay datos para mostrar con el filtro seleccionado")
        
        print("Callback completado exitosamente")
        return fig_mapa, fig_areas, fig_torta, tabla
        
    except Exception as e:
        print(f"Error en callback: {e}")
        # Figuras de error como fallback
        fig_error = px.scatter(title=f"Error: {str(e)}")
        return fig_error, fig_error, fig_error, html.P(f"Error: {str(e)}")

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)