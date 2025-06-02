import pandas as pd
import os
from datetime import datetime
import json

def generate_html_report():
    csv_path = 'catalogo.csv'
    if not os.path.exists(csv_path):
        print(f'No se encontró el archivo {csv_path}. Descárgalo primero.')
        return

    # Leer el CSV
    df = pd.read_csv(csv_path, delimiter=';', encoding='latin1')
    
    # Filtrar solo los datasets que tienen 'API' en la columna 'Formatos'
    api_datasets = df[df['Formatos'].str.contains('API', case=False, na=False)]
    
    # Preparar los datos para la tabla
    api_datasets['Última actualización'] = pd.to_datetime(
        api_datasets['Fecha de actualización:'].fillna(api_datasets['Fecha de incorporación al catálogo:']), 
        errors='coerce'
    )
    api_datasets['Días desde actualización'] = (datetime.now() - api_datasets['Última actualización']).dt.days

    # Análisis de datos
    total_apis = len(api_datasets)
    apis_por_sector = api_datasets['Sector'].value_counts().to_dict()
    apis_por_frecuencia = api_datasets['Frecuencia de actualización:'].value_counts().to_dict()
    
    # Análisis de actualización
    apis_actualizadas = {
        'actualizadas_30_dias': len(api_datasets[api_datasets['Días desde actualización'] <= 30]),
        'actualizadas_90_dias': len(api_datasets[api_datasets['Días desde actualización'] <= 90]),
        'actualizadas_180_dias': len(api_datasets[api_datasets['Días desde actualización'] <= 180]),
        'sin_actualizar_180_dias': len(api_datasets[api_datasets['Días desde actualización'] > 180])
    }

    # Preparar datos para gráficos
    chart_data = {
        'sectores': apis_por_sector,
        'frecuencias': apis_por_frecuencia,
        'actualizacion': apis_actualizadas
    }
    
    # Generar el HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo de APIs - Datos Madrid</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .container {{ margin-top: 2rem; }}
            .filters {{ margin-bottom: 1rem; }}
            .table-responsive {{ margin-top: 1rem; }}
            .badge {{ margin-right: 0.5rem; }}
            .fecha-actualizacion {{ 
                color: #666;
                font-size: 0.9em;
            }}
            .chart-container {{
                position: relative;
                height: 300px;
                margin-bottom: 2rem;
            }}
            .stats-card {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">Catálogo de APIs - Datos Madrid</h1>
            
            <!-- Resumen y Estadísticas -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Resumen del Catálogo</h5>
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="stats-card">
                                        <h6>Total de APIs</h6>
                                        <h3>{total_apis}</h3>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="stats-card">
                                        <h6>Actualizadas (30 días)</h6>
                                        <h3>{apis_actualizadas['actualizadas_30_dias']}</h3>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="stats-card">
                                        <h6>Actualizadas (90 días)</h6>
                                        <h3>{apis_actualizadas['actualizadas_90_dias']}</h3>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="stats-card">
                                        <h6>Sin actualizar (>180 días)</h6>
                                        <h3>{apis_actualizadas['sin_actualizar_180_dias']}</h3>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gráficos -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Distribución por Sector</h5>
                            <div class="chart-container">
                                <canvas id="sectorChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Frecuencia de Actualización</h5>
                            <div class="chart-container">
                                <canvas id="frecuenciaChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Filtros -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Filtros</h5>
                            <div class="row">
                                <div class="col-md-4">
                                    <label for="frecuencia" class="form-label">Frecuencia</label>
                                    <select class="form-select" id="frecuencia">
                                        <option value="">Todas</option>
                                        {generate_options(api_datasets['Frecuencia de actualización:'].unique())}
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label for="sector" class="form-label">Sector</label>
                                    <select class="form-select" id="sector">
                                        <option value="">Todos</option>
                                        {generate_options(api_datasets['Sector'].unique())}
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label for="formato" class="form-label">Formato</label>
                                    <select class="form-select" id="formato">
                                        <option value="">Todos</option>
                                        {generate_options(api_datasets['Formatos'].unique())}
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabla de Datos -->
            <div class="table-responsive">
                <table id="apiTable" class="table table-striped">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Sector</th>
                            <th>Frecuencia</th>
                            <th>Última actualización</th>
                            <th>Formatos</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_table_rows(api_datasets)}
                    </tbody>
                </table>
            </div>
        </div>

        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js"></script>
        <script>
            // Datos para los gráficos
            const chartData = {json.dumps(chart_data)};

            // Gráfico de sectores
            new Chart(document.getElementById('sectorChart'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(chartData.sectores),
                    datasets: [{{
                        data: Object.values(chartData.sectores),
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                            '#FF9F40', '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right'
                        }}
                    }}
                }}
            }});

            // Gráfico de frecuencias
            new Chart(document.getElementById('frecuenciaChart'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(chartData.frecuencias),
                    datasets: [{{
                        label: 'Número de APIs',
                        data: Object.values(chartData.frecuencias),
                        backgroundColor: '#36A2EB'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            // Configuración de DataTables
            $(document).ready(function() {{
                var table = $('#apiTable').DataTable({{
                    language: {{
                        url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
                    }},
                    pageLength: 25,
                    order: [[3, 'desc']]
                }});

                // Filtros
                $('#frecuencia, #sector, #formato').on('change', function() {{
                    table.draw();
                }});

                $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {{
                    var frecuencia = $('#frecuencia').val();
                    var sector = $('#sector').val();
                    var formato = $('#formato').val();

                    var rowFrecuencia = data[2];
                    var rowSector = data[1];
                    var rowFormato = data[4];

                    if (frecuencia && rowFrecuencia !== frecuencia) return false;
                    if (sector && rowSector !== sector) return false;
                    if (formato && !rowFormato.includes(formato)) return false;

                    return true;
                }});
            }});
        </script>
    </body>
    </html>
    """

    # Guardar el archivo HTML
    with open('api_catalog.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Reporte HTML generado: api_catalog.html")

def generate_options(options):
    """Genera las opciones para los selectores de filtros"""
    options = sorted([opt for opt in options if pd.notna(opt)])
    return '\n'.join([f'<option value="{opt}">{opt}</option>' for opt in options])

def generate_table_rows(df):
    """Genera las filas de la tabla HTML"""
    rows = []
    for _, row in df.iterrows():
        formatos = row['Formatos'].split(',') if pd.notna(row['Formatos']) else []
        formatos_html = ' '.join([f'<span class="badge bg-info">{f.strip()}</span>' for f in formatos])
        
        # Usar fecha de actualización si existe, sino usar fecha de incorporación
        fecha_actualizacion = row['Fecha de actualización:'] if pd.notna(row['Fecha de actualización:']) else row['Fecha de incorporación al catálogo:']
        ultima_actualizacion = pd.to_datetime(fecha_actualizacion, errors='coerce').strftime('%d/%m/%Y') if pd.notna(fecha_actualizacion) else 'N/A'
        
        # Añadir indicador si es fecha de incorporación
        if pd.isna(row['Fecha de actualización:']) and pd.notna(row['Fecha de incorporación al catálogo:']):
            ultima_actualizacion = f"{ultima_actualizacion} <span class='fecha-actualizacion'>(incorporación)</span>"
        
        rows.append(f"""
            <tr>
                <td>{row['Nombre']}</td>
                <td>{row['Sector']}</td>
                <td>{row['Frecuencia de actualización:']}</td>
                <td>{ultima_actualizacion}</td>
                <td>{formatos_html}</td>
                <td>
                    <a href="{row['URL']}" target="_blank" class="btn btn-sm btn-primary">Ver API</a>
                </td>
            </tr>
        """)
    return '\n'.join(rows)

if __name__ == '__main__':
    generate_html_report() 