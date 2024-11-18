metadata-viewer (BETA)
=======================

Metadata-viewer is a Python  package designed to help you easily visualize
metadata from various file formats mainly for visualizing metadata associated
with cryo-electron microscopy (cryo-EM) data. Its primary functionality includes
displaying data in both table and image gallery modes. This package is capable
of handling large datasets with millions of rows and performing operations such
as selecting and sorting quickly. While its core purpose is to serve as a viewer within the
Scipion framework, it can also be used independently outside of Scipion.
The package facilitates the exploration of cryo-EM-related information and other
types of metadata through efficient data manipulation and visualization, making
it a valuable tool for researchers in the field.
It is available as a small self-contained  `Python module <https://pypi.org/project/metadata-viewer/>`_.

Installation
-------------

You can install MetadataViewer using pip:

.. code-block::

 pip install metadata-viewer


Usage
------
**TODO**

Supported metadata file formats
--------------------------------

MetadataViewer supports a wide range of file formats(through Scipion), including but not limited to:

* star files
* xmd files
* sqlite files


Contributing
---------------
MetadataViewer is an open-source project, and contributions from the community
are welcome. If you'd like to contribute or report issues, please visit our
GitHub repository. `GitHub repository <https://github.com/scipion-em/metadata-viewer/>`_.


Authors
-------

 * Yunior C. Fonseca Reyna, Biocomputing Unit, National Center of Biotechnology, Madrid, Spain
 * Pablo Conesa Mingo, Biocomputing Unit, National Center of Biotechnology, Madrid, Spain
 * Jorge Jiménez, Biocomputing Unit, National Center of Biotechnology, Madrid, Spain

Testing
-------

``python3 -m unittest discover metadataviewer/tests``

