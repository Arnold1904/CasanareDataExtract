# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Casanare Data Extract
                                 A QGIS plugin
 Plugin para extraer y visualizar datos climáticos de Casanare
                             -------------------
        begin                : 2025-06-18
        version              : 1.0.0
        autores              : Arnold Julián Mesa Valcárcel
                               Cristian Leandro Camargo Pinilla
                               Ildefonso Narváez Ortiz
        copyright            : (C) 2025 Universidad Internacional del
                               Trópico Americano - Unitrópico
        email                : ingsistemas@unitropico.edu.co
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

 Descarga, recorte y preparación de los datos climáticos.

 Los datos NO se distribuyen con el plugin: la licencia de WorldClim no
 permite su redistribución. Cada usuario los descarga directamente desde
 el servidor oficial de WorldClim a su equipo. De cada archivo mensual
 global solo se conserva la ventana que cubre el departamento de Casanare.

 Fuente: CRU-TS 4.09 (Harris et al., 2020) reescalado con WorldClim 2.1
 (Fick y Hijmans, 2017), resolución de 2.5 minutos de arco.
 https://www.worldclim.org/data/monthlywth.html
"""

import calendar
import math
import os
import struct
import time
import zlib
from datetime import datetime

import numpy as np

URL_WORLDCLIM = ('https://geodata.ucdavis.edu/climate/worldclim/2_1/hist/cts4.09/'
                 'wc2.1_cruts4.09_2.5m_{var}_{decada}.zip')
NOMBRE_TIF = 'wc2.1_cruts4.09_2.5m_{var}_{anio}-{mes:02d}.tif'
DECADAS = ['1980-1989', '1990-1999', '2000-2009', '2010-2019', '2020-2024']

ANIO_INICIO = 1981
ANIO_FIN = 2022

# Ventana de Casanare dentro de la grilla global de 2.5' (8640 x 4320 celdas,
# esquina superior izquierda en -180, 90)
TAMANO_CELDA = 1.0 / 24.0
ESQUINA_X = -73.125
ESQUINA_Y = 6.375
COLUMNA_INICIO = 2565
FILA_INICIO = 2007
COLUMNAS = 81
FILAS = 52

# Variable del plugin -> variable de WorldClim
VARIABLES_WORLDCLIM = {'pp': 'prec', 'tmin': 'tmin', 'tmax': 'tmax'}
VARIABLES = ['pp', 'tmin', 'tmax', 'etp']

ARCHIVO_MASCARA = os.path.join(os.path.dirname(__file__), 'casanare_mask.npy')


def meses():
    """Lista de (año, mes) del periodo del plugin."""
    return [(anio, mes) for anio in range(ANIO_INICIO, ANIO_FIN + 1)
            for mes in range(1, 13)]


def fechas():
    """Fechas (primer día de cada mes) del periodo del plugin."""
    return [datetime(anio, mes, 1) for anio, mes in meses()]


def decada(anio):
    """Nombre de la década de WorldClim que contiene el año."""
    for nombre in DECADAS:
        inicio, fin = (int(a) for a in nombre.split('-'))
        if inicio <= anio <= fin:
            return nombre
    raise ValueError('Año fuera del rango de WorldClim: {}'.format(anio))


def mascara():
    """Máscara booleana (FILAS x COLUMNAS) de las celdas dentro de Casanare."""
    return np.load(ARCHIVO_MASCARA).astype(bool)


def celda_a_coordenadas(fila, columna):
    """Coordenadas (lon, lat) del centro de una celda."""
    lon = ESQUINA_X + (columna + 0.5) * TAMANO_CELDA
    lat = ESQUINA_Y - (fila + 0.5) * TAMANO_CELDA
    return lon, lat


def coordenadas_a_celda(lon, lat):
    """Celda (fila, columna) que contiene unas coordenadas, o None si está fuera."""
    columna = int(math.floor((lon - ESQUINA_X) / TAMANO_CELDA))
    fila = int(math.floor((ESQUINA_Y - lat) / TAMANO_CELDA))
    if 0 <= fila < FILAS and 0 <= columna < COLUMNAS:
        return fila, columna
    return None


def directorio_datos():
    """Carpeta del perfil de QGIS donde se guardan los datos descargados."""
    from qgis.core import QgsApplication
    return os.path.join(QgsApplication.qgisSettingsDirPath(), 'casanare_data_extract')


def ruta_variable(destino, variable):
    return os.path.join(destino, 'datos_{}.npy'.format(variable))


def datos_disponibles(destino):
    return all(os.path.exists(ruta_variable(destino, v)) for v in VARIABLES)


def cargar_datos(destino):
    """Carga los arreglos (meses x FILAS x COLUMNAS) de cada variable."""
    return {v: np.load(ruta_variable(destino, v)) for v in VARIABLES}


# --- Excel -----------------------------------------------------------------

def escribir_xlsx(ruta, encabezados, filas):
    """Escribe una hoja de Excel (.xlsx) mínima sin depender de openpyxl.

    Los números se guardan como celdas numéricas y el resto como texto.
    """
    import zipfile
    from xml.sax.saxutils import escape

    def columna(i):
        letras = ''
        i += 1
        while i:
            i, r = divmod(i - 1, 26)
            letras = chr(65 + r) + letras
        return letras

    def celda(valor, ref):
        if isinstance(valor, (int, float, np.integer, np.floating)) and not (
                isinstance(valor, (float, np.floating)) and math.isnan(valor)):
            return '<c r="{}"><v>{}</v></c>'.format(ref, valor)
        return '<c r="{}" t="inlineStr"><is><t>{}</t></is></c>'.format(ref, escape(str(valor)))

    filas_xml = []
    for n, fila in enumerate([encabezados] + [list(f) for f in filas], start=1):
        celdas = ''.join(celda(v, '{}{}'.format(columna(i), n)) for i, v in enumerate(fila))
        filas_xml.append('<row r="{}">{}</row>'.format(n, celdas))
    hoja = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>{}</sheetData></worksheet>').format(''.join(filas_xml))
    archivos = {
        '[Content_Types].xml': (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'),
        '_rels/.rels': (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'),
        'xl/workbook.xml': (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Datos" sheetId="1" r:id="rId1"/></sheets></workbook>'),
        'xl/_rels/workbook.xml.rels': (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>'),
        'xl/worksheets/sheet1.xml': hoja,
    }
    with zipfile.ZipFile(ruta, 'w', zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in archivos.items():
            z.writestr(nombre, contenido)


# --- ETP -------------------------------------------------------------------

def radiacion_extraterrestre(lat, dia_juliano):
    """Radiación extraterrestre Ra en MJ m-2 dia-1 (FAO-56, ecuación 21)."""
    phi = np.radians(lat)
    dr = 1 + 0.033 * math.cos(2 * math.pi * dia_juliano / 365)
    delta = 0.409 * math.sin(2 * math.pi * dia_juliano / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * math.tan(delta), -1, 1))
    return (24 * 60 / math.pi) * 0.0820 * dr * (
        ws * np.sin(phi) * math.sin(delta) + np.cos(phi) * math.cos(delta) * np.sin(ws))


def etp_hargreaves(tmin, tmax):
    """Evapotranspiración potencial mensual (mm) por Hargreaves-Samani (FAO-56, ec. 52).

    ETo = 0.0023 (Tmedia + 17.8) (Tmax - Tmin)^0.5 · 0.408 Ra, en mm/día,
    multiplicada por los días del mes. Ra se evalúa a mitad de mes en la
    latitud del centro de cada fila.
    """
    latitudes = np.array([celda_a_coordenadas(f, 0)[1] for f in range(FILAS)])
    etp = np.full(tmin.shape, np.nan, dtype=np.float32)
    for i, (anio, mes) in enumerate(meses()):
        dias = calendar.monthrange(anio, mes)[1]
        dia_juliano = datetime(anio, mes, 15).timetuple().tm_yday
        ra = radiacion_extraterrestre(latitudes, dia_juliano)[:, None]
        tmedia = (tmin[i] + tmax[i]) / 2
        rango = np.sqrt(np.clip(tmax[i] - tmin[i], 0, None))
        etp[i] = 0.0023 * (tmedia + 17.8) * rango * 0.408 * ra * dias
    return etp


# --- Lectura de los ZIP de WorldClim por rangos HTTP -----------------------

def leer_indice_zip(descargar_rango, url):
    """Lee el directorio central de un ZIP remoto sin descargar el archivo completo.

    Devuelve {nombre: (metodo, tamano_comprimido, posicion_cabecera_local)}.
    """
    cola = descargar_rango(url, 'bytes=-65536')
    pos = cola.rfind(b'PK\x05\x06')
    if pos < 0:
        raise IOError('No se encontró el índice del archivo ZIP: {}'.format(url))
    tamano, inicio = struct.unpack('<II', cola[pos + 12:pos + 20])
    indice = descargar_rango(url, 'bytes={}-{}'.format(inicio, inicio + tamano - 1))
    miembros = {}
    p = 0
    while p + 46 <= len(indice) and indice[p:p + 4] == b'PK\x01\x02':
        metodo, = struct.unpack('<H', indice[p + 10:p + 12])
        comprimido, = struct.unpack('<I', indice[p + 20:p + 24])
        largo_nombre, largo_extra, largo_coment = struct.unpack('<HHH', indice[p + 28:p + 34])
        cabecera, = struct.unpack('<I', indice[p + 42:p + 46])
        nombre = indice[p + 46:p + 46 + largo_nombre].decode('utf-8')
        miembros[nombre] = (metodo, comprimido, cabecera)
        p += 46 + largo_nombre + largo_extra + largo_coment
    return miembros


def extraer_miembro(descargar_rango, url, miembro):
    """Descarga y descomprime un archivo individual de un ZIP remoto."""
    metodo, comprimido, cabecera = miembro
    local = descargar_rango(url, 'bytes={}-{}'.format(cabecera, cabecera + 29))
    largo_nombre, largo_extra = struct.unpack('<HH', local[26:30])
    inicio = cabecera + 30 + largo_nombre + largo_extra
    datos = descargar_rango(url, 'bytes={}-{}'.format(inicio, inicio + comprimido - 1))
    if metodo == 8:
        return zlib.decompress(datos, -15)
    if metodo == 0:
        return datos
    raise IOError('Método de compresión no soportado: {}'.format(metodo))


def descargar_rango_qgis(url, rango):
    """Descarga un rango de bytes usando la red de QGIS (respeta el proxy configurado)."""
    from qgis.core import QgsBlockingNetworkRequest
    from qgis.PyQt.QtCore import QUrl
    from qgis.PyQt.QtNetwork import QNetworkRequest
    solicitud = QNetworkRequest(QUrl(url))
    solicitud.setRawHeader(b'Range', rango.encode('ascii'))
    # No guardar los archivos globales en la caché de red de QGIS
    solicitud.setAttribute(QNetworkRequest.Attribute.CacheSaveControlAttribute, False)
    peticion = QgsBlockingNetworkRequest()
    if peticion.get(solicitud, True) != QgsBlockingNetworkRequest.ErrorCode.NoError:
        raise IOError(peticion.errorMessage())
    return bytes(peticion.reply().content())


def leer_ventana_gdal(contenido_tif):
    """Lee la ventana de Casanare de un GeoTIFF global en memoria."""
    import contextlib
    from osgeo import gdal
    # Excepciones de GDAL solo dentro de este bloque, sin cambiar la configuración global de QGIS
    excepciones = gdal.ExceptionMgr(useExceptions=True) if hasattr(gdal, 'ExceptionMgr') else contextlib.nullcontext()
    ruta = '/vsimem/casanare_{}.tif'.format(id(contenido_tif))
    with excepciones:
        gdal.FileFromMemBuffer(ruta, contenido_tif)
        try:
            dataset = gdal.Open(ruta)
            banda = dataset.GetRasterBand(1)
            ventana = banda.ReadAsArray(COLUMNA_INICIO, FILA_INICIO, COLUMNAS, FILAS).astype(np.float32)
            sin_dato = banda.GetNoDataValue()
            if sin_dato is not None:
                ventana[ventana == np.float32(sin_dato)] = np.nan
            dataset = None
        finally:
            gdal.Unlink(ruta)
    return ventana


def con_reintentos(descargar_rango, intentos=6, espera=10, cancelado=None):
    """Reintenta una descarga ante fallas temporales de red (espera creciente entre intentos)."""
    def envoltura(url, rango):
        for intento in range(intentos):
            try:
                return descargar_rango(url, rango)
            except IOError:
                if intento == intentos - 1 or (cancelado and cancelado()):
                    raise
                time.sleep(espera * (intento + 1))
    return envoltura


def descargar_datos(destino, descargar_rango=descargar_rango_qgis, leer_ventana=leer_ventana_gdal,
                    progreso=None, cancelado=None):
    """Descarga los meses que falten, recorta Casanare y genera los archivos finales.

    Cada mes recortado se guarda en una carpeta temporal, de modo que si la
    descarga se interrumpe puede reanudarse sin repetir lo ya descargado.
    Devuelve True si terminó, False si fue cancelada.
    """
    parciales = os.path.join(destino, 'parciales')
    descargar_rango = con_reintentos(descargar_rango, cancelado=cancelado)
    os.makedirs(parciales, exist_ok=True)
    lista_meses = meses()
    total = len(VARIABLES_WORLDCLIM) * len(lista_meses)
    hechos = 0

    for var_wc in VARIABLES_WORLDCLIM.values():
        for nombre_decada in DECADAS:
            pendientes = [(a, m) for a, m in lista_meses if decada(a) == nombre_decada]
            faltantes = [(a, m) for a, m in pendientes
                         if not os.path.exists(os.path.join(parciales, '{}_{}-{:02d}.npy'.format(var_wc, a, m)))]
            hechos += len(pendientes) - len(faltantes)
            if not faltantes:
                continue
            url = URL_WORLDCLIM.format(var=var_wc, decada=nombre_decada)
            indice = leer_indice_zip(descargar_rango, url)
            for anio, mes in faltantes:
                if cancelado and cancelado():
                    return False
                tif = extraer_miembro(descargar_rango, url,
                                      indice[NOMBRE_TIF.format(var=var_wc, anio=anio, mes=mes)])
                ventana = leer_ventana(tif)
                np.save(os.path.join(parciales, '{}_{}-{:02d}.npy'.format(var_wc, anio, mes)), ventana)
                hechos += 1
                if progreso:
                    progreso(hechos, total)

    dentro = mascara()
    datos = {}
    for variable, var_wc in VARIABLES_WORLDCLIM.items():
        arreglo = np.stack([np.load(os.path.join(parciales, '{}_{}-{:02d}.npy'.format(var_wc, a, m)))
                            for a, m in lista_meses]).astype(np.float32)
        arreglo[:, ~dentro] = np.nan
        datos[variable] = arreglo
    datos['etp'] = etp_hargreaves(datos['tmin'], datos['tmax'])
    datos['etp'][:, ~dentro] = np.nan

    for variable, arreglo in datos.items():
        np.save(ruta_variable(destino, variable), arreglo)
    for archivo in os.listdir(parciales):
        os.remove(os.path.join(parciales, archivo))
    os.rmdir(parciales)
    return True
