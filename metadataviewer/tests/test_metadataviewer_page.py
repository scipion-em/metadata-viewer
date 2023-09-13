# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *          Pablo Conesa Mingo         (pconesa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import unittest

from metadataviewer.model import Column, Table, Page


class TestPage(unittest.TestCase):

    def testCreateColumn(self):
        columnPixelSize = Column('_rlnPixelSize', float)
        columnImageName = Column('_rlnImageName', str)

        self.assertEqual(columnPixelSize.getName(), '_rlnPixelSize')
        self.assertEqual(columnPixelSize.getRenderer(), float)
        self.assertEqual(columnPixelSize.__eq__(columnImageName), False)

    def testTable(self):
        table = Table('particles')
        page = Page(table)
        columnImageName = Column('_rlnImageName', str)
        columnPixelSize = Column('_rlnPixelSize', float)
        table.addColumn(columnImageName)
        table.addColumn(columnPixelSize)
        self.assertEqual(table.getSize(), 2)
        row1 = ['000001@J117/imported/015998556314607367796_BPV_1386.mrcs', 172.991730]
        row2 = ['000001@J117/imported/015998556314607367796_BPV_1387.mrcs', 172.991730]
        page.addRow(row1)
        page.addRow(row2)
        self.assertEqual(page.getSize(), 2)



