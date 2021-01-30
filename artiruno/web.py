# This module is only run by Brython.

import browser
import browser.aio as aio
import browser.html as H
import javascript as JS
from artiruno.vda import avda
from artiruno.interactive import setup_interactive, results_text
from artiruno.preorder import LT, GT, EQ

document, window = browser.document, browser.window
T = document.createTextNode

vda_running = False

class Quit(Exception): pass

def initialize_web_interface():
    with open('examples/jobs.json', 'r') as o:
        document['problem-definition'].value = o.read().strip()
    (document['start-button-parent'] <=
        H.BUTTON(T('Start decision-making'), id = 'start-button'))
    document['start-button'].bind('click', restart_decision_making)

def restart_decision_making(_):
    aio.run(_restart_decision_making())

async def _restart_decision_making():
    global vda_running

    # Terminate any current VDA and clear the log.
    if vda_running:
        # Kill the current VDA job.
        signal('choice', 'quit')
        # Wait till it's dead before continuing.
        await get_signal('quit_done')
    document['dm'].textContent = ''

    # Reword "start" to "restart".
    document['start-button'].textContent = 'Restart decision making'

    # Parse the problem definition.
    try:
        scenario = JS.JSON.parse(document['problem-definition'].value)
    except Exception as e:
        # There's no more specific exception type to use at the Python
        # level.
        document['dm'].textContent = str(e)
        return

    interact_args, alts, namer = setup_interactive(scenario)

    # Begin VDA.
    try:
        vda_running = True
        prefs = await interact(**interact_args)
        document['dm'] <= H.P(T(
            results_text(scenario, prefs, alts, namer)))
    except Quit:
        signal('quit_done')
    finally:
        vda_running = False

n_questions = 0

async def interact(criterion_names, alts, alt_names, **kwargs):
    global n_questions
    n_questions = 0

    async def asker(a, b):
        # Present the choices as a list with buttons.

        global n_questions
        n_questions += 1

        buttons = {}
        def button(the_id, text):
            buttons[the_id] = lambda _: signal('choice', the_id)
            return H.BUTTON(T(text), id = the_id)

        def display_item(item):
            # Display the item as a list with one criterion and value
            # per list item. Highlight the criteria value that differ
            # between the two options.
            return H.UL([
                 H.LI([T(name + ': '),
                     (T(value) if a[i] == b[i] else H.STRONG(T(value)))])
                 for i, (name, value)
                 in enumerate(zip(criterion_names, item))])

        document['dm'] <= H.DIV(
            [H.P(T('Q{}: Which would you prefer?'.format(n_questions))), H.UL([
                H.LI([button('option_a', 'Option A'),
                    display_item(a)]),
                H.LI([button('option_b', 'Option B'),
                    display_item(b)]),
                H.LI([button('equal', 'Equal'),
                    T('The two options are equally preferable')])])],
            Class = 'query')

        for button, callback in buttons.items():
            document[button].bind('click', callback)

        # Wait for the user to click a button.
        choice = await get_signal('choice')
        if choice == 'quit':
            raise Quit()

        # Replace the buttons with indicators of the user's decision.
        for button in buttons:
            document[button].replaceWith(H.SPAN(
               T('your choice' if button == choice else 'not chosen'),
               Class = 'chosen' if button == choice else 'not-chosen'))

        # Return the choice.
        return dict(option_a = GT, option_b = LT, equal = EQ)[choice]

    return await avda(
        asker = asker,
        alts = alts,
        **kwargs)

def signal(event_type, detail = None):
    document.dispatchEvent(window.CustomEvent.new(
        event_type, dict(detail = detail)))

async def get_signal(event_type):
    return (await aio.event(document, event_type)).detail
