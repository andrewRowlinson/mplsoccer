mplsoccer
=========

`mplsoccer` is a Python plotting library for drawing soccer / football pitches in Matplotlib and loading StatsBomb open-data.

.. image:: https://github.com/andrewRowlinson/mplsoccer/raw/master/docs/figures/README_animation_example.gif?raw=true

*An example using* `Metrica Sports <https://github.com/metrica-sports/sample-data>`_ *tracking data.*

See :ref:`modindex` for API.

-----------
Quick start
-----------

Use the package manager `pip <https://pip.pypa.io/en/stable/>`_ to install mplsoccer.

.. code-block:: bash

    pip install mplsoccer

Plot a pitch

.. code-block:: python

    from mplsoccer.pitch import Pitch
    pitch = Pitch()
    fig, ax = pitch.draw()
    

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   installation
   basics
   api
     
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
