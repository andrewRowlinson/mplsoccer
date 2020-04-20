.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_gallery_plot_kde.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_gallery_plot_kde.py:


================================
Event distribution using kdeplot 
================================

This example shows how to plot the location of events occurring in a match 
using kernel density estimation (KDE).


.. code-block:: default


    from mplsoccer.pitch import Pitch
    from mplsoccer.statsbomb import read_event, EVENT_SLUG
    import os








load first game that Messi played as a false-9 and the match before as dataframes


.. code-block:: default


    kwargs = {'related_event_df': False,'shot_freeze_frame_df': False, 'tactics_lineup_df': False}
    df_false9 = read_event(os.path.join(EVENT_SLUG,'69249.json'), **kwargs)['event']
    df_before_false9 = read_event(os.path.join(EVENT_SLUG,'69251.json'), **kwargs)['event']








Filter the dataframes to only include Messi's events and the starting positions


.. code-block:: default


    df_false9 = df_false9.loc[df_false9.player_id == 5503,['x', 'y']]
    df_before_false9 = df_before_false9.loc[df_before_false9.player_id == 5503,['x', 'y']]








View a dataframe


.. code-block:: default


    df_false9.head()






.. only:: builder_html

    .. raw:: html

        <div>
        <style scoped>
            .dataframe tbody tr th:only-of-type {
                vertical-align: middle;
            }

            .dataframe tbody tr th {
                vertical-align: top;
            }

            .dataframe thead th {
                text-align: right;
            }
        </style>
        <table border="1" class="dataframe">
          <thead>
            <tr style="text-align: right;">
              <th></th>
              <th>x</th>
              <th>y</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>5</th>
              <td>61.1</td>
              <td>39.8</td>
            </tr>
            <tr>
              <th>6</th>
              <td>60.9</td>
              <td>39.6</td>
            </tr>
            <tr>
              <th>20</th>
              <td>88.7</td>
              <td>46.1</td>
            </tr>
            <tr>
              <th>21</th>
              <td>88.7</td>
              <td>46.1</td>
            </tr>
            <tr>
              <th>22</th>
              <td>91.2</td>
              <td>39.6</td>
            </tr>
          </tbody>
        </table>
        </div>
        <br />
        <br />

Plotting Messi's first game as a False-9


.. code-block:: default


    pitch = Pitch(pitch_type = 'statsbomb', figsize = (16, 11), 
                  pitch_color = 'grass', stripe = True, constrained_layout=False)
    fig, ax = pitch.draw()

    # plotting
    ax.set_title('The first Game Messi played in the false 9 role', fontsize = 30, pad = 20)

    # plot the kernel density estimation
    pitch.kdeplot(df_false9.x, df_false9.y, ax = ax, cmap = 'plasma', linewidths = 3)

    # annotate
    pitch.annotate('6-2 thrashing \nof Real Madrid', (25,10), color = 'white',
                   fontsize = 25, ha = 'center', va = 'center', ax = ax)
    pitch.annotate('more events', (70,30), (20,30), ax=ax, color='white', ha = 'center', va = 'center',
                   fontsize = 20, arrowprops=dict(facecolor='white', edgecolor = 'None'))
    pitch.annotate('fewer events', (51,20), (20,20), ax=ax, color='white', ha = 'center', va = 'center',
                   fontsize = 20, arrowprops=dict(facecolor='white', edgecolor = 'None'))

    fig.tight_layout()




.. image:: /gallery/images/sphx_glr_plot_kde_001.png
    :class: sphx-glr-single-img





Plotting both Messi's first game as a False-9 and the game directly before


.. code-block:: default


    # Setup the pitches
    pitch = Pitch(pitch_type = 'statsbomb', figsize = (16, 7), layout = (1, 2), 
                  pitch_color = 'grass', stripe = True, constrained_layout=False)
    fig, ax = pitch.draw()

    # set the titles
    ax[0].set_title('Messi in the game directly before \n playing in the false 9 role', fontsize = 25, pad = 20)
    ax[1].set_title('The first Game Messi \nplayed in the false 9 role', fontsize = 25, pad = 20)

    # plot the kernel density estimation
    pitch.kdeplot(df_before_false9.x, df_before_false9.y, ax = ax[0], cmap = 'plasma', linewidths = 3)
    pitch.kdeplot(df_false9.x, df_false9.y, ax = ax[1], cmap = 'plasma', linewidths = 3)

    # annotations
    pitch.annotate('6-2 thrashing \nof Real Madrid', (25,10), color = 'white',
                   fontsize = 25, ha = 'center', va = 'center', ax = ax[1])
    pitch.annotate('2-2 draw \nagainst Valencia', (25,10), color = 'white',
                   fontsize = 25, ha = 'center', va = 'center', ax = ax[0])
    pitch.annotate('more events', (90,68), (30,68), ax=ax[0], color='white', ha = 'center', va = 'center',
                   fontsize = 20, arrowprops=dict(facecolor='white', edgecolor = 'None'))
    pitch.annotate('fewer events', (80,17), (80,5), ax=ax[0], color='white', ha = 'center', va = 'center',
                   fontsize = 20, arrowprops=dict(facecolor='white', edgecolor = 'None'))

    fig.tight_layout()




.. image:: /gallery/images/sphx_glr_plot_kde_002.png
    :class: sphx-glr-single-img






.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  8.977 seconds)


.. _sphx_glr_download_gallery_plot_kde.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: plot_kde.py <plot_kde.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: plot_kde.ipynb <plot_kde.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
