"""
Procesadores de archivos Excel de reportes.
"""

import pandas as pd
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Tuple, Any

from apps.alumnos.models import Alumno


def procesar_reporte_individual(archivo, reporte) -> Tuple[List[Dict], List[str]]:
    """
    Procesa archivo Excel de reporte individual.
    
    Args:
        archivo: Archivo Excel
        reporte: Instancia de Reporte
    
    Returns:
        Tuple con lista de datos extraídos y lista de errores
    """
    errores = []
    datos = []
    
    try:
        df = pd.read_excel(BytesIO(archivo.read()), engine='openpyxl')
        df.columns = df.columns.str.strip().str.lower()
        
        # Mapeo de columnas
        columnas = {
            'matricula': ['matricula', 'matrícula', 'no_control'],
            'asistencia': ['asistencia', 'nivel_asistencia'],
            'rendimiento': ['rendimiento', 'nivel_rendimiento'],
            'materias_riesgo': ['materias_riesgo', 'materias', 'materias_reprobacion'],
            'observaciones': ['observaciones', 'comentarios', 'notas'],
            'fecha_sesion': ['fecha_sesion', 'fecha', 'date'],
        }
        
        col_map = {}
        for campo, opciones in columnas.items():
            for opcion in opciones:
                if opcion in df.columns:
                    col_map[campo] = opcion
                    break
        
        if 'matricula' not in col_map:
            return [], ['Columna de matrícula no encontrada']
        
        # Obtener alumnos del tutor
        alumnos_tutor = {
            a.matricula: a for a in 
            Alumno.objects.filter(tutor=reporte.tutor, activo=True)
        }
        
        for idx, row in df.iterrows():
            try:
                matricula = str(row[col_map['matricula']]).strip()
                
                if matricula not in alumnos_tutor:
                    errores.append(f"Fila {idx + 2}: Alumno {matricula} no asignado al tutor")
                    continue
                
                dato = {
                    'reporte': reporte,
                    'alumno': alumnos_tutor[matricula],
                }
                
                # Campos opcionales
                if 'asistencia' in col_map:
                    valor = str(row.get(col_map['asistencia'], '')).lower().strip()
                    if valor in ['excelente', 'buena', 'regular', 'deficiente']:
                        dato['asistencia'] = valor
                
                if 'rendimiento' in col_map:
                    valor = str(row.get(col_map['rendimiento'], '')).lower().strip()
                    if valor in ['alto', 'medio', 'bajo', 'muy_bajo']:
                        dato['rendimiento'] = valor
                
                if 'materias_riesgo' in col_map:
                    valor = row.get(col_map['materias_riesgo'], '')
                    dato['materias_riesgo'] = str(valor) if pd.notna(valor) else ''
                
                if 'observaciones' in col_map:
                    valor = row.get(col_map['observaciones'], '')
                    dato['observaciones'] = str(valor) if pd.notna(valor) else ''
                
                if 'fecha_sesion' in col_map:
                    valor = row.get(col_map['fecha_sesion'])
                    if pd.notna(valor):
                        if isinstance(valor, datetime):
                            dato['fecha_sesion'] = valor.date()
                        else:
                            try:
                                dato['fecha_sesion'] = pd.to_datetime(valor).date()
                            except Exception as e:
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.warning(f"No se pudo parsear fecha individual '{valor}': {str(e)}")
                
                # Determinar si requiere seguimiento - Analiza múltiples factores
                rendimiento_bajo = dato.get('rendimiento') in ['bajo', 'muy_bajo']
                asistencia_baja = dato.get('asistencia') in ['regular', 'deficiente']
                tiene_materias_riesgo = bool(dato.get('materias_riesgo', '').strip())
                
                if rendimiento_bajo or asistencia_baja or tiene_materias_riesgo:
                    dato['requiere_seguimiento'] = True
                
                datos.append(dato)
                
            except Exception as e:
                errores.append(f"Fila {idx + 2}: Error - {str(e)}")
        
    except Exception as e:
        errores.append(f"Error leyendo archivo: {str(e)}")
    
    return datos, errores


