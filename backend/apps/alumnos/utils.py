"""
Utilidades para procesamiento de archivos Excel de alumnos.
"""

import pandas as pd
from io import BytesIO
from typing import Tuple, List, Dict


def procesar_excel_alumnos(archivo, programa_educativo_id: int) -> Tuple[List[Dict], List[str]]:
    """
    Procesa archivo Excel con listado de alumnos.
    
    Args:
        archivo: Archivo Excel subido
        programa_educativo_id: ID del programa educativo
    
    Returns:
        Tuple con lista de datos de alumnos y lista de errores
    """
    errores = []
    alumnos_data = []
    
    try:
        # Leer archivo Excel
        df = pd.read_excel(BytesIO(archivo.read()), engine='openpyxl')
        
        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()
        
        # Mapeo de columnas esperadas
        columnas_requeridas = {
            'matricula': ['matricula', 'matrícula', 'no_control', 'numero_control'],
            'nombre': ['nombre', 'nombres', 'name'],
            'apellido_paterno': ['apellido_paterno', 'paterno', 'apellido1', 'primer_apellido'],
            'semestre': ['semestre', 'semester', 'nivel'],
        }
        
        columnas_opcionales = {
            'apellido_materno': ['apellido_materno', 'materno', 'apellido2', 'segundo_apellido'],
            'email': ['email', 'correo', 'correo_electronico', 'e-mail'],
            'telefono': ['telefono', 'teléfono', 'cel', 'celular', 'phone'],
        }
        
        # Encontrar columnas en el archivo
        columnas_mapeadas = {}
        
        for campo, opciones in columnas_requeridas.items():
            encontrada = None
            for opcion in opciones:
                if opcion in df.columns:
                    encontrada = opcion
                    break
            if encontrada:
                columnas_mapeadas[campo] = encontrada
            else:
                errores.append(f"Columna requerida '{campo}' no encontrada")
        
        for campo, opciones in columnas_opcionales.items():
            for opcion in opciones:
                if opcion in df.columns:
                    columnas_mapeadas[campo] = opcion
                    break
        
        if errores:
            return [], errores
        
        # Procesar filas
        for idx, row in df.iterrows():
            try:
                alumno = {
                    'matricula': str(row[columnas_mapeadas['matricula']]).strip(),
                    'nombre': str(row[columnas_mapeadas['nombre']]).strip(),
                    'apellido_paterno': str(row[columnas_mapeadas['apellido_paterno']]).strip(),
                    'semestre': int(row[columnas_mapeadas['semestre']]),
                    'programa_educativo_id': programa_educativo_id,
                }
                
                # Campos opcionales
                if 'apellido_materno' in columnas_mapeadas:
                    valor = row.get(columnas_mapeadas['apellido_materno'], '')
                    alumno['apellido_materno'] = str(valor).strip() if pd.notna(valor) else ''
                
                if 'email' in columnas_mapeadas:
                    valor = row.get(columnas_mapeadas['email'], '')
                    alumno['email'] = str(valor).strip() if pd.notna(valor) else ''
                
                if 'telefono' in columnas_mapeadas:
                    valor = row.get(columnas_mapeadas['telefono'], '')
                    alumno['telefono'] = str(valor).strip() if pd.notna(valor) else ''
                
                # Validaciones básicas
                if not alumno['matricula'] or alumno['matricula'] == 'nan':
                    errores.append(f"Fila {idx + 2}: Matrícula vacía")
                    continue
                
                if not alumno['nombre'] or alumno['nombre'] == 'nan':
                    errores.append(f"Fila {idx + 2}: Nombre vacío")
                    continue
                
                alumnos_data.append(alumno)
                
            except Exception as e:
                errores.append(f"Fila {idx + 2}: Error procesando - {str(e)}")
        
    except Exception as e:
        errores.append(f"Error leyendo archivo: {str(e)}")
    
    return alumnos_data, errores


def generar_plantilla_alumnos() -> BytesIO:
    """
    Genera plantilla Excel para importar alumnos.
    
    Returns:
        BytesIO con archivo Excel
    """
    df = pd.DataFrame(columns=[
        'Matrícula',
        'Nombre',
        'Apellido Paterno',
        'Apellido Materno',
        'Email',
        'Teléfono',
        'Semestre'
    ])
    
    # Agregar ejemplo
    df.loc[0] = ['A12345678', 'Juan', 'Pérez', 'García', 'juan@email.com', '5512345678', 1]
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Alumnos')
    
    output.seek(0)
    return output
