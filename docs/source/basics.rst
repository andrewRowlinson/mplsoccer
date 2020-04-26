Basics
============

Plot a pitch
------------
.. code-block:: python

    from mplsoccer.pitch import Pitch
    pitch = Pitch()
    fig, ax = pitch.draw()

Plot on a matplotlib axis
-------------------------

It also works with other matplotlib figures so you can play around with different charts. Just pass an argument for `ax` to `Pitch.draw`.

.. code-block:: python

    from mplsoccer.pitch import Pitch
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(ncols=2, figsize=(16, 5))
    pitch = Pitch()
    pitch.draw(ax=ax[1])
    pitch.scatter(50, 40, s=200, ax=ax[1])
     