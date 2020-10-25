import sys, json
from artiruno.preorder import LT, EQ, GT
from artiruno.vda import vda

def interact(criterion_names, **kwargs):

    def asker(a, b):
        print('\nWhich do you prefer?')

        options = dict(a = GT, b = LT, c = EQ)
        for k, v in sorted(options.items()):
            print(f'\n({k})')
            if v == EQ:
                print('  The two options are equally preferable')
            else:
                for name, value in zip(criterion_names, a if v == GT else b):
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

    return vda(asker = asker, **kwargs)

def main():
    with open(sys.argv[1]) as o:
        scenario = json.load(o)

    if alts := scenario.get('alts'):
        alts = tuple(tuple(a[c] for c in scenario['criteria'])
            for a in scenario['alts'].values())

    prefs = interact(
        criterion_names = list(scenario['criteria']),
        criteria = list(scenario['criteria'].values()),
        alts = alts,
        find_best = scenario.get('find_best'),
        max_dev = 2 * len(scenario['criteria']))

    print("Best:", prefs.maxes(alts))

    prefs.get_subset(alts).render('/tmp/graph', format = 'png', view = True)
