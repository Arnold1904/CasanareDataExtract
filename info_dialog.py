# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfoDialog
                                 A QGIS plugin
 Ventana informativa para el plugin Casanare Data Extract
                             -------------------
        begin                : 2025-09-23
        version              : 1.0.0
        autores              : Arnold Julián Mesa Valcárcel
                               Cristian Leandro Camargo Pinilla
                               Ildefonso Narváez Ortiz
        copyright            : (C) 2025 Universidad Internacional del
                               Trópico Americano - Unitrópico
        email                : ingsistemas@unitropico.edu.co
 ***************************************************************************/
"""

from qgis.PyQt import QtWidgets, QtCore, QtGui
from qgis.PyQt.QtCore import Qt


class InfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        """Constructor para la ventana de información"""
        super(InfoDialog, self).__init__(parent)
        self.setupUi()
    
    def setupUi(self):
        """Configurar la interfaz de usuario"""
        self.setObjectName("InfoDialog")
        self.setWindowTitle("Información del Plugin - Casanare Data Extract")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.resize(700, 500)
        
        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Scroll Area para contenido largo
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        
        # Título principal
        title_label = QtWidgets.QLabel("Casanare Data Extract")
        title_font = QtGui.QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E7D32; margin: 10px;")
        scroll_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QtWidgets.QLabel("Plugin para extraer y visualizar datos climáticos de Casanare")
        subtitle_font = QtGui.QFont()
        subtitle_font.setPointSize(12)
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        scroll_layout.addWidget(subtitle_label)
        
        # Separador
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        scroll_layout.addWidget(line)
        
        # Sección: Funcionalidad del Plugin
        func_title = QtWidgets.QLabel("🔧 Funcionalidades del Plugin")
        func_title.setFont(self._get_section_font())
        func_title.setStyleSheet("color: #1976D2; margin: 15px 0 10px 0;")
        scroll_layout.addWidget(func_title)
        
        func_text = QtWidgets.QLabel("""
Este plugin permite consultar y visualizar series climáticas mensuales históricas (1981–2022) del departamento de Casanare, Colombia.

Principales características:
• Descarga de datos: obtiene los datos directamente del servidor oficial de WorldClim y conserva solo el recorte de Casanare
• Visualización interactiva: mapa clickeable para seleccionar puntos de interés
• 4 variables climáticas: precipitación, temperatura mínima, máxima y evapotranspiración potencial
• Series temporales: gráficos dinámicos con datos históricos
• Exportación múltiple: datos y gráficos en formatos CSV, Excel, PNG y PDF
• Búsqueda por coordenadas: ingreso manual de longitud y latitud
• Filtrado temporal: selección de rangos de años específicos
        """)
        func_text.setWordWrap(True)
        func_text.setStyleSheet("margin: 0 20px; line-height: 1.4;")
        scroll_layout.addWidget(func_text)
        
        # Sección: Datos y Fuente
        data_title = QtWidgets.QLabel("📊 Fuente de los Datos")
        data_title.setFont(self._get_section_font())
        data_title.setStyleSheet("color: #1976D2; margin: 15px 0 10px 0;")
        scroll_layout.addWidget(data_title)
        
        data_text = QtWidgets.QLabel("""
