# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CasanareDataExtractDialog
                                 A QGIS plugin
 Plugin para extraer y visualizar datos climáticos de Casanare
 Estructura base generada con Plugin Builder (GPL):
 http://g-sherman.github.io/Qgis-Plugin-Builder/
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
"""

import os

import numpy as np
import matplotlib.pyplot as plt
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas  # Qt5 y Qt6
except ImportError:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # matplotlib < 3.5

from qgis.core import QgsApplication, QgsTask
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtCore
from qgis.PyQt.QtGui import QPixmap, QImage, QPainter, QColor

from . import data_manager as dm
from .info_dialog import InfoDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MyPlugin_dialog_base.ui'))

# Índice del combo de variables -> (clave de datos, nombre, unidades)
VARIABLES = [
    ('pp', 'Precipitación', 'mm'),
    ('tmin', 'Temperatura mínima', '°C'),
    ('tmax', 'Temperatura máxima', '°C'),
    ('etp', 'Evapotranspiración', 'mm'),
]


class TareaDescarga(QgsTask):
    """Descarga los datos de WorldClim en segundo plano."""

    def __init__(self, destino):
        super(TareaDescarga, self).__init__(
            'Casanare Data Extract: descarga de datos WorldClim', QgsTask.Flag.CanCancel)
        self.destino = destino
        self.error = None

    def run(self):
        try:
            return dm.descargar_datos(
                self.destino,
                progreso=lambda hechos, total: self.setProgress(100.0 * hechos / total),
                cancelado=self.isCanceled)
        except Exception as e:
            self.error = str(e)
            return False


class CasanareDataExtractDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CasanareDataExtractDialog, self).__init__(parent)
        self.setupUi(self)
        # Hacer el diálogo redimensionable y maximizable
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowMaximizeButtonHint | QtCore.Qt.WindowType.WindowMinimizeButtonHint)
        self.resize(1000, 800)

        self.datos = None
        self.tarea = None
        self.destino = dm.directorio_datos()
        self.dentro = dm.mascara()
        self.fechas = dm.fechas()
        self.fechas_str = [fecha.strftime('%Y-%m') for fecha in self.fechas]
        self.anios = sorted(set(fecha.year for fecha in self.fechas))
        self.selected_px = None
        self.selected_py = None
        self.selected_coords = None
        self.heatmap_mode = False

        # Poblar combos de años
        self.combo_anio_inicio.addItems([str(a) for a in self.anios])
        self.combo_anio_fin.addItems([str(a) for a in self.anios])
        self.combo_anio_inicio.setCurrentIndex(0)
        self.combo_anio_fin.setCurrentIndex(len(self.anios) - 1)

        # --- Matplotlib Figure ---
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        self.scroll_grafica = QtWidgets.QScrollArea()
        self.scroll_grafica.setWidget(self.canvas)
        self.scroll_grafica.setWidgetResizable(True)
        self.scroll_grafica.setMinimumHeight(300)  # espacio para las etiquetas de fecha
        self.scroll_grafica.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.layout().addWidget(self.scroll_grafica)
        self.label_grafica.hide()  # Ocultar QLabel, usar canvas

        # Botón para cambiar a mapa de calor debajo del mapa
        self.pushButton_heatmap = QtWidgets.QPushButton('Cambiar Color')
        main_layout = self.findChild(QtWidgets.QVBoxLayout, 'verticalLayout_main')
        main_layout.insertWidget(1, self.pushButton_heatmap)

        controls_layout = self.findChild(QtWidgets.QVBoxLayout, 'verticalLayout_controls')

        # Panel de descarga de datos (se muestra solo si faltan los datos)
        self.panel_descarga = QtWidgets.QWidget()
        descarga_layout = QtWidgets.QVBoxLayout(self.panel_descarga)
        descarga_layout.setContentsMargins(0, 0, 0, 0)
        self.label_descarga = QtWidgets.QLabel(
            'Descargue una sola vez los datos de WorldClim '
            '(≈17 GB de tráfico, ≈35 MB en disco). Puede interrumpir y reanudar la descarga.')
        self.label_descarga.setWordWrap(True)
        self.label_descarga.setMinimumHeight(self.label_descarga.fontMetrics().lineSpacing() * 4)
        self.pushButton_descargar = QtWidgets.QPushButton('Descargar datos de WorldClim')
        self.progress_descarga = QtWidgets.QProgressBar()
        self.progress_descarga.setRange(0, 100)
        self.progress_descarga.hide()
        descarga_layout.addWidget(self.label_descarga)
        descarga_layout.addWidget(self.pushButton_descargar)
        descarga_layout.addWidget(self.progress_descarga)
        controls_layout.insertWidget(0, self.panel_descarga)

        # Campos de coordenadas manuales en el panel derecho
        controls_layout.addWidget(QtWidgets.QLabel('Ingresar coordenadas manualmente:'))
        self.lineEdit_X = QtWidgets.QLineEdit()
        self.lineEdit_X.setPlaceholderText('Longitud, ejemplo: -71.6')
        self.lineEdit_X.setToolTip('Coordenada X (longitud)')
        controls_layout.addWidget(self.lineEdit_X)
        self.lineEdit_Y = QtWidgets.QLineEdit()
        self.lineEdit_Y.setPlaceholderText('Latitud, ejemplo: 5.4')
        self.lineEdit_Y.setToolTip('Coordenada Y (latitud)')
        controls_layout.addWidget(self.lineEdit_Y)
        self.pushButton_show = QtWidgets.QPushButton('Buscar por coordenadas')
        self.pushButton_show.setToolTip('Buscar el punto en el mapa usando las coordenadas ingresadas')
        controls_layout.addWidget(self.pushButton_show)

        # Conectar eventos
        self.pushButton_exportCsv.clicked.connect(self._export_csv)
        self.pushButton_exportExcel.clicked.connect(self._export_excel)
        self.pushButton_exportPng.clicked.connect(self._export_png)
        self.pushButton_exportPdf.clicked.connect(self._export_pdf)
        self.pushButton_info.clicked.connect(self._show_info)
        self.pushButton_show.clicked.connect(self._buscar_por_coordenadas)
        self.pushButton_heatmap.clicked.connect(self._toggle_heatmap)
        self.pushButton_descargar.clicked.connect(self._descargar_datos)
        self.label_map.mousePressEvent = self._on_map_click
        self.combo_variable.currentIndexChanged.connect(self._update_plot)
        self.combo_anio_inicio.currentIndexChanged.connect(self._update_plot)
        self.combo_anio_fin.currentIndexChanged.connect(self._update_plot)

        if dm.datos_disponibles(self.destino):
            self._cargar_datos()
        else:
            self._habilitar_controles(False)
            self.label_map.setText('Descargue los datos para ver el mapa')
            self._update_plot()

    # --- Datos ---------------------------------------------------------------

    def _habilitar_controles(self, habilitar):
        for widget in (self.combo_variable, self.combo_anio_inicio, self.combo_anio_fin,
                       self.pushButton_exportCsv, self.pushButton_exportExcel,
                       self.pushButton_exportPng, self.pushButton_exportPdf,
                       self.pushButton_heatmap, self.pushButton_show,
                       self.lineEdit_X, self.lineEdit_Y):
            widget.setEnabled(habilitar)
        self.panel_descarga.setVisible(not habilitar)

    def _cargar_datos(self):
        try:
            self.datos = dm.cargar_datos(self.destino)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos:\n{str(e)}")
            self._habilitar_controles(False)
            return
        # Mapa base: precipitación media mensual del periodo
        self.mapa_base = np.full(self.dentro.shape, np.nan, dtype=np.float32)
        self.mapa_base[self.dentro] = np.nanmean(self.datos['pp'][:, self.dentro], axis=0)
        self._habilitar_controles(True)
        self._update_map_pixmap()
        self._update_plot()

    def _descargar_datos(self):
        self.pushButton_descargar.setEnabled(False)
        self.progress_descarga.setValue(0)
        self.progress_descarga.show()
        self.tarea = TareaDescarga(self.destino)
        self.tarea.progressChanged.connect(lambda p: self.progress_descarga.setValue(int(p)))
        self.tarea.taskCompleted.connect(self._descarga_terminada)
        self.tarea.taskTerminated.connect(self._descarga_fallida)
        QgsApplication.taskManager().addTask(self.tarea)

    def _descarga_terminada(self):
        self.progress_descarga.hide()
        self.pushButton_descargar.setEnabled(True)
        self.label_map.setText('')
        self._cargar_datos()

    def _descarga_fallida(self):
        self.progress_descarga.hide()
        self.pushButton_descargar.setEnabled(True)
        error = self.tarea.error if self.tarea else None
        if error:
            mensaje = f"La descarga se detuvo:\n{error}\n\nPuede reanudarla con el mismo botón."
        else:
            mensaje = "La descarga fue cancelada. Puede reanudarla con el mismo botón."
        QtWidgets.QMessageBox.warning(self, "Descarga de datos", mensaje)

    def _serie_seleccionada(self):
        """Devuelve (nombre, unidades, fechas, serie) del punto y rango elegidos, o None."""
        if self.datos is None or self.selected_px is None:
            return None
        anio_ini = int(self.combo_anio_inicio.currentText())
        anio_fin = int(self.combo_anio_fin.currentText())
        if anio_ini > anio_fin:
            return None
        clave, var_name, units = VARIABLES[self.combo_variable.currentIndex()]
        indices = [i for i, f in enumerate(self.fechas) if anio_ini <= f.year <= anio_fin]
        serie = self.datos[clave][indices, self.selected_py, self.selected_px]
        return var_name, units, [self.fechas[i] for i in indices], serie

    def _datos_exportacion(self):
        """Construye el DataFrame a exportar, o muestra un aviso y devuelve None."""
        seleccion = self._serie_seleccionada()
        if seleccion is None:
            QtWidgets.QMessageBox.warning(
                self, "Error", "Seleccione un punto dentro de Casanare y un rango de años válido")
            return None
        try:
            import pandas as pd
        except ImportError:
            QtWidgets.QMessageBox.critical(
                self, "Error", "La exportación requiere la librería pandas, que no está instalada en QGIS")
            return None
        var_name, units, fechas, serie = seleccion
        df = pd.DataFrame({
            'Fecha': [f.strftime('%Y-%m') for f in fechas],
            f'{var_name} ({units})': np.round(serie.astype(float), 2),
            'Longitud': [round(self.selected_coords[0], 4)] * len(serie),
            'Latitud': [round(self.selected_coords[1], 4)] * len(serie),
            'Pixel_X': [self.selected_px] * len(serie),
            'Pixel_Y': [self.selected_py] * len(serie)
        })
        return var_name, units, df

    def _nombre_archivo(self, var_name, extension):
        return (f"casanare_{var_name.lower().replace(' ', '_')}_"
                f"{self.combo_anio_inicio.currentText()}_{self.combo_anio_fin.currentText()}.{extension}")

    # --- Exportación ---------------------------------------------------------

    def _export_pdf(self):
        """Exporta los datos del punto seleccionado a PDF"""
        exportacion = self._datos_exportacion()
        if exportacion is None:
            return
        from matplotlib.backends.backend_pdf import PdfPages
        var_name, units, df = exportacion
        anio_ini = self.combo_anio_inicio.currentText()
        anio_fin = self.combo_anio_fin.currentText()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            f"Exportar datos de {var_name} a PDF",
            self._nombre_archivo(var_name, 'pdf'),
            "PDF files (*.pdf)"
        )
        if filename:
            try:
                # Paginación: 30 filas por página, hoja A4, márgenes y variables en cada página
                rows_per_page = 30
                num_rows = len(df)
                num_pages = (num_rows + rows_per_page - 1) // rows_per_page
                a4_inches = (8.27, 11.69)  # A4 size in inches (width, height)
                left_margin = 0.5
                right_margin = 0.5
                top_margin = 1.2  # margen superior mayor para el título
                bottom_margin = 0.7
                table_width = a4_inches[0] - left_margin - right_margin
                table_height = a4_inches[1] - top_margin - bottom_margin
                with PdfPages(filename) as pdf:
                    for page in range(num_pages):
                        start = page * rows_per_page
                        end = min(start + rows_per_page, num_rows)
                        df_page = df.iloc[start:end]
                        fig, ax = plt.subplots(figsize=a4_inches)
                        ax.axis('off')
                        # Título con variables
                        title_text = (f"Datos seleccionados - {var_name} ({units})\n"
                                      f"Coordenada: {self.selected_coords[0]:.4f}, {self.selected_coords[1]:.4f}\n"
                                      f"Rango: {anio_ini}-{anio_fin} | Página {page+1} de {num_pages}\n"
                                      f"Fuente: WorldClim 2.1 / CRU-TS 4.09")
                        plt.title(title_text, fontsize=12, loc='left', pad=20)
                        # Tabla
                        table = ax.table(cellText=df_page.values,
                                         colLabels=df_page.columns,
                                         loc='center',
                                         cellLoc='center',
                                         bbox=[left_margin/a4_inches[0], (top_margin+0.1)/a4_inches[1],
                                               table_width/a4_inches[0], (table_height-0.2)/a4_inches[1]])
                        table.auto_set_font_size(False)
                        table.set_fontsize(7)
                        table.scale(1.15, 1.25)
                        # Ajustar ancho de columnas para evitar solapamientos
                        for key, cell in table.get_celld().items():
                            cell.set_width(1.0 / len(df_page.columns))
                        plt.subplots_adjust(left=left_margin/a4_inches[0],
                                           right=1-right_margin/a4_inches[0],
                                           top=1-top_margin/a4_inches[1],
                                           bottom=bottom_margin/a4_inches[1])
                        pdf.savefig(fig)
                        plt.close(fig)
                QtWidgets.QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a:\n{filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo PDF:\n{str(e)}")

    def _export_excel(self):
        """Exporta los datos del punto seleccionado a Excel (.xlsx)"""
        exportacion = self._datos_exportacion()
        if exportacion is None:
            return
        var_name, units, df = exportacion
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            f"Exportar datos de {var_name} a Excel",
            self._nombre_archivo(var_name, 'xlsx'),
            "Excel files (*.xlsx)"
        )
        if filename:
            try:
                try:
                    df.to_excel(filename, index=False)
                except ImportError:
                    # QGIS no siempre incluye openpyxl: se usa el escritor propio
                    dm.escribir_xlsx(filename, list(df.columns), df.itertuples(index=False))
                QtWidgets.QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a:\n{filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo Excel:\n{str(e)}")

    def _export_csv(self):
        """Exporta los datos del punto seleccionado a CSV"""
        exportacion = self._datos_exportacion()
        if exportacion is None:
            return
        var_name, units, df = exportacion
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            f"Exportar datos de {var_name}",
            self._nombre_archivo(var_name, 'csv'),
            "CSV files (*.csv)"
        )
        if filename:
            try:
                df.to_csv(filename, index=False, encoding='utf-8')
                QtWidgets.QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a:\n{filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo:\n{str(e)}")

    def _export_png(self):
        """Exporta la gráfica actual como imagen PNG"""
        seleccion = self._serie_seleccionada()
        if seleccion is None:
            QtWidgets.QMessageBox.warning(
                self, "Error", "Seleccione un punto dentro de Casanare y un rango de años válido")
            return
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Exportar gráfica como PNG",
            'grafica_' + self._nombre_archivo(seleccion[0], 'png'),
            "PNG files (*.png)"
        )
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
                QtWidgets.QMessageBox.information(self, "Éxito", f"Gráfica exportada correctamente a:\n{filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo exportar la imagen:\n{str(e)}")

    def _show_info(self):
        """Muestra la ventana de información del plugin"""
        try:
            info_dialog = InfoDialog(self)
            info_dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de información:\n{str(e)}")

    # --- Mapa y gráfica ------------------------------------------------------

    def _toggle_heatmap(self):
        self.heatmap_mode = not self.heatmap_mode
        self._update_map_pixmap()

    def _update_map_pixmap(self):
        if self.datos is None:
            return
        arr = self.mapa_base
        mask_valid = ~np.isnan(arr)
        h, w = arr.shape
        rgb_array = np.zeros((h, w, 3), dtype=np.uint8)
        arr_valid = arr[mask_valid]
        if arr_valid.size > 0:
            arr_norm = (arr_valid - arr_valid.min()) / (arr_valid.max() - arr_valid.min() + 1e-8)
            cmap = plt.get_cmap('hot' if self.heatmap_mode else 'Blues')
            # Se evita el extremo claro de la escala para que el mapa contraste con el fondo
            rgb_array[mask_valid] = (cmap(0.15 + 0.85 * arr_norm)[:, :3] * 255).astype(np.uint8)
        rgb_array[~mask_valid] = [0, 0, 0]
        rgb_array = np.ascontiguousarray(rgb_array)
        qimg = QImage(rgb_array.data, w, h, w * 3, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(self.label_map.width(), self.label_map.height())

        # Dibuja el punto rojo si hay selección
        if self.selected_px is not None and self.selected_py is not None:
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QColor(0, 0, 0, 255))  # Borde negro
            painter.setBrush(QColor(255, 0, 0, 255))  # Relleno rojo
            # Centro de la celda seleccionada en el pixmap
            x = int((self.selected_px + 0.5) / w * self.label_map.width())
            y = int((self.selected_py + 0.5) / h * self.label_map.height())
            painter.drawEllipse(x-6, y-6, 12, 12)
            painter.end()

        self.label_map.setPixmap(pixmap)

    def _seleccionar_celda(self, py, px):
        if not self.dentro[py, px]:
            QtWidgets.QMessageBox.warning(self, "Error", "El punto está fuera del departamento de Casanare")
            return
        self.selected_px = px
        self.selected_py = py
        self.selected_coords = dm.celda_a_coordenadas(py, px)
        self.label_coords.setText(
            f"Coordenadas: {self.selected_coords[0]:.4f}, {self.selected_coords[1]:.4f}")
        self._update_map_pixmap()  # Actualiza el mapa con el punto rojo
        self._update_plot()

    def _on_map_click(self, event):
        if self.datos is None:
            return
        pos = event.position() if hasattr(event, 'position') else event.pos()  # Qt6 / Qt5
        px = min(int(pos.x() / self.label_map.width() * dm.COLUMNAS), dm.COLUMNAS - 1)
        py = min(int(pos.y() / self.label_map.height() * dm.FILAS), dm.FILAS - 1)
        self._seleccionar_celda(py, px)

    def _buscar_por_coordenadas(self):
        try:
            x_coord = float(self.lineEdit_X.text().replace(',', '.'))
            y_coord = float(self.lineEdit_Y.text().replace(',', '.'))
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingrese coordenadas válidas (números decimales)")
            return
        celda = dm.coordenadas_a_celda(x_coord, y_coord)
        if celda is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Las coordenadas están fuera del área de Casanare")
            return
        self._seleccionar_celda(*celda)

    def _update_plot(self):
        self.ax.clear()
        if self.datos is None or self.selected_px is None:
            texto = 'Seleccione un punto en el mapa' if self.datos is not None else 'Descargue los datos para ver la gráfica'
            self.ax.text(0.5, 0.5, texto, ha='center', va='center')
            self.canvas.draw()
            return
        seleccion = self._serie_seleccionada()
        if seleccion is None:
            self.ax.text(0.5, 0.5, 'El año inicial debe ser menor o igual al año final',
                         ha='center', va='center')
            self.canvas.draw()
            return
        var_name, units, fechas, serie = seleccion
        fechas_str = [f.strftime('%Y-%m') for f in fechas]
        # Ajustar el ancho del canvas para permitir scroll si hay muchas fechas
        self.canvas.setMinimumWidth(max(400, 20 * len(fechas_str)))
        self.ax.plot(fechas_str, serie, marker='o', linestyle='-', linewidth=1,
                     color='red' if 'Temperatura' in var_name else 'blue')
        self.ax.set_title(f'{var_name} en ({self.selected_coords[0]:.4f}, {self.selected_coords[1]:.4f})')
        self.ax.set_xlabel('Fecha')
        self.ax.set_ylabel(f'{var_name} ({units})')
        self.ax.tick_params(axis='x', labelrotation=45)
        self.ax.grid(True, alpha=0.3)
        if 'Temperatura' in var_name:
            self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}'))
        self.fig.tight_layout()
        self.canvas.draw()
