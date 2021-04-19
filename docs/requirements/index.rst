============
Requirements
============

ArcGIS
======

Many stages of the analyses for the study were conducted using ArcGIS Pro 2.5. As a result, all processing and analyses described in this manual use ArcGIS Pro 2.5 or arcpy (version)  (or later). While it is possible to perform the basic preprocessing in open source GIS software like Quantum GIS or using python spatial libraries (e.g., shapely, fiona, gdal), the Script Tools for updating the zone attributes (Script Tool A) and creating project opportunity areas (Script Tool B), have been designed specifically for use in ArcGIS Pro 2.5 (or later).

Python
======

Python is an open-source programming language.

Sphinx
======

Sphinx is needed to build the documentation locally.

To install Sphinx:

.. code:: bash

    pip install sphinx

To build the documentation into HTML format, navigate to the ``docs`` folder in terminal and run the following command:

.. code:: bash

    make html
