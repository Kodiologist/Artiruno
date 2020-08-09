Artiruno is an in-progress Python package for performing verbal decision analysis (VDA) in the manner of ZAPROS (Larichev & Moshkovich, 1995) and UniComBOS (Ashikhmin & Furems, 2005). VDA is a class of decision-support software for multiple-criteria decision-making that doesn't ask the user for explicit preference functions or criterion weights. Instead, the user is asked questions such as "Which of these two items would you prefer?". VDA doesn't always produce a total order for the alternatives, but the weaker assumptions made about what people are capable of accurately judging helps to ensure that results aren't contaminated by arbitrary choices of numbers and functions.

In ``artiruno.preorder``, Artiruno provides a class for `preordered sets`_ that should be just as useful outside the context of decision-making.

The test suite uses ``pytest``. To run it, just use the command ``pytest``.

.. _`preordered sets`: https://en.wikipedia.org/wiki/Preorder

License
============================================================

This program is copyright 2020 Kodi B. Arfer.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the `GNU General Public License`_ for more details.

.. _`GNU General Public License`: http://www.gnu.org/licenses/

References
============================================================

Ashikhmin, I., & Furems, E. (2005). UniComBOS—Intelligent decision support system for multi-criteria comparison and choice. *Journal of Multi-Criteria Decision Analysis, 13*, 147–157. ``doi:10.1002/mcda.380``

Larichev, O. I., & Moshkovich, H. M. (1995). ZAPROS-LM—A method and system for ordering multiattribute alternatives. *European Journal of Operational Research, 82*, 503–521. ``doi:10.1016/0377-2217(93)E0143-L``
