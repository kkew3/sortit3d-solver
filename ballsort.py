import sys
import itertools
import contextlib
import copy
import math
import argparse
import textwrap


class State:
    def __init__(self, bins, limits):
        """
        :param bins: a list of lists of symbols
        """
        assert len(bins) == len(limits)
        self.bins = bins
        self.limits = limits

        self._ncolors = []
        for b in self.bins:
            self._ncolors.extend(b)
        self._ncolors = len(set(self._ncolors))

    def __hash__(self):
        return hash((
            tuple(sorted(map(''.join, self.bins))),
            tuple(self.limits),
        ))

    def __eq__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        if self.limits != other.limits:
            return NotImplemented
        return sorted(map(''.join, self.bins)) \
                == sorted(map(''.join, other.bins))

    def __str__(self):
        w = max(math.ceil(math.log10(x)) if x else 2 for x in self.limits)
        sbuf = []
        for l, b in zip(self.limits, self.bins):
            if not l:
                l = 'oo'
            else:
                l = str(l)
            sbuf.append(l.rjust(w))
            sbuf.append(' [')
            sbuf.append(''.join(b))
            sbuf.append('\n')
        del sbuf[-1]
        return ''.join(sbuf)

    def __repr__(self):
        return str(self).replace('\n', '; ')

    def __bool__(self):
        return (max(len(set(x)) for x in self.bins) <= 1 and sum(
            1 for x in self.bins if not x) == len(self.bins) - self._ncolors)

    def apply(self, from_to):
        f, t = from_to
        if not self.bins[f]:
            raise ValueError
        if len(self.bins[t]) == self.limits[t]:
            raise ValueError
        new = copy.deepcopy(self)
        top = new.bins[f][-1]
        del new.bins[f][-1]
        new.bins[t].append(top)
        return new

    def neighbors(self):
        nbrs = []
        for x in itertools.permutations(range(len(self.bins)), 2):
            with contextlib.suppress(ValueError):
                state = self.apply(x)
                if state not in nbrs:
                    nbrs.append((x, state))
        return nbrs


def heuristics(state):
    diversity = 0
    for b in state.bins:
        diversity += max(0, len(set(b)) - 1)**2
    return diversity


def search_path(state):
    """
    >>> root = State([['A', 'B'], []], [2, 2])
    >>> search_path(root)
    [(0, 1)]
    >>> root = State([list('ABC'), [], []], [3, 3, 3])
    >>> route = search_path(root)
    >>> for step in route:
    ...     root = root.apply(step)
    >>> assert route
    >>> root = State([list('PGYA'), list('PPBG'), [], list('BYRY'),
    ...               list('YRRB'), list('GGBP'), []],
    ...              [4] * 7)
    >>> route = search_path(root)
    >>> for step in route:
    ...     root = root.apply(step)
    >>> assert route
    """
    path = {}
    open_queue = [state]
    open_set = set([state])
    closed_set = set()
    while open_queue:
        open_queue.sort(key=heuristics)
        bot = open_queue.pop(0)
        open_set.remove(bot)
        if bot:
            break
        if bot not in closed_set:
            closed_set.add(bot)
            for diff, nbr in bot.neighbors():
                if nbr not in closed_set and nbr not in open_set:
                    path[nbr] = bot, diff
                    open_queue.append(nbr)
                    open_set.add(nbr)
    if bot:
        rev_route = []
        p = bot
        while p != state:
            p, d = path[p]
            rev_route.append(d)
        route = list(reversed(rev_route))
        return route
    return None


def load_states_from_file(infile):
    def _load_state(buffer):
        limits = []
        bins = []
        for line in buffer:
            ul, tube = line.split(maxsplit=1)
            try:
                ul = int(ul)
            except ValueError:
                ul = None
            limits.append(ul)
            bins.append(list(tube[1:]))
        return State(bins, limits)

    lines = filter(None, map(str.strip, infile))
    states = []
    sbuf = []
    for l in lines:
        if l.startswith('-') and sbuf:
            states.append(_load_state(sbuf))
            sbuf.clear()
        elif not l.startswith('#'):
            sbuf.append(l)
    if sbuf:
        states.append(_load_state(sbuf))
    return states


def make_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Sort it 3D game solver. When specifying problems in FILE, the
            problems should be split by at least one hyphen, and the hash
            sign at the beginning of a line leads to a line of comment.
            See below for an example how to specifying problems.

                           *** Begin of example FILE ***
            # Problem 1
            # There are two bins, both of which hold unlimited number of balls.
            # The first bin contain two balls 'A' and 'B'; the second one is
            # empty.
            oo [AB
            oo [

            # hyphens split up problems
            ---

            # Problem 2
            # There are three bins, which hold at most 3, 4 and 5 balls
            # respectively. The first bin contain three balls 'A', 'B' and 'C',
            # the second one empty, and the third one a single ball 'B'.
            3 [ABC
            4 [
            5 [B
                            *** End of example FILE ***

            All balls are enumerated from the bottom to the top of a bin.
            For example, `[ABC` denotes from top to bottom 'C', 'B', 'A' three
            balls.

            The bin index starts from 0. `X->Y` in the answer means move the
            top ball from bin X to bin Y. Therefore, to solve the above two
            problems, `0->1` and `0->1\\n0->2` will be printed. Likewise, the
            answers are split by hyphens.'''))
    parser.add_argument(
        'problems',
        metavar='FILE',
        help=('the path to the FILE containing problems to '
              'solve, or `-\' to read from stdin'))
    return parser


def main():
    args = make_parser().parse_args()
    try:
        if args.problems == '-':
            problems = load_states_from_file(sys.stdin)
        else:
            with open(args.problems) as infile:
                problems = load_states_from_file(infile)
        for state in problems:
            route = search_path(state)
            if not route:
                print('<no solution>')
            else:
                for step in route:
                    print('{}->{}'.format(*step))
            print('---')
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        sys.stderr.close()


if __name__ == '__main__':
    main()
