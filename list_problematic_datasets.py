import pandas as pd
import os

def main():
    csv_path = 'catalogo.csv'
    if not os.path.exists(csv_path):
        print(f'No se encontró el archivo {csv_path}. Descárgalo primero.')
        return

    # Leer el CSV (el delimitador es ';')
    df = pd.read_csv(csv_path, delimiter=';', encoding='latin1')

    # Filtrar solo los datasets que tienen 'API' en la columna 'Formatos'
    api_datasets = df[df['Formatos'].str.contains('API', case=False, na=False)]

    # Criterios de calidad
    problematic = []
    for _, row in api_datasets.iterrows():
        problems = []
        if not isinstance(row['Nombre'], str) or len(row['Nombre'].strip()) < 5:
            problems.append('Nombre muy corto o vacío')
        if not isinstance(row['Sector'], str) or not row['Sector'].strip():
            problems.append('Sin sector')
        if not isinstance(row['Palabras clave:'], str) or len(row['Palabras clave:'].split(',')) < 3:
            problems.append('Pocas palabras clave')
        if not isinstance(row['Licencia:'], str) or not row['Licencia:'].strip():
            problems.append('Sin licencia')
        if not isinstance(row['Frecuencia de actualización:'], str) or not row['Frecuencia de actualización:'].strip():
            problems.append('Sin frecuencia')
        if not isinstance(row['Formatos'], str) or len(row['Formatos'].split(',')) < 2:
            problems.append('Pocos formatos')
        if problems:
            problematic.append({
                'Nombre': row['Nombre'],
                'URL': row['URL'] if 'URL' in row else '',
                'Problemas': problems
            })

    if not problematic:
        print('No se encontraron APIs problemáticas.')
        return

    print(f"\nSe encontraron {len(problematic)} APIs problemáticas:\n")
    for ds in problematic:
        print(f"Nombre: {ds['Nombre']}")
        print(f"URL: {ds['URL']}")
        print(f"Problemas: {', '.join(ds['Problemas'])}")
        print('-' * 60)

if __name__ == '__main__':
    main() 