====================================
Artiruno documentation
====================================

.. contents::
   :local:

.. role:: html(raw)
   :format: html

Introduction
============================================================

This manual describes Artiruno version |release|.

Artiruno is a Python package for performing verbal decision analysis (VDA) in the manner of ZAPROS (Larichev & Moshkovich, 1995) and UniComBOS (Ashikhmin & Furems, 2005). VDA is a class of decision-support software for multiple-criteria decision-making that doesn't ask the user for explicit preference functions or criterion weights. Instead, the user is asked questions such as "Which of these two items would you prefer?". VDA doesn't always produce a total order for the alternatives, but the weaker assumptions made about what people are capable of accurately judging helps to ensure that results aren't contaminated by arbitrary choices of numbers and functions.

Artiruno is described in more detail and empirically assessed in a paper in the :html:`<i>Journal of Multi-Criteria Decision Analysis</i>` (Arfer, 2024).

Usage
============================================================

Artiruno has a `web interface <http://arfer.net/projects/artiruno/webi>`_ and a terminal-based interface. It can also be used programmatically. To install the latest release from PyPI, use the command ``pip3 install artiruno``. You'll need `Python <http://www.python.org>`_ 3.8 or greater. You can then start an interactive VDA session with ``python3 -m artiruno FILENAME``; say ``python3 -m artiruno --help`` to see the available command-line options.

Artiruno input files are formatted in `JSON <https://www.json.org>`_. See the ``examples`` directory of the source code for examples, and :func:`artiruno.avda` below for a description of the arguments.

Artiruno has an automated test suite that uses pytest. To run it, install the PyPI packages ``pytest`` and ``pytest-asyncio`` and then use the command ``pytest``. To run it on a web browser with Pyodide, use the script ``pyodide_testing.py``. By default, regardless of platform, particularly slow tests are skipped; say ``pytest --slow`` to run all the tests.

The documentation uses Sphinx. To build it, say ``sphinx-build -b html doc/ doc/_build/``.

How it works
============================================================

Given a set of alternatives and a set of criteria on which the alternatives can be rated, Artiruno can try to find the best single alternative or the best ``n`` alternatives, or it can try to rank all the alternatives. See Arfer (2024) for details. Once the goal has been achieved, or Artiruno can't find any more useful questions to ask, Artiruno will return the inferred preferences. In interactive mode, the top-``n`` subset of your preferences (as defined by :meth:`artiruno.PreorderedSet.extreme`) will be shown if requested, and your preferences will be displayed as a graph with GraphViz if :doc:`the corresponding Python package <graphviz:index>` is available. (Graphs are not currently implemented for the web interface.)

API reference
============================================================

Verbal decision analysis
------------------------------------------------------------

.. autofunction:: artiruno.vda
.. autofunction:: artiruno.avda

Preorders
------------------------------------------------------------

.. autoclass:: artiruno.PreorderedSet
   :members:
.. autoexception:: artiruno.ContradictionError

Relations
------------------------------------------------------------

.. autoclass:: artiruno.Relation
   :members:
   :special-members:

Utility functions
------------------------------------------------------------

.. autofunction:: artiruno.choose2
.. autofunction:: artiruno.cmp

Bibliography
============================================================

Arfer, K. B. (2024). Artiruno: A free-software tool for multi-criteria decision-making with verbal decision analysis. :html:`<i>Journal of Multi-Criteria Decision Analysis, 31</i>`. ``doi:10.1002/mcda.1827``. Retrieved from http://arfer.net/projects/artiruno/paper

Ashikhmin, I., & Furems, E. (2005). UniComBOS—Intelligent decision support system for multi-criteria comparison and choice. :html:`<i>Journal of Multi-Criteria Decision Analysis, 13</i>`, 147–157. ``doi:10.1002/mcda.380``

Larichev, O. I., & Moshkovich, H. M. (1995). ZAPROS-LM—A method and system for ordering multiattribute alternatives. :html:`<i>European Journal of Operational Research, 82</i>`, 503–521. ``doi:10.1016/0377-2217(93)E0143-L``

Moshkovich, H. M., & Mechitov, A. I. (2018). Selection of a faculty member in academia: A case for verbal decision analysis. :html:`<i>International Journal of Business and Systems Research, 12</i>`, 343–363. ``doi:10.1504/IJBSR.2018.10011350``
