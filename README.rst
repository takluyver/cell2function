IPython extension to convert a cell to a function

Code that starts off as exploratory interactive code in a notebook often
solidifies into something that you want to reuse in other cells. This utility
turns a cell into a function definition. The new function expects every variable
that was used before it's defined, and returns every variable defined in that cell.
This will rarely be right, but deleting code is easier than writing it.

To use it, load the extension with ``%load_ext cell2function``, and then add
``%%cell2function`` at the top of cells you want to turn into functions. The new
functions will appear in a new cell beneath.

See `the demo notebook <nbviewer.ipython.org/github/takluyver/cell2function/blob/master/Cell2function demo.ipynb>`_
for more information.