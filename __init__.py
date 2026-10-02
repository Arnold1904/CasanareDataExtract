"""
/***************************************************************************
 CasanareDataExtract
                     A QGIS plugin
 Plugin para extraer y visualizar datos climáticos de Casanare
 Estructura base generada con Plugin Builder (GPL): http://g-sherman.github.io/Qgis-Plugin-Builder/
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
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CasanareDataExtract class from file CasanareDataExtract.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .MyPlugin import CasanareDataExtract
    return CasanareDataExtract(iface)
