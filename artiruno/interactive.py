import sys, json
from artiruno.preorder import LT, EQ, GT
from artiruno.vda import vda

def interact(criterion_names, alts, alt_names, **kwargs):

    def asker(a, b):
        print('\nWhich do you prefer?')

        options = dict(a = GT, b = LT, c = EQ)
        for k, v in sorted(options.items()):
            item = {GT: a, LT: b, EQ: None}[v]
            print(f'\n({k})' + (
                ' <<< ' + alt_names[alts.index(item)]
                    if item in alts else ''))
            if v == EQ:
                print('  The two options are equally preferable')
            else:
                for name, value in zip(criterion_names, item):
                    print(f'- {name}: {value}')

        print('')
        while True:
            try:
                inp = input('> ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                print('Aborted.')
                raise artiruno.Abort()
            try:
                return options[inp]
            except KeyError:
                print('Invalid input.')

    return vda(asker = asker, alts = alts, **kwargs)

def main():
    with open(sys.argv[1]) as o:
        scenario = json.load(o)

    if alts := scenario.get('alts'):
        alts = list(alts.items())
        alt_names = tuple(k for k, _ in alts)
        alts = tuple(tuple(a[c] for c in scenario['criteria'])
            for _, a in alts)

    prefs = interact(
        criterion_names = list(scenario['criteria']),
        criteria = list(scenario['criteria'].values()),
        alt_names = alt_names,
        alts = alts,
        find_best = scenario.get('find_best'),
        max_dev = 2 * len(scenario['criteria']))

    print("Best:", ", ".join(
        alt_names[alts.index(a)]
        for a in prefs.maxes(alts)))

    (prefs.get_subset(alts)
        .graph(namer = lambda a: alt_names[alts.index(a)])
        .render(filename = '/tmp/graph', format = 'png', view = True))
