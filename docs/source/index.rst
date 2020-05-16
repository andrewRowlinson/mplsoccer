mplsoccer
=========

`mplsoccer` is a Python library for drawing soccer/football pitches in Matplotlib and loading StatsBomb open-data.

-----------
Quick start
-----------

Use the package manager `pip <https://pip.pypa.io/en/stable/>`_ to install mplsoccer.

.. code-block:: bash

    pip install mplsoccer

Plot a StatsBomb pitch:

.. code-block:: python

    from mplsoccer.pitch import Pitch
    pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw()
	
.. image:: gallery/pitch_setup/images/sphx_glr_plot_quick_start_001.png

---------------------
Why mplsoccer exists?
---------------------

mplsoccer shares some of the tools I built for the OptaPro Analytics Forum.
At the time there weren't any open-sourced python tools.
Now alternatives exist, such as `matplotsoccer <https://pypi.org/project/matplotsoccer/>`_

By using mplsoccer, I hope that you can spend more time building insightful graphics rather than having to learn to draw pitches from scratch.

-----------------------
Advantages of mplsoccer
-----------------------

mplsoccer:

1) draws 7 different pitch types by changing a single argument, which is useful as there isn't a standardised data format
2) extends matplotlib to plot heatmaps, (comet) lines, footballs and rotated markers
3) flips the data coordinates in vertical format so you don't need to remember to flip them
4) creates tidy dataframes for StatsBomb data, which is useful as most of the alternatives produce nested dataframes
 
-------
License
-------
`MIT <https://choosealicense.com/licenses/mit/>`_

-------------
Contributions
-------------

Contributions are welcome. It would be great to add the following functionality to mplsoccer:

- pass maps
- pass sonars
- Voronoi diagrams

I would also welcome more examples in the gallery to help others.

Please get in touch at rowlinsonandy@gmail.com or `@numberstorm <https://twitter.com/numberstorm>`_ on Twitter.

-----------
Inspiration
-----------

mplsoccer was inspired by other people's work:

- `Peter McKeever <http://petermckeever.com/2019/01/plotting-pitches-in-python/>`_ inspired the API design
- `ggsoccer <https://github.com/Torvaney/ggsoccer>`_ is a library for plotting pitches in R
- `lastrow <https://twitter.com/lastrowview>`_ often tweets animations and the accompanying code
- `fcrstats <http://fcrstats.com/>`_ has some great tutorials for using football data
- `fcpython <https://fcpython.com/>`_ also has some great tutorials in Python
- `Karun Singh <https://twitter.com/karun1710>`_ tweets some interesting football analytics and visuals
- `StatsBomb <https://statsbomb.com/>`_ has great visual designs and free open-data
- John Burn-Murdoch's `tweet <https://twitter.com/jburnmurdoch/status/1057907312030085120>`_ got me interested in football analytics



.. _Python: http://www.python.org/

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   installation
   gallery/pitch_setup/plot_pitches
   gallery/statsbomb/plot_statsbomb_data
   gallery/index
   api
     
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
