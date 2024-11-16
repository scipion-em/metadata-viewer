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
import importlib
import sys
import argparse

import logging

from metadataviewer.dao.numpy_dao import NumpyDao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROPERTIES_TABLE_LABELS = ' key value'


def defineArgs():
    parser = argparse.ArgumentParser(prog="Metadata viewer", description="Launcher of Metadata viewer form the command line.")
    parser.add_argument("fileName", help="File to be displayed by the dataviewer ")
    parser.add_argument("--tableview", help="Displays the file in table mode", action="store_true", default=False)
    parser.add_argument("--galleryview", help="Displays the file in gallery mode", action="store_true", default=False)
    parser.add_argument("--darktheme", help="Load the viewer with a dark theme", action="store_true", default=False)
    parser.add_argument("--extensionpath", help="Path to a module to load to extend the viewer", type=str, default=None)
    parser.add_argument("--visiblelabels", help="List of column names that will be visible", type=str, default=None)
    parser.add_argument("--orderlabels", help="List of column names that will be used to stablished a columns order", type=str, default=None)

    return parser


def main():
    parser = defineArgs()
    argsList = sys.argv[1:]
    args = parser.parse_args(argsList)

    logger.info('Calling metadata viewer from command line')
    from metadataviewer.model import ObjectManager

    if args.extensionpath is not None:
        extensiopath = args.extensionpath
        logger.info("Extending from %s" % extensiopath)
        spec = importlib.util.spec_from_file_location("mdvextension", extensiopath)
        extension_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extension_module)
        extension_module.extendMDViewer(ObjectManager)

    objectManager = ObjectManager()
    objectManager.registerDAO(NumpyDao)

    if args.visiblelabels:
        logger.info("Visible labels: %s" % args.visiblelabels)
        args.visiblelabels += PROPERTIES_TABLE_LABELS
        objectManager.setVisibleLabels(args.visiblelabels.split(' '))

    if args.orderlabels:
        logger.info("Order labels: %s" % args.orderlabels)
        objectManager.setColumnsOrder('objects', args.orderlabels.split(' '))

    objectManager.open(args)


if __name__ == "__main__":
    main()
