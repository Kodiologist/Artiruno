====================================
Artiruno documentation
====================================

.. contents::
   :local:

Introduction
============================================================

This manual describes Artiruno version |release|.

Artiruno is a Python package for performing verbal decision analysis (VDA) in the manner of ZAPROS (Larichev & Moshkovich, 1995) and UniComBOS (Ashikhmin & Furems, 2005). VDA is a class of decision-support software for multiple-criteria decision-making that doesn't ask the user for explicit preference functions or criterion weights. Instead, the user is asked questions such as "Which of these two items would you prefer?". VDA doesn't always produce a total order for the alternatives, but the weaker assumptions made about what people are capable of accurately judging helps to ensure that results aren't contaminated by arbitrary choices of numbers and functions.

Usage
============================================================

Artiruno has a `web interface <http://arfer.net/projects/artiruno/webi>`_ and a terminal-based interface. It can also be used programmatically. To install the latest release from PyPI, use the command ``pip3 install artiruno``. You'll need `Python <http://www.python.org>`_ 3.8 or greater. You can then start an interactive VDA session with ``python3 -m artiruno FILENAME``; say ``python3 -m artiruno --help`` to see the available command-line options.

Artiruno input files are formatted in `JSON <https://www.json.org>`_. See the ``examples`` directory of the source code for examples, and :func:`artiruno.avda` below for a description of the arguments.

Artiruno has an automated test suite that uses pytest. To run it, install the PyPI packages ``pytest`` and ``pytest-asyncio`` and then use the command ``pytest``. To run it on a web browser with Pyodide, use the script ``pyodide_testing.py``. By default, regardless of platform, particularly slow tests are skipped; say ``pytest --slow`` to run all the tests.

The documentation uses Sphinx. To build it, say ``sphinx-build -b html doc/ doc/_build/``.

How it works
============================================================

Given a set of alternatives and a set of criteria on which the alternatives can be rated, Artiruno can try to find the best single alternative or the best ``n`` alternatives, or it can try to rank all the alternatives. Here are the basic assumptions that Artiruno makes about the decision-making scenario:

- There are finitely many *criteria*, each of which is an ordered list of finitely many levels, and levels that are listed later are strictly better than earlier ones. For example, a criterion could be ``Location``, with levels ``["Far", "Some distance", "Almost ideal"]``, which means that ``Some distance`` is preferred to ``Far``.
- An *item*, or option to be considered, is completely described by its values on the criteria. Each item has exactly one value for each criterion.
- Your preferences between items are ordered, such that ``a ≤ b`` means that item ``a`` is worse than or equally as good as item ``b``. Specifically, your preferences are an *eventually total preorder*, meaning that:

  - They're *reflexive*: you're indifferent between an item and itself.
  - They're *transitive*: if for items ``a``, ``b``, and ``c``, ``a ≤ b`` and ``b ≤ c``, then ``a ≤ c``.
  - They're *eventually total*: for any two distinct items ``a`` and ``b``, exactly one of ``a < b``, ``a > b``, or ``a ≈ b`` must be true (with the last relation meaning indifference or equivalence: ``a ≤ b`` and ``a ≥ b`` and yet ``a ≠ b``). However, Artiruno's knowledge of your preferences is in general incomplete, and its ignorance of the relation between a pair of items ``a`` and ``b`` is represented as incomparability. This is the sense in which the totality is only eventual.

- The *rule of segmentwise dominance*:

  - In the simple case, the *rule of dominance* states that if ``a`` is strictly worse than ``b`` on one criterion, and no better than ``b`` on all other criteria, then ``a < b``.
  - Segmentwise dominance generalizes dominance as follows. For each item ``p`` and subset of the criteria ``S``, let ``dev_from_ref(S, p)`` be the item that has the best value on all criteria except possibly the criteria in ``S``, for which it has the criterion values of ``p``. In other words, ``dev_from_ref(S, p)`` deviates from the *reference item*—the best possible item—only on ``S``, and values for these criteria come from ``p``. Then let ``a`` and ``b`` be distinct items and ``{A[1], A[2], …, A[n]}`` and ``{B[1], B[2], …, B[n]}`` be partitions of the criteria. If ``dev_from_ref(A[i], a) ≤ dev_from_ref(B[i], b)`` for all ``i``, and at least one of these inequalities is strict, then ``a < b``; if none of the inequalities are strict, then ``a ≈ b`` instead.

At a high level, the way Artiruno works is by applying transitivity and dominance to make as many inferences as it can, and then asking you questions about hypothetical items (generated by ``dev_from_ref``) in order to apply segmentwise dominance and narrow things down. Artiruno will try to ask as few questions as possible in order to reach the goal you requested (e.g., finding the best item among a set of alternatives), and it will try to ask simpler questions (with hypothetical items that minimally deviate from the reference item) before more complex ones.

Once the goal has been achieved, or Artiruno can't find any more useful questions to ask, Artiruno will return the inferred preferences. In interactive mode, the top-``n`` subset of your preferences (as defined by :meth:`artiruno.PreorderedSet.extreme`) will be shown if requested, and your preferences will be displayed as a graph with GraphViz if :doc:`the corresponding Python package <graphviz:index>` is available. (Graphs are not currently implemented for the web interface.)

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

.. raw:: html

    <p>Ashikhmin, I., & Furems, E. (2005). UniComBOS—Intelligent decision support system for multi-criteria comparison and choice. <i>Journal of Multi-Criteria Decision Analysis, 13</i>, 147–157. <code>doi:10.1002/mcda.380</code>

    <p>Larichev, O. I., & Moshkovich, H. M. (1995). ZAPROS-LM—A method and system for ordering multiattribute alternatives. <i>European Journal of Operational Research, 82</i>, 503–521. <code>doi:10.1016/0377-2217(93)E0143-L</code>
