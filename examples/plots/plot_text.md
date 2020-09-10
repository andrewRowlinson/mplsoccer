# An Automatic Way of Adding Text in Matplotlib

* If you need any help or have any suggestion/feedback ping me [here](https://twitter.com/slothfulwave612).

## Content

* [Overview](#overview)
* [Documentation](#soccerplotsutilsplot_text)
* [Examples](#examples)


## Overview

* `soccerplots` package now comes with a *utility function* that can help users to add and modify text without the need of using `text()` method.

* `plot_text()` is the method which can be used to add and modify text as per the users need.

* Here, we will cover the documentation of `plot_text()` method with some examples to show how one can add and modify text.

## soccerplots.utils.plot_text

```python
soccerplots.utils.plot_text(x, y, text, text_dict, ax, color_rest='k', align="left", fontsize=None, **kwargs)
```

|  No.  |  Parameter  |  About Parameter  |
|-------|-------------|-------------------|
| 1. | x | (float) x-coodrinate value for text.|
| 2. | y | (float) y-coodrinate value for text.|
| 3. | text| (str) the text that will be added.|
| 4. | text_dict | (dict) contains words that the user wants to format.|
| 5. | ax | (ax.Axes) axis object.|
| 6. | color_rest| (str, optional) color for the text. Defaults to 'k'.|
| 7. | align | (str, optional) alignment of boxes. Defaults to "left".|
| 8. | fontsize | (float, optional) size of the text. Default to None.|
| 9. | \*\*kwargs(optional)| all other keyword arguments are passed on to matplotlib.axes.Axes.text.|

|  No.  |  Returns  |  About  |
|-------|-----------|---------|
|  1.   |  ax       | (axes.Axes)axis object|


## Examples

* Here we will look into some of the examples that can help in adding text using `soccerplots.utils.plot_text()` method.

* **Examples Content:**
  * [Adding text with colors](#adding-text-with-colors)
  * [Add Fontstyle](#add-fontstyle)
  * [Coloring consecutive words](#coloring-consecutive-words)
  * [Fontweight](#fontweight)
  * [Changing size of words](#changing-size-of-words)
  * [Changing fontsize of the whole text](#changing-fontsize-of-the-whole-text)
  * [Changing fontstyle](#changing-fontstyle)
  * [Add multiple lines with colors and styles](#Add-multiple-lines-with-colors-and-styles)
  * [ignore_last](#ignore_last)
  * [Different fontsize for different lines](#different-fontsize-for-different-lines)
  * [Quote](#quote)
  
### Adding text with colors

* Here, we will add a text saying `Hello World!!! This is Python Programming` and will color `Python` with `green` color and `Programming` with `crimson` color.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "Hello World!!! This is Python Programming"

## addition info about text
text_dict = dict(
    Python = dict(color="green"),         ## Python color is "green"
    Programming = dict(color="crimson")   ## Programming color is "crimson"
)

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax
)
```

* *Output:*

![1_simple_text](https://user-images.githubusercontent.com/33928040/92321757-2e1b2b00-f04a-11ea-816b-683b25a653b2.jpg)


### Add Fontstyle

* We will add a text saying `Hello World!!! Matplotlib is Love` and will add `italic` fontstyle to `Hello World!!!` and color `Matplotlib` and `Love`.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "Hello World!!! Matplotlib is Love"

## addition info about text
text_dict = {
    "Hello": dict(fontstyle="italic"),      ## Hello is italic
    "World!!!": dict(fontstyle="italic"),   ## World!!! is italic
    "Matplotlib": dict(color="#897941"),    ## color to Matplotlib
    "Love": dict(color="crimson")           ## color to Love
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax
)
```

* *Output:*

![2_fontstyle](https://user-images.githubusercontent.com/33928040/92321843-e2b54c80-f04a-11ea-96ea-913a244b804a.jpg)

* There is an **alternative way** of doing this.

* Since we can see that in the above text `Hello` and `World!!!` are coming together. So without passing them as multiple keys we can pass them as a single key, for that we have to change the `text` a bit.

* The `text` will now look like: `Hello_World!!! Matplotlib is Love` and then we will pass `ignore=True` to the dictionary for the `Hello_World!!!` key in `text_dict`.(see code-snippet below)

* `_`(underscore) will tell the method that we are combining these two words and the modification will come for both these words, `ignore=True` will tell the method to ignore the `_` sign in the text and replace it with ` `(space).

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "Hello_World!!! Matplotlib is Love"                      ## _ has been added

## addition info about text
text_dict = {
    "Hello_World!!!": dict(fontstyle="italic", ignore=True),    ## ignore_last has been set to True
    "Matplotlib": dict(color="#897941"),                        ## color to Matplotlib
    "Love": dict(color="crimson")                               ## color to Love
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax
)
```

* *Output:*

![2_fontstyle_2](https://user-images.githubusercontent.com/33928040/92322054-923eee80-f04c-11ea-907a-1ed46939763a.jpg)


### Coloring consecutive words

* Our text here is the same as above `Hello World!!! Matplotlib is Love` and we will color `Hello World!!!` also making it italic.

* Again, we will change the text a bit adding `_` between `Hello` and `World!!!` and will pass `ignore=True` and some color-value to the dictionary.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "Hello_World!!! Matplotlib is Love"       ## added underscore

## addition info about text
text_dict = {
    "Hello_World!!!": dict(fontstyle="italic", color="#3524A6", ignore=True),    ## added color 
    "Matplotlib": dict(color="#897941"),      ## color to Matplotlib
    "Love": dict(color="crimson")             ## color to Love
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax
)
```

* *Output:*

![3_coloring_cons](https://user-images.githubusercontent.com/33928040/92322246-b7802c80-f04d-11ea-8888-691b554520d1.jpg)

### Fontweight

* The text is: `Hello World!!! Matplotlib is Love`.

* Here we will add `fontweight="bold"` for `Matplotlib` and `Love` and `Hello World!!!` will remain italic and will add some color too.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "Hello_World!!! Matplotlib is Love"

## addition info about text
text_dict = {
    "Hello_World!!!": dict(fontstyle="italic", color="#3524A6", ignore=True),    ## italic and color
    "Matplotlib": dict(color="#897941", fontweight="bold"),                      ## bold and color
    "Love": dict(color="crimson", fontweight="bold")                             ## bold and color
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax
)
```

* *Output:*

![4_bold](https://user-images.githubusercontent.com/33928040/92322367-71779880-f04e-11ea-8539-9427bf601b31.jpg)


### Changing size of words

* Here we will see how to change the size of words in a text.

* Our text is `This word is small and this word is large` and we will add color to `word` and make it `bold` and change `fontsize` for `small` and `large`.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "This word is small and this word is large"

## addition info about text
text_dict = {
    "word": dict(fontweight="bold", color="#897941"),    ## bold and color
    "small": dict(fontsize="small"),                     ## fontsize is "small", can pass a floating value as well
    "large": dict(fontsize="large")                      ## fontsize is "large", can pass a floating value as well
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax
)
```

* *Output:*

![4_small](https://user-images.githubusercontent.com/33928040/92322484-15614400-f04f-11ea-9b0a-dbe8918879f5.jpg)


## Changing fontsize of the whole text

* Our text here is: `Computer Programming is just awesome`

* And we will increase the fontsize for our whole string also adding color to `awesome` and making `Computer Programming` italic.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "Computer_programming is just awesome"

## addition info about text
text_dict = {
    "awesome": dict(fontweight="bold", color="#897941"),            ## bold with color
    "Computer_programming": dict(fontstyle="italic", ignore=True)   ## italic 
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax, fontsize=15       ## increased fontsize
)
```

* *Output:*

![4_small_fontfamily](https://user-images.githubusercontent.com/33928040/92322852-89045080-f051-11ea-8c8e-ceb2c1895e85.jpg)


### Changing fontstyle

* We will now see how to change fontstyle, the text is the same as above.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "Computer_programming is just awesome"

## addition info about text
text_dict = {
    "awesome": dict(fontweight="bold", color="#897941"),
    "Computer_programming": dict(fontstyle="italic", ignore=True)
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax, fontfamily="Purisa"        ## added fontstyle
)
```

* *Output:*

![4_small_fontsize](https://user-images.githubusercontent.com/33928040/92322896-dc769e80-f051-11ea-8c84-0caf9057cf0a.jpg)


### Add multiple lines with colors and styles

* Here we will add two lines:
```
This is Line Number 01
And This is Line Number 02
```

* We will add color, italic fontstyle and bold fontweight to `Number 01`, and will add color, oblique fontstyle and roman fontweight to `Number 02`.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = "This is Line Number_01\nAnd This is Line Number_02"

## addition info about text
text_dict = {
    "Number_01": dict(color="crimson", fontstyle="italic", fontweight="bold", ignore=True),     ## added modifications
    "Number_02": dict(color="#897941", fontstyle="oblique", fontweight="roman", ignore=True)    ## added modifications
}

## create subplot
fig, ax = plt.subplots()

## plot the text
ax = plot_text(
    x = 0.5, y = 0.5, 
    text = text, text_dict = text_dict, ax = ax
)
```

* *Output:*

![5_mul_lines](https://user-images.githubusercontent.com/33928040/92322966-658dd580-f052-11ea-93da-7d0e228e9f05.jpg)

* **Note:** You can pass `text` for multiple line strings like this as well:

```python
text = """This is Line Number_01
And This is Line Number_02"""
```

### ignore_last

* Let's say we have `Corners, Crosses, Freekicks and Passes` as our text and we want to color `Corners` and `Crosses` but we don't want to color the `,` that are included in those words, what we will do is pass another argument `ignore_last=True`, this will ignore the last character of a word and make the required changes.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = """How are the best creators in Europe's top 5 league making chances
through Corners, Crosses, Indirect_Freekicks and Open_Play_Passes?"""

## addition info about text
## ignore_last will ignore the last word
text_dict = {
    "Corners,": dict(color="skyblue", ignore_last=True),
    "Crosses,": dict(color="gold", ignore_last=True),                    
    "Indirect_Freekicks": dict(color="grey", ignore=True),
    "Open_Play_Passes?": dict(color="crimson", ignore=True, ignore_last=True)
}

## create subplot
fig, ax = plt.subplots(facecolor="#121212")
ax.set_facecolor("#121212")
ax.set(xlim=(-2, 2))
ax.axis("off")

## plot the text
ax = plot_text(
    x = 0., y = 0.6, 
    text = text, text_dict = text_dict, ax = ax, 
    color_rest="#F0FFF0", fontsize=9
)
```

* *Output:*

![6_foot_1](https://user-images.githubusercontent.com/33928040/92323179-39735400-f054-11ea-987d-9bc429e0bfdc.jpg)


### Different fontsize for different lines

* Let's say we have the following text:
```python
text = """La Liga 2019/20: Expected Performance
Rolling average comparison between goal difference & expected goal difference"""
```

* And now we want to have larger fontsize for the first line and a smaller one for the second. We can do this by passing a list of fontsizes to `plot_text` method.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## text to be plotted
text = """La Liga 2019/20: Expected Performance
Rolling average comparison between goal_difference & expected_goal_difference"""

## text dict
text_dict = {
    "goal_difference": dict(color="skyblue", ignore=True),
    "expected_goal_difference": dict(color="gold", ignore=True)
}

## create subplot
fig, ax = plt.subplots(facecolor="#121212")
ax.set_facecolor("#121212")
ax.set(xlim=(-2, 2))
ax.axis("off")

## plot the text
ax = plot_text(
    x = 0., y = 0.6, 
    text = text, text_dict = text_dict, ax = ax, 
    color_rest="#F0FFF0", fontsize=[13, 9], va="top"     ## list of fontsize and 
                                                         ## va="top" to reduce distance between first and second line
)
```

* *Output:*

![6_foot_4](https://user-images.githubusercontent.com/33928040/92323332-78ee7000-f055-11ea-8a17-3b20b581b7a0.jpg)


## Quote

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from soccerplots.utils import plot_text

## file at http://bit.do/johantxt
with open("johan.txt", "r") as ofile:
    text = ofile.read()

text_dict = {
    "youth_teams": dict(color="#00FF00", fontstyle="italic", ignore=True),
    "first_team.": dict(color="#F5F5F5", fontstyle="italic", 
                       fontweight="semibold", ignore=True, ignore_last=True),
    "emhasis": dict(color="gold", fontweight="demibold"),
    "learning.": dict(color="#00FFFF", ignore_last=True),
    "suspicion": dict(color="#F04D4D", fontweight="roman"),
    "youth_coaches": dict(color="#00FF00", fontstyle="italic", ignore=True),
    "winning.": dict(color="crimson", ignore_last=True),
    "reputation.": dict(color="#008080", fontweight="bold", ignore_last=True),
    "club.": dict(color="gold", ignore_last=True),
    "talent": dict(color="#C674C6"),
    "learn,": dict(color="#00FFFF", fontweight="bold", ignore_last=True),
    "point?": dict(color="lime", ignore_last=True),
    "developing": dict(color="#32CD32"),
    "Johan_Cruyff": dict(color="#FFA500", ignore=True, fontsize=15)
}

## create subplot
fig, ax = plt.subplots(figsize=(12, 4), facecolor="#121212")
ax.set_facecolor("#121212")
ax.axis("off")

ax = plot_text(0.5, 0.5, text, text_dict, ax=ax, color_rest="#FFFAFA", 
               fontsize=12, fontfamily="Norasi")
```

* *Output:*

![quote](https://user-images.githubusercontent.com/33928040/92323968-b4d80400-f05a-11ea-9db5-ac62f8e1790d.jpg)

---