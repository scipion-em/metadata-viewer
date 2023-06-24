# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
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

import sys
import argparse
from PyQt5.QtWidgets import QApplication

from metadataviewer.gui.qtviewer import QTMetadataViewer

QT_VIEWER = 'qtviewer'


def defineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("fileName", help="File to be displayed by the dataviewer ")
    parser.add_argument("--viewer", help="Select a viewer implementation (qtviewer, tkviewer, terminal)", default=QT_VIEWER)
    parser.add_argument("--tableview", help="Displays the file in table mode", action="store_true", default=False)
    parser.add_argument("--galleryview", help="Displays the file in gallery mode", action="store_true", default=False)
    return parser


def main():
    parser = defineArgs()
    argsList = sys.argv[1:]
    args = parser.parse_args(argsList)
    app = QApplication(sys.argv)
    if args.viewer == QT_VIEWER:
        window = QTMetadataViewer(args)
        window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()