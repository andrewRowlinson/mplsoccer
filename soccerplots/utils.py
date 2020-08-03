'''
author: Anmol Durgapal || @slothfulwave612

Python module containing helper functions.
'''

## necessary packages/modules
import numpy as np

def get_coordinates(n):
    '''
    Function for getting coordinates and rotation values for the labels.

    Argument:
        n -- int, number of labels.
    
    Returns:
        list of coordinate and rotation values.
    '''
    ## calculate alpha
    alpha = 2 * np.pi/n

    ## rotation values
    alphas = alpha * np.arange(n)

    ## x-coordinate value
    coord_x = np.cos(alphas)

    ## y-coordinate value
    coord_y = np.sin(alphas)

    return np.c_[coord_x, coord_y, alphas]

def get_vertex_coord(old_value, old_min, old_max, new_min, new_max):
    '''
    Function for getting coordinate for each vertex of the polygon.

    Arguments:
        old_value, old_min, old_max, new_min, new_max -- float values.

    Returns:
        new_value -- float value(the coordinate value either x or y).
    '''
    ## calculate the value
    new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min

    return new_value

def get_indices_between(range_list, coord_list, value, reverse):
    '''
    Function to get the x-coordinate and y-coordinate for the polygon vertex.

    Arguments:
        range_list -- list of range value for a particular parameter.
        coord_list -- list of coordinate values where the numerical labels are placed.
        value -- float, the value of the parameter.
        reverse -- bool, to tell whether the range values are in reversed order or not.

    Returns:
        x_coord, y_coord -- x-coordinate and y-coordinate value.
    '''
    ## getting index value
    idx_1, idx_2 = get_index(array=range_list, value=value, reverse=reverse)

    ## get x coordinate
    x_coord = get_vertex_coord(
        old_value=value,
        old_min=range_list[idx_1],
        old_max=range_list[idx_2],
        new_min=coord_list[idx_1, 0],
        new_max=coord_list[idx_2, 0]
    )

    ## get y coordinate
    y_coord = get_vertex_coord(
        old_value=value,
        old_min=range_list[idx_1],
        old_max=range_list[idx_2],
        new_min=coord_list[idx_1, 1],
        new_max=coord_list[idx_2, 1]
    )

    return x_coord, y_coord

def get_index(array, value, reverse):
    '''
    Function to get the indices of two list items between which the value lies.

    Arguments:
        array -- list containing numerical values.
        value -- float/int, value to be searched.
        reverse -- bool, whether or not the range values are in reverse order.

    Returns:
        the two indices between which value lies.
    '''
    
    if reverse == True:
        ## loop over the array/list
        for i in range(0, len(array) - 1):
            if array[i] >= value >= array[i+1]:
                return i, i+1

    ## loop over the array/list
    for i in range(0, len(array) - 1):
        if array[i] <= value <= array[i+1]:
            return i, i+1