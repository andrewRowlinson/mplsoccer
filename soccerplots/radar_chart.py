'''
author: Anmol Durgapal || @slothfulwave612

A Python module for plotting radar-chart.

The radar-chart theme is inspired from @Statsbomb.
'''

## import necessary packages/modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from . import utils

def plot_radar(ranges, params, values, radar_color, label_fontsize=10, range_fontsize=6.5, filename=None, 
               dpi=300, title=dict(), alpha=[0.6, 0.6], compare=False, fontname='Liberation Serif', credit_size=13):
    '''
    Function to plot radar-chart.

    Arguments:
        ranges -- list of tuples containing min and max value for each parameter.
        params -- list of string values containing the name of parameters.
        values -- list of float values for each parameters.
                  can be nested list as well when making comparison charts.
        radar_color -- list of two color values.
        label_fontsize -- float, the fontsize of label. Default: 10
        range_fontsize -- float, the fontsize for range values. Default: 6.5
        filename -- str, the name per which the file will be saved added extension. Default: None
        dpi -- int, dots per inch value, Default: 300.
        title -- dict, containing information of title and subtitle, Default: dict()
        alpha -- float[0, 1], alpha value for color, Default: [0.6, 0.6].
        compare -- bool, True: if a comparison radar chart will be made.
                         False: otherwise.
                    Default: False
        fontname -- str, font-name to be used for the entire radar chart, Default: 'Liberation Serif'.
        credit_size -- float, the font-size for the credit string, Default: 13.

    
    Returns:
        fig, ax -- figure and axis object.
    '''
    ## assert required conditions 
    assert len(ranges) >= 3, "Length of ranges should be greater than equal to 3"
    assert len(params) >= 3, "Length of params should be greater than equal to 3"

    if compare == True:
        ## for making comparison radar charts
        assert len(values) == len(radar_color) == len(alpha), "Length for values, radar_color and alpha do not match"
    else:
        assert len(values) >= 3, "Length of values should be greater than equal to 3"
        assert len(ranges) == len(params) == len(values), "Length for ranges, params and values not matched"

    ## make subplot
    fig, ax = plt.subplots(figsize=(20, 10))

    ## set axis
    ax.set_aspect('equal')
    ax.set(xlim=(-23, 23), ylim=(-23, 25))

    if type(radar_color) == str:
        ## make radar_color a list
        radar_color = [radar_color]
        radar_color.append('#D6D6D6')

    ## add labels around the last circles
    ax = add_labels(params=params, ax=ax, fontsize=label_fontsize, fontname=fontname)

    ## add ranges
    ax, xy, range_values = add_ranges(ranges=ranges, ax=ax, range_fontsize=range_fontsize, fontname=fontname)

    if compare == True:
        ## for making comparison radar charts

        for i in range(len(values)):
            ## fetch value
            value = values[i]

            ## get vertices
            vertices = get_vertices(value, xy, range_values)

            ## make the radar chart
            ax = plot_circles(ax=ax, radar_color=radar_color[i], vertices=vertices, alpha=alpha[i], compare=True)

    else:
        ## get vertices
        vertices = get_vertices(values, xy, range_values)

        ## make the radar chart
        ax = plot_circles(ax=ax, radar_color=radar_color, vertices=vertices)
    
    ## add credits
    ax.text(22, -22, 'Radar Chart Theme Inspired From @Statsbomb', name=fontname, ha='right',
            fontdict={'color': '#95919B'}, fontsize=credit_size)

    ## tidy axis
    ax.axis('off')
    
    if len(title) > 0:
        ax = plot_titles(ax, title, fontname)

    if filename:
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')

    return fig, ax

def plot_titles(ax, title, fontname):
    '''
    Function for plotting title values to the radar-chart.

    Arguments:
        ax -- axis object.
        title -- dict, containing information of title and subtitle.
        fontname -- str, font to be used.

    Returns:
        ax -- axis object.
    '''
    if title.get('title_color') == None:
        ## add title color
        title['title_color'] = '#000000'

    if title.get('subtitle_color') == None:
        ## add a subtitle color
        title['subtitle_color'] = '#000000'

    if title.get('title_fontsize') == None:
        ## add titile fontsize
        title['title_fontsize'] = 20
    
    if title.get('sub_title_fontsize') == None:
        ## add subtitle fontsize
        title['subtitle_fontsize'] = 15

    if title.get('title_name'):
        ## plot the title name
        ax.text(-22, 24, title['title_name'], fontsize=title['title_fontsize'], fontweight='bold', fontdict={'color': title['title_color']}, name=fontname)
    
    if title.get('subtitle_name'):
        ## plot the title name
        ax.text(-22, 22, title['subtitle_name'], fontsize=title['subtitle_fontsize'], fontdict={'color': title['subtitle_color']}, name=fontname)

    if title.get('title_color_2') == None:
        ## add title color
        title['title_color_2'] = '#000000'
    
    if title.get('subtitle_color_2') == None:
        ## add subtitle color
        title['subtitle_color_2'] = '#000000'
    
    if title.get('title_name_2'):
        ## plot the second title name
        ax.text(22, 24, title['title_name_2'], fontsize=title['title_fontsize'], fontweight='bold', 
                fontdict={'color': title['title_color_2']}, ha='right', name=fontname)
    
    if title.get('subtitle_name_2'):
        ## plot the second subtitle name
        ax.text(22, 22, title['subtitle_name_2'], fontsize=title['subtitle_fontsize'], 
                fontdict={'color': title['subtitle_color_2']}, ha='right', name=fontname) 
    
    return ax

