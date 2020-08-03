import setuptools

with open('README.rst', 'r') as o:
    long_description = o.read()

setuptools.setup(
    name = 'artiruno',
    author = 'Kodi B. Arfer',
    description = 'Verbal decision analysis',
    long_description = long_description,
    long_description_content_type = 'text/x-rst',
    url = 'https://github.com/Kodiologist/Artiruno',
    packages = setuptools.find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        'Operating System :: OS Independent'],
    python_requires = '>=3.8')
