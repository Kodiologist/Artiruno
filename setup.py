import setuptools, ast

with open('README.rst', 'r') as o:
    long_description = o.read()

with open('artiruno/_version.py', 'r') as o:
    version = ast.literal_eval(ast.parse(o.read()).body[0].value)

setuptools.setup(
    name = 'artiruno',
    version = version,
    author = 'Kodi B. Arfer',
    description = 'Verbal decision analysis',
    long_description = long_description,
    long_description_content_type = 'text/x-rst',
    url = 'https://github.com/Kodiologist/Artiruno',
    packages = setuptools.find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering'],
    python_requires = '>=3.8')
