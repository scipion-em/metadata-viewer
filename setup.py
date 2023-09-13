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

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

from metadataviewer import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Load requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='metadata-viewer',  # Required
    version=__version__,  # Required
    description='Generic metadata viewer',  # Required
    long_description=long_description,  # Optional
    url='https://github.com/fonsecareyna82/metadata_viewer',  # Optional
    author='Yunior C. Fonseca-Reyna, Pablo Conesa, Jorge Jiménez',  # Optional
    author_email='cfonseca@cnb.csic.es, pconesa@cnb.csic.es, jjimenez@cnb.csic.es',  # Optional
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='metadata-viewer',  # Optional
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'metadataviewer': ['gui/resources/*'],
    },
    install_requires=[requirements],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/fonsecareyna82/metadata_viewer/issues',
        'Source': 'https://github.com/fonsecareyna82/metadata_viewer',
    },
)