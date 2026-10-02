# coding=utf-8
"""Pruebas de las funciones de datos (no requieren QGIS ni conexión).

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ingsistemas@unitropico.edu.co'
__date__ = '2026-10-02'
__copyright__ = 'Copyright 2025, Universidad Internacional del Trópico Americano - Unitrópico'

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import data_manager as dm  # noqa: E402


class DataManagerTest(unittest.TestCase):
    """Pruebas de fechas, grilla, máscara y ETP."""

    def test_fechas_mensuales(self):
        fechas = dm.fechas()
        self.assertEqual(len(fechas), 504)
        etiquetas = [f.strftime('%Y-%m') for f in fechas]
        self.assertEqual(len(set(etiquetas)), 504)
        self.assertEqual(etiquetas[:3], ['1981-01', '1981-02', '1981-03'])
        self.assertEqual(etiquetas[-1], '2022-12')

    def test_decadas(self):
        self.assertEqual(dm.decada(1981), '1980-1989')
        self.assertEqual(dm.decada(2022), '2020-2024')

    def test_coordenadas(self):
        celda = dm.coordenadas_a_celda(-72.5, 5.8)
        self.assertEqual(celda, (13, 15))
        lon, lat = dm.celda_a_coordenadas(*celda)
        self.assertAlmostEqual(lon, -72.4791667, places=5)
        self.assertAlmostEqual(lat, 5.8125, places=5)
        self.assertIsNone(dm.coordenadas_a_celda(-75.0, 5.0))

    def test_mascara(self):
        mascara = dm.mascara()
        self.assertEqual(mascara.shape, (dm.FILAS, dm.COLUMNAS))
        self.assertEqual(int(mascara.sum()), 2346)

    def test_etp_hargreaves(self):
        forma = (len(dm.meses()), dm.FILAS, dm.COLUMNAS)
        tmin = np.full(forma, 22.0, dtype=np.float32)
        tmax = np.full(forma, 32.0, dtype=np.float32)
        etp = dm.etp_hargreaves(tmin, tmax)
        # En Casanare la ETP mensual con estas temperaturas está entre 100 y 200 mm
        self.assertTrue(np.all((etp > 100) & (etp < 200)))


if __name__ == "__main__":
    unittest.main()
