'''This module provides a simple terminal-based interactive interface
to VDA. The session is initialized from the command line, and then
the user's choices are read from standard input.'''

import sys, json
from artiruno.preorder import LT, EQ, GT
from artiruno.vda import vda, Abort
from artiruno._version import __version__

def interact(criterion_names, alts, alt_names, **kwargs):
    n_questions = 0

    def asker(a, b):
        nonlocal n_questions

        n_questions += 1
        print('\nWhich do you prefer?')

        options = dict(a = GT, b = LT, e = EQ, q = Abort)
        for k in 'a', 'b':
            item = dict(a = a, b = b)[k]
            print(f'\n({k})' + (
                ' <<< ' + alt_names[alts.index(item)]
                    if alt_names and item in alts else ''))
            for i, (name, value) in enumerate(zip(criterion_names, item)):
                print(f'- {name}: {value}' +
                    ('   <<< different' if a[i] != b[i] else ''))
        print('\n(e) The two options are equally preferable')
        print('(q) Abort')

        print('')
        while True:
            try:
                inp = input('> ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                print('Aborted.')
                raise Abort()
            try:
                v = options[inp]
            except KeyError:
                print('Invalid input.')
                continue
            if v is Abort:
                print('Aborted.')
                raise Abort()
            return v

    prefs = vda(
        asker = asker,
        alts = alts,
        allowed_pairs_callback = apc,
        **kwargs)
    return prefs, n_questions

def apc(allowed_pairs):
    if len(allowed_pairs) > 1:
        print('Allowed pairs now:', allowed_pairs[0])

def setup_interactive(scenario):
    alt_names = None
    if alts := scenario.get('alts'):
        if isinstance(alts, dict):
            alt_names, alts = zip(*alts.items())
        alts = tuple(tuple(a[c] for c in scenario['criteria'])
            for a in alts)
    namer = ((lambda a: alt_names[alts.index(a)])
        if alt_names
        else str)
    interact_args = dict(
        criterion_names = list(scenario['criteria']),
        criteria = list(scenario['criteria'].values()),
        alt_names = alt_names,
        alts = alts,
        find_best = scenario.get('find_best'),
        max_dev = 2 * len(scenario['criteria']))
    return interact_args, alts, namer

def results_text(scenario, prefs, alts, n_questions, namer):
    # We provide more detailed text for the special case of
    # `find_best = 1`.
    if scenario.get('find_best'):
        best = prefs.extreme(scenario['find_best'], alts)
        return (
            'Best: ' + ', '.join(map(namer, best))
                if scenario['find_best'] > 1 else
            "This program couldn't identify the best alternative."
                if not best else
            'Your definitions of the criteria and alternatives imply a single best alternative: ' + namer(next(iter(best)))
                if len(best) == 1 and n_questions == 0 else
            'Your choices imply a single best alternative: ' + namer(next(iter(best)))
                if len(best) == 1 else
            'Your choices imply that all alternatives are tied for the best.'
                if alts and len(best) == len(alts) else
            'Your choices imply that these alternatives are tied for the best: ' + ', '.join(sorted(map(namer, best))))
    return 'Preferences: ' + prefs.get_subset(alts).summary(namer)

def main():
    import argparse
    args = argparse.ArgumentParser(
        prog = 'artiruno',
        description = __doc__)
    args.add_argument('--version', action = 'version',
        version = 'Artiruno ' + __version__)
    args.add_argument('FILEPATH',
        help = 'path to a JSON file describing the scenario')
    args = args.parse_args()

    with open(args.FILEPATH) as o:
        scenario = json.load(o)

    interact_args, alts, namer = setup_interactive(scenario)
    prefs, n_questions = interact(**interact_args)
    print(results_text(scenario, prefs, alts, n_questions, namer))

    try:
        import graphviz
    except ModuleNotFoundError:
        print('The Python module `graphviz` is not installed. '
            'No graph for you.')
        return
    from tempfile import mktemp
    (prefs.get_subset(alts)
        .graph(namer = namer)
        .render(filename = mktemp(), format = 'png', view = True))
