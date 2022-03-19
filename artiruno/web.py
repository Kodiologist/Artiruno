# This module is only run by Pyodide.

import asyncio, json
import js, pyodide
from artiruno.vda import avda
from artiruno.interactive import setup_interactive, results_text
from artiruno.preorder import LT, GT, EQ

# ------------------------------------------------------------
# * Global state
# ------------------------------------------------------------

vda_running = False
n_questions = 0

# ------------------------------------------------------------
# * Helpers
# ------------------------------------------------------------

class Quit(Exception): pass

T = js.document.createTextNode

signals = dict(
    choice = asyncio.Event(),
    quit_done = asyncio.Event())

def signal(event_type, value = True):
    signals[event_type].value = value
    signals[event_type].set()

async def get_signal(event_type):
    await signals[event_type].wait()
    signals[event_type].clear()
    value = signals[event_type].value
    signals[event_type].value = None
    return value

def E(id_str):
    return js.document.getElementById(id_str)

class H:
    'Create an HTML element, set attributes, and add children.'
    def __getattr__(self, element_name):
        def f(*children, **attrs):
            x = js.document.createElement(element_name)
            for c in children:
                x.appendChild(c)
            for k, v in attrs.items():
                x.setAttribute(k.lower(), v)
            return x
        setattr(H, element_name, f)
        return f
H = H()

# ------------------------------------------------------------
# * Main functions
# ------------------------------------------------------------

def initialize_web_interface():
    with open('examples/jobs.json', 'r') as o:
        E('problem-definition').value = o.read().strip()
    E('start-button-parent').appendChild(
        H.BUTTON(T('Start decision-making'), id = 'start-button'))
    E('start-button').addEventListener('click',
        pyodide.create_proxy(lambda _:
            asyncio.ensure_future(restart_decision_making())))

async def restart_decision_making():
    try:
       await _restart_decision_making()
    except Exception as e:
        E('dm').textContent = repr(e)
        return

async def _restart_decision_making():
    global vda_running

    # Terminate any current VDA and clear the log.
    if vda_running:
        # Kill the current VDA job.
        signal('choice', 'quit')
        # Wait till it's dead before continuing.
        await get_signal('quit_done')
    E('dm').textContent = ''

    # Reword "start" to "restart".
    E('start-button').textContent = 'Restart decision making'

    # Parse the problem definition.
    scenario = json.loads(E('problem-definition').value)
    interact_args, alts, namer = setup_interactive(scenario)

    # Begin VDA.
    try:
        vda_running = True
        prefs = await interact(**interact_args)
        E('dm').appendChild(H.P(T(
            results_text(scenario, prefs, alts, namer))))
    except Quit:
        signal('quit_done')
    finally:
        vda_running = False

async def interact(criterion_names, alts, alt_names, **kwargs):
    global n_questions
    n_questions = 0

    async def asker(a, b):
        # Present the choices as a list with buttons.

        global n_questions
        n_questions += 1

        buttons = {}
        def button(the_id, text):
            buttons[the_id] = pyodide.create_proxy(
                lambda _: signal('choice', the_id))
            return H.BUTTON(T(text), id = the_id)

        def display_item(item):
            # Display the item as a list with one criterion and value
            # per list item. Highlight the criteria value that differ
            # between the two options.
            return H.UL(*(
                H.LI(
                    T(name + ': '),
                    (T(value) if a[i] == b[i] else H.STRONG(T(value))))
                for i, (name, value)
                in enumerate(zip(criterion_names, item))))

        E('dm').appendChild(H.DIV(
            H.P(T('Q{}: Which would you prefer?'.format(n_questions))),
            H.UL(
                H.LI(button('option_a', 'Option A'),
                    display_item(a)),
                H.LI(button('option_b', 'Option B'),
                    display_item(b)),
                H.LI(button('equal', 'Equal'),
                    T('The two options are equally preferable'))),
            Class = 'query'))

        for button, callback in buttons.items():
            E(button).addEventListener('click', callback)

        # Wait for the user to click a button.
        choice = await get_signal('choice')
        if choice == 'quit':
            raise Quit()

        # Replace the buttons with indicators of the user's decision.
        for button, callback in buttons.items():
            E(button).replaceWith(H.SPAN(
               T('your choice' if button == choice else 'not chosen'),
               Class = 'chosen' if button == choice else 'not-chosen'))
            callback.destroy()

        # Return the choice.
        return dict(option_a = GT, option_b = LT, equal = EQ)[choice]

    return await avda(
        asker = asker,
        alts = alts,
        **kwargs)