<b>Origen:</b> WorldClim 2.1 – datos históricos mensuales (CRU-TS 4.09 reescalado con WorldClim 2.1)<br>
<b>Sitio web:</b> <a href="https://www.worldclim.org/data/monthlywth.html" style="color: #1976D2;">https://www.worldclim.org/data/monthlywth.html</a><br>
<br>
<b>Especificaciones técnicas:</b><br>
• <b>Periodo:</b> enero de 1981 a diciembre de 2022 (504 meses)<br>
• <b>Resolución espacial:</b> 2.5 minutos de arco (≈4.6 km)<br>
• <b>Cobertura:</b> departamento de Casanare, Colombia<br>
• <b>Formato original:</b> GeoTIFF mensual global<br>
<br>
<b>Variables incluidas:</b><br>
• <b>Precipitación (PP):</b> precipitación total mensual (mm)<br>
• <b>Temperatura mínima (TMIN):</b> temperatura mínima media mensual (°C)<br>
• <b>Temperatura máxima (TMAX):</b> temperatura máxima media mensual (°C)<br>
• <b>Evapotranspiración (ETP):</b> evapotranspiración potencial mensual (mm), calculada por el plugin
con el método de Hargreaves-Samani (FAO-56) a partir de TMIN y TMAX<br>
<br>
<b>Citas:</b><br>
Fick, S.E. y R.J. Hijmans, 2017. WorldClim 2: new 1km spatial resolution climate surfaces for global
land areas. International Journal of Climatology 37 (12): 4302-4315.<br>
Harris, I., Osborn, T.J., Jones, P.D., Lister, D.H., 2020. Version 4 of the CRU TS monthly
high-resolution gridded multivariate climate dataset. Scientific Data 7: 109.
        """)
        data_text.setWordWrap(True)
        data_text.setOpenExternalLinks(True)
        data_text.setStyleSheet("margin: 0 20px; line-height: 1.4;")
        scroll_layout.addWidget(data_text)
        
        # Sección: WorldClim Info
        worldclim_title = QtWidgets.QLabel("🌍 Acerca de WorldClim")
        worldclim_title.setFont(self._get_section_font())
        worldclim_title.setStyleSheet("color: #1976D2; margin: 15px 0 10px 0;")
        scroll_layout.addWidget(worldclim_title)
        
        worldclim_text = QtWidgets.QLabel("""
WorldClim es una base de datos de variables climáticas globales de alta resolución espacial que se puede usar para mapeo y modelado espacial en un SIG o con otros programas informáticos.

Condiciones de uso: los datos de WorldClim son de libre uso académico y no comercial; su redistribución o uso comercial requiere autorización previa de sus autores. Por esta razón el plugin no incluye los datos: cada usuario los descarga directamente desde WorldClim.
        """)
        worldclim_text.setWordWrap(True)
        worldclim_text.setStyleSheet("margin: 0 20px; line-height: 1.4;")
        scroll_layout.addWidget(worldclim_text)
        
        # Sección: Información técnica
        tech_title = QtWidgets.QLabel("⚙️ Información Técnica")
        tech_title.setFont(self._get_section_font())
        tech_title.setStyleSheet("color: #1976D2; margin: 15px 0 10px 0;")
        scroll_layout.addWidget(tech_title)
        
        tech_text = QtWidgets.QLabel("""
<b>Autores:</b> Arnold Julián Mesa Valcárcel, Cristian Leandro Camargo Pinilla, Ildefonso Narváez Ortiz<br>
<b>Titular:</b> Universidad Internacional del Trópico Americano – Unitrópico<br>
<b>Grupo de investigación:</b> TICTRÓPICO<br>
<b>Contacto:</b> ingsistemas@unitropico.edu.co<br>
<b>Versión del plugin:</b> 1.0.0<br>
<b>Compatible con:</b> QGIS 3.10 o superior<br>
<b>Lenguaje:</b> Python<br>
<b>Licencia:</b> GNU General Public License v2 o posterior<br>
<br>
<b>Dependencias principales:</b><br>
• NumPy: manejo de arreglos multidimensionales<br>
• Matplotlib: generación de gráficos<br>
• Pandas: exportación de datos tabulares (Excel requiere además openpyxl)<br>
• GDAL y API de QGIS: lectura de los GeoTIFF, descarga y tareas en segundo plano
        """)
        tech_text.setWordWrap(True)
        tech_text.setStyleSheet("margin: 0 20px; line-height: 1.4;")
        scroll_layout.addWidget(tech_text)
        
        # Espacio adicional al final
        scroll_layout.addStretch()
        
        # Configurar scroll area
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Botón de cerrar
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QtWidgets.QPushButton("Cerrar")
        close_button.setMinimumSize(100, 30)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
            }
            QLabel {
                background-color: transparent;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
    
    def _get_section_font(self):
        """Retorna la fuente para los títulos de sección"""
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        return font