def plot_circles(ax, radar_color, vertices, alpha=None, compare=False):
    '''
    Function to plot concentric circles.

    Arguments:
        ax -- axis object.
        radar_color -- list of colors.
        vertices -- list of coordinate values for each vertex of the polygon.
        alpha -- float[0-1], the alpha value for colors.
        compare -- bool, True: if a comparison radar chart will be made.
                         False: otherwise.

    Returns:
        ax -- axis object.
    '''
    ## radius value for each circle
    radius = [3.35, 6.7, 10.05, 13.4, 16.75]

    ## edge-color, linewidth, zorder for circle
    ec_circle, lw_circle, zorder_circle = '#D6D6D6', 20, 2

    if compare:    ## for making comparison radar charts
        ## plot a polygon
        radar_1 = Polygon(vertices, fc=radar_color, zorder=zorder_circle+1, alpha=alpha)
        ax.add_patch(radar_1)
    else:
        ## plot a polygon
        radar_1 =  Polygon(vertices, fc=radar_color[0], zorder=zorder_circle-1)
        ax.add_patch(radar_1)

    ## create concentric circles 
    for rad in radius:
        ## create circle
        circle_1 = plt.Circle(xy=(0, 0), radius=rad, fc='none', ec=ec_circle, lw=lw_circle, zorder=zorder_circle)
        ax.add_patch(circle_1)

        if compare == False:
            ## create another circle to fill in second color
            circle_2 = plt.Circle(xy=(0, 0), radius=rad, fc='none', ec=radar_color[1], lw=lw_circle, zorder=zorder_circle+1)
            circle_2.set_clip_path(radar_1)
            ax.add_patch(circle_2)
    
    return ax

def add_labels(params, ax, fontsize, fontname, return_list=False, radius=19):
    '''
    Function to add labels around the last circle.

    Arguments:
        params -- list of values containing the name of parameters.
        ax -- axis object.
        fontsize -- float, the fontsize of label.
        fontname -- str, font to be used.
        return_list -- list, of x and y values. Default: False
        radius -- radius of the circle around which labels are to be align. Default: 19
    
    Returns:
        ax -- axis object.
        x_y -- list of coordinate values, if return_list == True.
    '''

    ## get coordinates and rotation values
    coord = utils.get_coordinates(n=len(params))

    if return_list == True:
        x_y = []

    for i in range(len(params)):
        ## fetch rotation value
        rot = coord[i, 2]

        ## the x and y coordinate for labels
        x, y = (radius*np.sin(rot), radius*np.cos(rot))

        if return_list == True:
            ## add x_y cordinates 
            tup_temp = (x, y)
            x_y.append(tup_temp)

        if y < 0:
            rot += np.pi

        if type(params[i]) == np.float64:
            p = round(params[i], 2)
        else:
            p = params[i]
    
        ax.text(x, y, p, rotation=-np.rad2deg(rot), ha='center', va='center', fontsize=fontsize, name=fontname)
    
    if return_list == True:
        return ax, x_y
    else:
        return ax

def add_ranges(ranges, ax, range_fontsize, fontname):
    '''
    Function to add range value around each circle.

    Arguments:
        ranges -- list of tuples containing min and max value for each parameter.
        ax -- axis object.
        rang_fontsize -- float, fontsize of range values.
        fontname -- str, font to be used.

    Returns:
        ax -- axis object.
        x_y -- numpy array containing x and y coordinate for each numerical range values.
        range_values -- numpy array containing range value for each parameter.
    '''
    ## radius value for every circle
    radius = [2.5, 4.1, 5.8, 7.5, 9.2, 10.9, 12.6, 14.3, 15.9, 17.6]

    ## x and y coordinate values for range numbers
    x_y = []

    ## range values for every ranges
    range_values = np.array([])

    for rng in ranges:
        value = np.linspace(start=rng[0], stop=rng[1], num=10)
        range_values = np.append(range_values, value)
    
    range_values = range_values.reshape((len(ranges),10))

    for i in range(len(radius)):

        ## parameter list
        params = range_values[:, i]

        ax, xy = add_labels(params=params, ax=ax, fontsize=range_fontsize, fontname=fontname, return_list=True, radius=radius[i])
        x_y.append(xy)

    return ax, np.array(x_y), range_values

def get_vertices(values, xy, range_values):
    '''
    Function to get vertex coordinates(x and y) for the required polygon.

    Arguments:
        values -- list of values for each parameter.
        xy -- numpy array containing coordinate values for each label-number.
        range_values -- numpy array containing the range value for each paramter.

    Returns:
        vertices -- numpy array containing coordinates for each vertex of the polygon.
    '''
    ## init an empty list
    vertices = []

    ## calculating coordinate values
    for i in range(len(range_values)):
        
        ## list of range value for each parameter
        range_list = range_values[i, :]
        coord_list = xy[:, i]

        if range_list[0] > range_list[-1]:
            ## if range values are in reversed order
            if values[i] >= range_list[0]:
                ## if value is greater
                x_coord, y_coord = coord_list[0, 0], coord_list[0, 1]

            elif values[i] <= range_list[-1]:
                ## if value is smaller
                x_coord, y_coord = coord_list[-1, 0], coord_list[-1, 1]

            else:
                ## get indices between which the value is present
                x_coord, y_coord = utils.get_indices_between(range_list=range_list, coord_list=coord_list, value=values[i], reverse=True)

        else:
            if values[i] >= range_list[-1]:
                ## if value is greater
                x_coord, y_coord = coord_list[-1, 0], coord_list[-1, 1]

            elif values[i] <= range_list[0]:
                ## if value is smaller
                x_coord, y_coord = coord_list[0, 0], coord_list[0, 1]

            else:
                ## get indices between which the value is present
                x_coord, y_coord = utils.get_indices_between(range_list=range_list, coord_list=coord_list, value=values[i], reverse=False)

        ## add x-y coordinate in vertices as a list
        vertices.append([x_coord, y_coord])
    
    return vertices       