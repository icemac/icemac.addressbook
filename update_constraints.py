"""Adapted from https://github.com/zopefoundation/Zope/blob/4aadecc/util.py."""
import os

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser

HERE = os.path.abspath(os.path.dirname(__file__))


class CaseSensitiveParser(RawConfigParser):

    def optionxform(self, value):
        return value


def generate(in_, constraints_file):
    in_file = os.path.join(HERE, in_)
    out_file_constraints = os.path.join(HERE, constraints_file)
    parser = CaseSensitiveParser()
    parser.read(in_file)

    constraints = []
    versions = parser.items('versions')
    for name, pin in versions:
        if not pin:
            continue

        spec = '%s==%s' % (name, pin)
        constraints.append(spec + '\n')

    with open(out_file_constraints, 'w') as fcon:
        for con in sorted(constraints):
            fcon.write(con)


def main():
    generate('profiles/versions.cfg', 'constraints.txt')


if __name__ == '__main__':
    main()
