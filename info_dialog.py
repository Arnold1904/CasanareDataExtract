# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfoDialog
                                 A QGIS plugin
 Ventana informativa para el plugin Casanare Data Extract
                             -------------------
        begin                : 2025-09-23
        copyright            : (C) 2025 by Arnold Mesa
        email                : arnoldjulianmesa@gmail.com
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
Este plugin permite extraer y visualizar datos climáticos históricos del departamento de Casanare, Colombia.

Principales características:
• Visualización interactiva: Mapa clickeable para seleccionar puntos de interés
• 4 variables climáticas: Precipitación, temperatura mínima, máxima y evapotranspiración
• Series temporales: Gráficos dinámicos con datos históricos
• Exportación múltiple: Datos y gráficos en formatos CSV, Excel, PNG y PDF
• Búsqueda por coordenadas: Ingreso manual de latitud y longitud
• Filtrado temporal: Selección de rangos de años específicos
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
<b>Origen:</b> WorldClim - Global Climate Data
<b>Website:</b> <a href="https://worldclim.org/" style="color: #1976D2;">https://worldclim.org/</a>

<b>Especificaciones técnicas:</b>
• <b>Año base:</b> 1980
• <b>Resolución espacial:</b> ~1km² (30 arc-seconds)
• <b>Cobertura:</b> Departamento de Casanare, Colombia
• <b>Formato original:</b> Archivos raster (.tif)

<b>Variables incluidas:</b>
• <b>Precipitación (PP):</b> Precipitación mensual promedio (mm)
• <b>Temperatura mínima (TMIN):</b> Temperatura mínima mensual (°C)
• <b>Temperatura máxima (TMAX):</b> Temperatura máxima mensual (°C)
• <b>Evapotranspiración (ETP):</b> Evapotranspiración potencial (mm)
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
WorldClim es una base de datos de variables climáticas globales de alta resolución espacial que se puede usar para mapeo y modelado espacial. Estos datos se pueden usar para mapeo y modelado espacial en un SIG o con otros programas informáticos.

Características de WorldClim:
• Base de datos gratuita y de acceso libre
• Cobertura global con alta resolución espacial
• Datos interpolados de estaciones meteorológicas
• Ampliamente utilizado en investigación científica
• Actualizado regularmente con nuevos datos
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
<b>Desarrollador:</b> Arnold Mesa
<b>Email:</b> arnoldjulianmesa@gmail.com
<b>Versión del plugin:</b> 1.0
<b>Compatible with:</b> QGIS 3.0+
<b>Lenguaje:</b> Python
<b>Licencia:</b> GNU General Public License v2

<b>Dependencias principales:</b>
• NumPy: Manejo de arrays multidimensionales
• Matplotlib: Generación de gráficos
• Pandas: Manipulación de datos tabulares
• QGIS API: Integración con la plataforma GIS
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