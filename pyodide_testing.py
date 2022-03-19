# Set up the test suite for running it with Pyodide.
# Command-line arguments are passed to `pytest`.
# N.B. `--slow` on Firefox takes about 15 minutes on my fairly beefy
# laptop, vs. less than a tenth of that with native CPython.

import sys, tempfile, subprocess, re
from pathlib import Path

pyodide_version = re.search('pyodide/(v[^/]+)',
    Path('webi.html').read_text()).group(1)

td = Path('/tmp/artiruno_pyodide_testing_SNtl1aBcvhoD5PO8upr4')
td.mkdir(exist_ok = True)
subprocess.check_call(['tar',
    '--create', '--auto-compress',
    '--file', td / 'artiruno_for_pyodide.tar.gz',
    '--exclude', '__pycache__',
    *'artiruno conftest.py examples pytest.ini tests setup.py'.split()])

page = '''
    <!DOCTYPE html>
    <script src="https://cdn.jsdelivr.net/pyodide/PYV/full/pyodide.js"></script>
    <title>Artiruno Pyodide testing</title>
    <script>
    async function main()
       {let pyodide = await loadPyodide(
           {indexURL: "https://cdn.jsdelivr.net/pyodide/PYV/full/"})
        await pyodide.loadPackage('pytest')
        await pyodide.loadPackage('micropip')
        await pyodide.runPythonAsync(`
            import pyodide
            pyodide.webloop.WebLoop.close = lambda *a, **kw: True
              # Work around https://github.com/pyodide/pyodide/issues/2221
            import micropip
            await micropip.install('pytest-asyncio')
            from pyodide.http import pyfetch
            await (await pyfetch('artiruno_for_pyodide.tar.gz')).unpack_archive()`)
        console.log('pytest exit code: ', pyodide.runPython(`
            import pytest
            pytest.main(['-s', '--verbose', '--color=no', *ARGS])`))}
    main()
    </script>'''
(td / 'page.html').write_text(page
    .replace('PYV', pyodide_version)
    .replace('ARGS', repr(sys.argv[1:])))

print(f'''Now launch a test server with
    python3 -m http.server --bind 127.0.0.1 --dir {td}
open the page with
    "$BROWSER" http://0.0.0.0:8000/page.html
and check the browser console for pytest's output.''')
