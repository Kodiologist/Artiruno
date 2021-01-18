import sys, json
from tempfile import mktemp
from artiruno.preorder import LT, EQ, GT
from artiruno.vda import vda, Abort
from artiruno._version import __version__

def interact(criterion_names, alts, alt_names, **kwargs):

    def asker(a, b):
        print('\nWhich do you prefer?')

        options = dict(a = GT, b = LT, e = EQ, q = Abort)
        for k in 'a', 'b':
            item = dict(a = a, b = b)[k]
            print(f'\n({k})' + (
                ' <<< ' + alt_names[alts.index(item)]
                    if alt_names and item in alts else ''))
            for name, value in zip(criterion_names, item):
                print(f'- {name}: {value}')
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

    return vda(
        asker = asker,
        alts = alts,
        allowed_pairs_callback = apc,
        **kwargs)

def apc(allowed_pairs):
    if len(allowed_pairs) > 1:
        print("Allowed pairs now:", allowed_pairs[0])

def main():
    print('Artiruno', __version__)

    with open(sys.argv[1]) as o:
        scenario = json.load(o)

    alt_names = None
    if alts := scenario.get('alts'):
        if isinstance(alts, dict):
            alt_names, alts = zip(*alts.items())
        alts = tuple(tuple(a[c] for c in scenario['criteria'])
            for a in alts)

    prefs = interact(
        criterion_names = list(scenario['criteria']),
        criteria = list(scenario['criteria'].values()),
        alt_names = alt_names,
        alts = alts,
        find_best = scenario.get('find_best'),
        max_dev = 2 * len(scenario['criteria']))

    print("Best:", ", ".join(
        alt_names[alts.index(a)] if alt_names else str(a)
        for a in prefs.maxes(alts)))

    (prefs.get_subset(alts)
        .graph(namer = (lambda a: alt_names[alts.index(a)])
            if alt_names else str)
        .render(filename = mktemp(), format = 'png', view = True))