def procesar_reporte_grupal(archivo, reporte) -> Tuple[Dict, List[str]]:
    """
    Procesa archivo Excel de reporte grupal.
    
    Args:
        archivo: Archivo Excel
        reporte: Instancia de Reporte
    
    Returns:
        Tuple con diccionario de datos y lista de errores
    """
    errores = []
    datos = {}
    
    try:
        df = pd.read_excel(BytesIO(archivo.read()), engine='openpyxl')
        
        # Buscar datos en formato clave-valor
        for idx, row in df.iterrows():
            if len(row) >= 2:
                clave = str(row.iloc[0]).lower().strip()
                valor = row.iloc[1]
                
                if 'alumnos atendidos' in clave or 'asistieron' in clave:
                    datos['num_alumnos_atendidos'] = int(valor) if pd.notna(valor) else 0
                
                elif 'total alumnos' in clave or 'grupo' in clave:
                    datos['num_alumnos_grupo'] = int(valor) if pd.notna(valor) else 0
                
                elif 'temas' in clave:
                    datos['temas_tratados'] = str(valor) if pd.notna(valor) else ''
                
                elif 'problem' in clave:
                    datos['problematicas_detectadas'] = str(valor) if pd.notna(valor) else ''
                
                elif 'observ' in clave or 'comentarios' in clave:
                    datos['observaciones'] = str(valor) if pd.notna(valor) else ''
                
                elif 'fecha' in clave:
                    if pd.notna(valor):
                        if isinstance(valor, datetime):
                            datos['fecha_sesion'] = valor.date()
                        else:
                            try:
                                datos['fecha_sesion'] = pd.to_datetime(valor).date()
                            except Exception as e:
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.warning(f"No se pudo parsear fecha grupal '{valor}': {str(e)}")
        
        # Buscar lista de alumnos en riesgo (con flexibilidad en nombramiento)
        cols_bajas = df.columns.str.lower().str.strip().tolist()
        col_riesgo = next((col for col in cols_bajas if 'riesgo' in col or 'problema' in col), None)
        
        if col_riesgo:
            col_idx = cols_bajas.index(col_riesgo)
            matriculas = df.iloc[:, col_idx].dropna().tolist()
            
            alumnos_ids = list(
                Alumno.objects.filter(
                    matricula__in=[str(m).strip() for m in matriculas],
                    tutor=reporte.tutor
                ).values_list('id', flat=True)
            )
            datos['alumnos_riesgo_ids'] = alumnos_ids
        
        datos['reporte'] = reporte
        
    except Exception as e:
        errores.append(f"Error procesando archivo: {str(e)}")
    
    return datos, errores


def generar_plantilla_reporte(tipo_reporte: str) -> BytesIO:
    """
    Genera plantilla Excel para un tipo de reporte.
    
    Args:
        tipo_reporte: Tipo de reporte
    
    Returns:
        BytesIO con archivo Excel
    """
    output = BytesIO()
    
    if tipo_reporte.startswith('ind_'):
        # Plantilla individual
        df = pd.DataFrame(columns=[
            'Matrícula',
            'Asistencia',
            'Rendimiento',
            'Materias en Riesgo',
            'Observaciones',
            'Fecha Sesión'
        ])
        df.loc[0] = [
            'A12345678', 'Buena', 'Medio', 
            'Cálculo, Física', 'Requiere asesoría adicional',
            datetime.now().strftime('%Y-%m-%d')
        ]
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Reporte Individual')
            
            # Agregar hoja de instrucciones
            instrucciones = pd.DataFrame({
                'Campo': ['Matrícula', 'Asistencia', 'Rendimiento', 'Materias en Riesgo', 'Observaciones', 'Fecha Sesión'],
                'Descripción': [
                    'Matrícula del alumno',
                    'Valores: Excelente, Buena, Regular, Deficiente',
                    'Valores: Alto, Medio, Bajo, Muy_Bajo',
                    'Lista de materias separadas por coma',
                    'Comentarios adicionales',
                    'Formato: YYYY-MM-DD'
                ]
            })
            instrucciones.to_excel(writer, index=False, sheet_name='Instrucciones')
    
    else:
        # Plantilla grupal
        df = pd.DataFrame({
            'Campo': [
                'Fecha de Sesión',
                'Alumnos Atendidos',
                'Total Alumnos Grupo',
                'Temas Tratados',
                'Problemáticas Detectadas',
                'Observaciones'
            ],
            'Valor': [
                datetime.now().strftime('%Y-%m-%d'),
                25,
                30,
                'Tema 1, Tema 2',
                'Descripción de problemáticas',
                'Observaciones generales'
            ],
            '': ['', '', '', '', '', ''],
            'Alumnos en Riesgo': [
                'A12345678', 'A87654321', '', '', '', ''
            ]
        })
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Reporte Grupal')
            
            # Agregar hoja de instrucciones
            instrucciones = pd.DataFrame({
                'Campo': ['Fecha de Sesión', 'Alumnos Atendidos', 'Total Alumnos', 'Temas Tratados', 'Problemáticas Detectadas', 'Observaciones', 'Alumnos en Riesgo'],
                'Descripción': [
                    'Formato: YYYY-MM-DD',
                    'Número de alumnos que asistieron a la sesión',
                    'El número de integrantes del grupo',
                    'Lista de temas tratados',
                    'Problemáticas identificadas a nivel grupal',
                    'Comentarios',
                    'En la última columna, ponga las matrículas de alumnos que muestran algún riesgo'
                ]
            })
            instrucciones.to_excel(writer, index=False, sheet_name='Instrucciones')
            
    output.seek(0)
    return output
