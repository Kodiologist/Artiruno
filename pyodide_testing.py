# Set up the test suite for running it with Pyodide.
# Command-line arguments are passed to `pytest`.
# N.B. `--slow` on Firefox takes about 15 minutes on my fairly beefy
# laptop, vs. less than a tenth of that with native CPython.

import sys, tempfile, shutil, pathlib

pyodide_version = '0.19.1'

td = pathlib.Path('/tmp/artiruno_pyodide_testing_SNtl1aBcvhoD5PO8upr4')
td.mkdir(exist_ok = True)
shutil.make_archive(str(td / 'artiruno'), 'tar')

page = '''
    <!DOCTYPE html>
    <script src="https://cdn.jsdelivr.net/pyodide/vPYV/full/pyodide.js"></script>
    <title>Artiruno Pyodide testing</title>
    <script>
    async function main()
       {let pyodide = await loadPyodide(
           {indexURL: "https://cdn.jsdelivr.net/pyodide/vPYV/full/"})
        await pyodide.loadPackage('pytest')
        await pyodide.runPythonAsync(`
            from pyodide.http import pyfetch
            await (await pyfetch('artiruno.tar')).unpack_archive()`)
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
