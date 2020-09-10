"""
__author__: Anmol_Durgapal(@slothfulwave612)

Python module containing helper functions.
"""

## necessary packages/modules
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, TextArea, HPacker, VPacker
from PIL import Image

def get_coordinates(n):
    """
    Function for getting coordinates and rotation values for the labels.

    Args:
        n (int): number of labels.

    Returns:
        list: coordinate and rotation values.
    """    

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
    """
    Function for getting coordinate for each vertex of the polygon.

    Args:
        old_value, old_min, old_max, new_min, new_max -- float values.

    Returns:
        float: the coordinate value either x or y.
    """    

    ## calculate the value
    new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min

    return new_value

def get_indices_between(range_list, coord_list, value, reverse):
    """
    Function to get the x-coordinate and y-coordinate for the polygon vertex.

    Args:
        range_list (list): range value for a particular parameter.
        coord_list (list): coordinate values where the numerical labels are placed.
        value (float): the value of the parameter.
        reverse (bool): to tell whether the range values are in reversed order or not.

    Returns:
        tuple: x-coordinate and y-coordinate value.
    """    

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
    """
    Function to get the indices of two list items between which the value lies.

    Args:
        array (list): containing numerical values.
        value (float/int): value to be searched.
        reverse (bool): whether or not the range values are in reverse order.

    Returns:
        int: the two indices between which value lies.
    """    

    if reverse == True:
        ## loop over the array/list
        for i in range(0, len(array) - 1):
            if array[i] >= value >= array[i+1]:
                return i, i+1

    ## loop over the array/list
    for i in range(0, len(array) - 1):
        if array[i] <= value <= array[i+1]:
            return i, i+1

def set_labels(ax, label_value, label_axis):
    """
    Function to set label for a given axis.

    Args:
        ax (axes.Axes): axis object.
        label_value (list): ticklabel values.
        label_axis (str): axis name, 'x' or 'y'

    Returns:
        list: label names
    """    

    if label_axis == 'x':
        ax.set_xticks(np.arange(len(label_value)))
        axis = ax.get_xticklabels()
    else:
        ax.set_yticks(np.arange(len(label_value)) + 1)
        axis = ax.get_yticklabels()
    
    ## fetch labels
    labels = [items.get_text() for items in axis]

    ## init a count variable
    if label_axis == 'x':
        count = 0
    else:
        count = len(label_value) - 1
    
    ## iterate through all the labels and change the label name
    for i in range(len(labels)):
        labels[i] = label_value[count]

        if label_axis == 'x':
            count += 1
        else:
            count -= 1
    
    return labels            

def add_image(image, fig, left, bottom, width=None, height=None, **kwargs):
    """
    -----> The method is taken from mplsoccer package (from github) <-----
    -----> Andy Rowlinson(@numberstorm) <-----

    Adds an image to a figure using fig.add_axes and ax.imshow

    Args:
        image (str): image path.
        fig (matplotlib.figure.Figure): figure object
        left (float): The left dimension of the new axes.
        bottom (float): The bottom dimension of the new axes.
        width (float, optional): The width of the new axes. Defaults to None.
        height (float, optional): The height of the new axes. Defaults to None.
        **kwargs: All other keyword arguments are passed on to matplotlib.axes.Axes.imshow.

    Returns:
        matplotlib.figure.Figure: figure object.
    """    
    ## open image
    image = Image.open(image)

    ## height, width, channel of shape
    shape = np.array(image).shape
    
    image_height, image_width =  shape[0], shape[1]
    image_aspect = image_width / image_height
    
    figsize = fig.get_size_inches()
    fig_aspect = figsize[0] / figsize[1]
    
    if height is None:
        height = width / image_aspect * fig_aspect
    
    if width is None:
        width = height*image_aspect/fig_aspect
    
    ## add image
    ax_image = fig.add_axes((left, bottom, width, height))
    ax_image.axis('off')  # axis off so no labels/ ticks
    
    ax_image.imshow(image, **kwargs)
    
    return fig

def plot_text(x, y, text, text_dict, ax, color_rest='k', align="left", fontsize=None, **kwargs):
    """
    Function to plot text.

    Args:
        x (float): x-coodrinate value for text.
        y (float): y-coodrinate value for text.
        text (str): the text that will be plotted.
        text_dict (dict): contains words that the user wants to format.
        ax (axes.Axes): axis object.
        color_rest (str, optional): color for the string. Defaults to 'k'.
        align (str, optional): alignment, can have these values {'top', 'bottom', 'left', 'right', 'center', 'baseline'}. Defaults to "left". 
        fontsize (float, optional): size of the font. Defaults to None.
        **kwargs(optional): All other keyword arguments are passed on to matplotlib.axes.Axes.imshow.

    Returns:
        axes.Axes: axis object
    """    

    ## init an empty list and a count variable to 0
    hpacker_list = []
    count = 0
    
    for sentence in text.split('\n'):
        ## init an empty string and list
        temp_string = ""
        temp_hpacker = []
        
        for word in sentence.split(' '):
            present = text_dict.get(word)
            
            if present == None:
                temp_string += (word + " ")
                
            elif present and temp_string != "":
                if type(fontsize) == list:
                    size = fontsize[count]
                else:
                    size = fontsize

                textbox = TextArea(
                    temp_string.strip(),
                    textprops = dict(
                        color = color_rest,  
                        size = size,
                        **kwargs
                    )
                )
                temp_hpacker.append(textbox)
                temp_string = ""
            
            if present:
                if present.get("color") == None:
                    color = color_rest
                else:
                    try:
                        color = present["color"]
                    except Exception:
                        color = present["fontcolor"]

                if present.get("ignore") == True:
                    word = word.replace('_', ' ')
                    del present["ignore"]

                if present.get("size") or present.get("fontsize"):
                    try:
                        size = present["fontsize"]
                    except Exception:
                        size = present["size"]
                elif type(fontsize) == list:
                    size = fontsize[count]
                else:
                    size = fontsize

                if present.get("ignore_last") == True:
                    w_1 = word[:-1]
                    w_2 = word[-1]
                    del present["ignore_last"]

                    textbox_1 = TextArea(
                        w_1,
                        textprops = dict(      
                            present,
                            color = color,
                            size = size,
                            **kwargs
                        )
                    )

                    textbox_2 = TextArea(
                        w_2,
                        textprops = dict(      
                            present,
                            color = color_rest,
                            size = size,
                            **kwargs
                        )
                    )    

                    temp_box = HPacker(children=[textbox_1, textbox_2], align=align, pad=0, sep=0)
                    temp_hpacker.append(temp_box)

                else:
                    textbox = TextArea(
                        word,
                        textprops = dict(      
                            present,
                            color = color,
                            size = size,
                            **kwargs
                        )
                    )
                    temp_hpacker.append(textbox)
        
        if len(temp_string) > 0:
            if type(fontsize) == list:
                size = fontsize[count]
            else:
                size = fontsize

            textbox = TextArea(
                temp_string.strip(),
                textprops = dict(
                    color = color_rest,    
                    size = size,
                    **kwargs
                )
            )
            temp_hpacker.append(textbox)
        
        count += 1
        box_h = HPacker(children=temp_hpacker, align=align, pad=0, sep=4)
        hpacker_list.append(box_h)
        
    final_box = VPacker(children=hpacker_list, pad=0, sep=4)

    text = AnnotationBbox(final_box, (x, y), frameon=False)
    ax.add_artist(text)
    
    return ax    