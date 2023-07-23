.. image:: logo.png
   :width: 157
   :align: center

**mplsoccer is a Python library for plotting soccer/football charts in Matplotlib and
loading StatsBomb open-data.**

-----------
Quick start
-----------

Use the package manager `pip <https://pip.pypa.io/en/stable/>`_ to install mplsoccer.

.. code-block:: bash

    pip install mplsoccer

Or install via `Anaconda <https://docs.anaconda.com/free/anaconda/install/index.html>`_

.. code-block:: bash

    conda install -c conda-forge mplsoccer

Plot a StatsBomb pitch:

.. code-block:: python

    from mplsoccer.pitch import Pitch
    pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw()
	
.. image:: gallery/pitch_setup/images/sphx_glr_plot_quick_start_001.png

------------------
What is mplsoccer?
------------------

In mplsoccer, you can:

- plot football/soccer pitches on nine different pitch types
- plot radar charts
- plot Nightingale/pizza charts
- plot bumpy charts for showing changes over time
- plot arrows, heatmaps, hexbins, scatter, and (comet) lines
- load StatsBomb data as a tidy dataframe
- standardize pitch coordinates into a single format

I hope mplsoccer helps you make insightful graphics faster,
so you don't have to build charts from scratch.

-------------
Want to help?
-------------

I would love the community to get involved in mplsoccer.
Take a look at our `open-issues <https://github.com/andrewRowlinson/mplsoccer/issues>`_
for inspiration. Please get in touch at rowlinsonandy@gmail.com or on
`Twitter <https://twitter.com/numberstorm>`_ to find out more.

--------------
Recent changes
--------------

View the `changelog <https://github.com/andrewRowlinson/mplsoccer/blob/master/CHANGELOG.md>`_
for a full list of the recent changes to mplsoccer.

-------
License
-------
`MIT <https://choosealicense.com/licenses/mit/>`_

-----------
Inspiration
-----------

mplsoccer was inspired by:

- `Peter McKeever <https://petermckeever.com/>`_ heavily inspired the API design
- `ggsoccer <https://github.com/Torvaney/ggsoccer>`_ influenced the design and Standardizer
- `lastrow's <https://twitter.com/lastrowview>`_ legendary animations
- `fcrstats' <https://twitter.com/FC_rstats>`_ tutorials for using football data
- `fcpython's <https://fcpython.com/>`_ Python tutorials for using football data
- `Karun Singh's <https://twitter.com/karun1710>`_ expected threat (xT) visualizations
- `StatsBomb's <https://statsbomb.com/>`_ great visual design and free open-data
- John Burn-Murdoch's `tweet <https://twitter.com/jburnmurdoch/status/1057907312030085120>`_
  got me interested in football analytics


.. _Python: http://www.python.org/

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
   installation
   gallery/pitch_setup/plot_pitches
   gallery/radar/plot_radar
   gallery/bumpy_charts/plot_bumpy
   gallery/statsbomb/plot_statsbomb_data
   gallery/index
   api
     
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
