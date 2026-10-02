# Casanare Data Extract

Plugin de QGIS para consultar y visualizar series climáticas mensuales (1981–2022) del departamento de Casanare, Colombia: precipitación, temperatura mínima, temperatura máxima y evapotranspiración potencial.

- Mapa interactivo de Casanare: clic sobre un punto o búsqueda por coordenadas.
- Serie temporal del punto en el rango de años elegido.
- Exportación a CSV, Excel, PNG y PDF.

## Datos

Los datos climáticos **no se incluyen** en el plugin: la licencia de WorldClim permite su uso académico y no comercial, pero no su redistribución. La primera vez que se abre el plugin, el botón **Descargar datos de WorldClim** obtiene los archivos mensuales del servidor oficial, conserva solo la ventana de Casanare (≈35 MB) y descarta el resto. Son unos 17 GB de tráfico; la descarga corre en segundo plano y puede reanudarse.

- Fuente: CRU-TS 4.09 (Harris et al., 2020) reescalado con WorldClim 2.1 (Fick y Hijmans, 2017), 2.5 minutos de arco. https://www.worldclim.org/data/monthlywth.html
- La evapotranspiración potencial la calcula el plugin con Hargreaves-Samani (FAO-56) a partir de las temperaturas mínima y máxima.
- `casanare_mask.npy` contiene únicamente la máscara de celdas del departamento.

## Requisitos

QGIS 3.10 o superior, incluido QGIS 4 (probado en QGIS 3.44 LTR y QGIS 4.2), con numpy, matplotlib y pandas, que vienen incluidos en QGIS. La exportación a Excel no requiere librerías adicionales.

## Autores

- Arnold Julián Mesa Valcárcel
- Cristian Leandro Camargo Pinilla
- Ildefonso Narváez Ortiz

Grupo de investigación TICTRÓPICO — convocatoria interna CIG 04 de 2024.

Copyright (C) 2025 Universidad Internacional del Trópico Americano – Unitrópico. Contacto: ingsistemas@unitropico.edu.co

## Licencia

GNU General Public License v2 o posterior (ver `LICENSE`). La estructura base del plugin fue generada con Plugin Builder (GPL).
