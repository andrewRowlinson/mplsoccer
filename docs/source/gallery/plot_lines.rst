.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_gallery_plot_lines.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_gallery_plot_lines.py:


=====================
Pass plot using lines
=====================

This example shows how to plot all passes from a team in a match as lines.


.. code-block:: default


    from mplsoccer.pitch import Pitch
    from mplsoccer.statsbomb import read_event, EVENT_SLUG
    from matplotlib import rcParams
    from matplotlib.lines import Line2D
    import os

    rcParams['text.color'] = '#c7d5cc'  # set the default text color

    # get event dataframe for game 7478, create a dataframe of the passes, and a boolean mask for the outcome
    df = read_event(os.path.join(EVENT_SLUG, '7478.json'),
                    related_event_df=False, shot_freeze_frame_df=False, tactics_lineup_df=False)['event']








Boolean mask for filtering the dataset by team


.. code-block:: default


    team1, team2 = df.team_name.unique()
    mask_team1 = (df.type_name == 'Pass') & (df.team_name == team1)








Filter dataset to only include one teams passes and get boolean mask for the completed passes


.. code-block:: default


    df_pass = df.loc[mask_team1, ['x', 'y', 'pass_end_x', 'pass_end_y', 'outcome_name']]
    mask_complete = df_pass.outcome_name.isnull()








View the pass dataframe.


.. code-block:: default


    df_pass.head()






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
              <th>pass_end_x</th>
              <th>pass_end_y</th>
              <th>outcome_name</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>20</th>
              <td>11.0</td>
              <td>80.0</td>
              <td>29.0</td>
              <td>68.0</td>
              <td>NaN</td>
            </tr>
            <tr>
              <th>22</th>
              <td>29.0</td>
              <td>67.0</td>
              <td>58.0</td>
              <td>80.0</td>
              <td>Out</td>
            </tr>
            <tr>
              <th>28</th>
              <td>56.0</td>
              <td>68.0</td>
              <td>75.0</td>
              <td>77.0</td>
              <td>NaN</td>
            </tr>
            <tr>
              <th>37</th>
              <td>95.0</td>
              <td>80.0</td>
              <td>110.0</td>
              <td>56.0</td>
              <td>NaN</td>
            </tr>
            <tr>
              <th>40</th>
              <td>109.0</td>
              <td>56.0</td>
              <td>106.0</td>
              <td>54.0</td>
              <td>Incomplete</td>
            </tr>
          </tbody>
        </table>
        </div>
        <br />
        <br />

Plotting


.. code-block:: default


    # Setup the pitch
    pitch = Pitch(pitch_type='statsbomb', orientation='horizontal',
                  pitch_color='#22312b', line_color='#c7d5cc', figsize=(16, 11),
                  constrained_layout=False, tight_layout=True)
    fig, ax = pitch.draw()

    # Plot the completed passes
    pitch.lines(df_pass[mask_complete].x, df_pass[mask_complete].y,
                df_pass[mask_complete].pass_end_x, df_pass[mask_complete].pass_end_y,
                lw=4, transparent=True, comet=True,
                color='#ad993c', ax=ax)

    # Plot the other passes
    pitch.lines(df_pass[~mask_complete].x, df_pass[~mask_complete].y,
                df_pass[~mask_complete].pass_end_x, df_pass[~mask_complete].pass_end_y,
                lw=4, transparent=True, comet=True,
                color='#ba4f45', ax=ax)

    # setup the legend
    custom_lines = [Line2D([0], [0], color='#ad993c', lw=4),
                    Line2D([0], [0], color='#ba4f45', lw=4)]
    ax.legend(custom_lines, ['completed passes', 'other passes'], 
              facecolor='#22312b', edgecolor='None', fontsize=20, loc='upper left')

    # Set the title
    ax.set_title(f'{team1} passes vs {team2}', fontsize=30)

    # Set the figure facecolor
    fig.set_facecolor('#22312b')




.. image:: /gallery/images/sphx_glr_plot_lines_001.png
    :class: sphx-glr-single-img






.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  7.269 seconds)


.. _sphx_glr_download_gallery_plot_lines.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: plot_lines.py <plot_lines.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: plot_lines.ipynb <plot_lines.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
