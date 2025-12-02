# MIT License
#
# Copyright (c) 2018 Antoine Busque
# Copyright (c) 2018-2020 Philippe Proulx
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import json
import operator
import random
import sys
import unicodedata
from importlib import resources
import qngng
import enum
import re


@enum.unique
class _Gender(enum.Enum):
    MALE = 1
    FEMALE = 2


class _PartialName:
    def __init__(self, name, gender=None):
        self._name = name
        self._gender = gender

    @property
    def name(self):
        return self._name

    @property
    def gender(self):
        return self._gender


class _FullName:
    def __init__(self, name, surname, gender, middle_name=None):
        self._name = name
        self._middle_name = middle_name
        self._surname = surname
        self._gender = gender

    @property
    def name(self):
        return self._name

    @property
    def middle_name(self):
        return self._middle_name

    @property
    def surname(self):
        return self._surname

    @property
    def gender(self):
        return self._gender

    @property
    def middle_initial(self):
        assert self._middle_name is not None
        return self._middle_name[0].upper()


class _App:
    def __init__(self, std_surname_count, std_with_middle_name, gender, cats):
        self._std_surname_count = std_surname_count
        self._std_with_middle_name = std_with_middle_name
        self._gender = gender
        self._create_objs(cats)

    def random_full_name(self):
        rand_cat = random.choice(list(self._cat_objs))

        if rand_cat == 'std':
            return self._random_std_full_name()
        else:
            return random.choice(self._cat_objs[rand_cat])

    def _random_std_full_name(self):
        rand_name_objs = random.sample(self._name_objs, 2 if self._std_with_middle_name else 1)
        rand_surname_objs = random.sample(self._surname_objs, self._std_surname_count)
        surname = '-'.join([obj.name for obj in rand_surname_objs])
        return _FullName(rand_name_objs[0].name, surname, rand_name_objs[0].gender,
                         rand_name_objs[1].name if self._std_with_middle_name else None)

    def _get_cat_objs(self, cat):
        assert cat != 'std'
        objs = []

        if self._gender is None or self._gender == _Gender.MALE:
            objs += self._cat_file_to_objs(cat + '-m',
                                           lambda n, s: _FullName(n, s, _Gender.MALE))

        if self._gender is None or self._gender == _Gender.FEMALE:
            objs += self._cat_file_to_objs(cat + '-f',
                                           lambda n, s: _FullName(n, s, _Gender.FEMALE))

        return objs

    def _create_all_cat_objs(self, cats):
        self._cat_objs = {}

        if 'std' in cats:
            self._cat_objs['std'] = []

        for cat in (cats - {'std'}):
            self._cat_objs[cat] = self._get_cat_objs(cat)

    def _create_std_objs(self):
        self._name_objs = []

        if self._gender is None or self._gender == _Gender.MALE:
            self._name_objs += self._cat_file_to_objs('std-names-m',
                                                      lambda n, s: _PartialName(n, _Gender.MALE))

        if self._gender is None or self._gender == _Gender.FEMALE:
            self._name_objs += self._cat_file_to_objs('std-names-f',
                                                      lambda n, s: _PartialName(n, _Gender.FEMALE))

        self._surname_objs = self._cat_file_to_objs('std-surnames',
                                                    lambda n, s: _PartialName(s))

    def _create_objs(self, cats):
        self._create_std_objs()
        self._create_all_cat_objs(cats)

    @staticmethod
    def _cat_file_to_objs(cat_filename, create_obj_func):
        resource_path = f'cats/{cat_filename}.json'

        try:
            ref = resources.files('qngng').joinpath(resource_path)
            content = ref.read_text()
        except (FileNotFoundError, TypeError):
            return []

        entries = json.loads(content)

        objs = []

        for entry in entries:
            name = entry.get('name')
            surname = entry.get('surname')
            objs.append(create_obj_func(name, surname))

        return objs


class _CliError(RuntimeError):
    pass


def _parse_args():
    parser = argparse.ArgumentParser(description=qngng.__description__)
    parser.add_argument('--gender', '-g', choices=['male', 'female'],
                        help='Print a male or female name')
    parser.add_argument('--male', '-m', action='store_true',
                        help='Shorthand for `--gender=male`')
    parser.add_argument('--female', '-f', action='store_true',
                        help='Shorthand for `--gender=female`')
    parser.add_argument('--snake-case', '-s', action='store_true',
                        help='Print name in `snake_case` format')
    parser.add_argument('--kebab-case', '-k', action='store_true',
                        help='Print name in `kebab-case` format')
    parser.add_argument('--camel-case', '-C', action='store_true',
                        help='Print name in `camelCase` format')
    parser.add_argument('--cap-camel-case', action='store_true',
                        help='Print name in `CapitalizedCamelCase` format')
    parser.add_argument('--cat', '-c', action='append',
                        help='Category name')
    parser.add_argument('--double-surname', '-d', action='store_true',
                        help='Create a double-barrelled surname (only available for the `std` category)')
    parser.add_argument('--middle-initial', '-I', action='store_true',
                        help='Generate a middle initial (only available for the `std` category)')
    parser.add_argument('--middle-name', '-M', action='store_true',
                        help='Generate a middle name (only available for the `std` category)')
    parser.add_argument('--wheel', '-w', action='store_true',
                        help='Spin a wheel to find a name (only use interactively)')
    parser.add_argument('--version', '-V', action='version', version=f'qngng {qngng.__version__}',
                        help='Show version and quit')
    args = parser.parse_args()

    if sum([0 if args.gender is None else 1, args.male, args.female]) > 1:
        raise _CliError('Cannot specify more than one option amongst `--gender`, `--male`, and `--female`.')

    if args.middle_name and args.middle_initial:
        raise _CliError('Cannot specify more than one option amongst `--middle-initial` and `--middle-name`.')

    if args.male:
        args.gender = 'male'

    if args.female:
        args.gender = 'female'

    if args.gender == 'male':
        args.gender = _Gender.MALE
    elif args.gender == 'female':
        args.gender = _Gender.FEMALE
    else:
        args.gender = random.choice([_Gender.MALE, _Gender.FEMALE])

    if sum([args.kebab_case, args.snake_case, args.camel_case, args.cap_camel_case]) > 1:
        raise _CliError('Cannot specify more than one option amongst `--snake-case`, `--kebab-case`, `--camel-case`, and `--cap-camel-case`.')

    args.fmt = _Format.DEFAULT

    if args.snake_case:
        args.fmt = _Format.SNAKE
    elif args.kebab_case:
        args.fmt = _Format.KEBAB
    elif args.camel_case:
        args.fmt = _Format.CAMEL
    elif args.cap_camel_case:
        args.fmt = _Format.CAP_CAMEL

    unique_cats = {
        'std',
        'uda-actors',
        'uda-hosts',
        'uda-singers',
        'lbl',
        'sn',
        'icip',
        'd31',
        'dug',
    }
    grouping_cats = {
        'all',
        'uda',
    }
    valid_cats = unique_cats | grouping_cats
    real_cats = []

    if args.cat is None:
        real_cats.append('std')
    else:
        for cat in args.cat:
            if cat not in valid_cats:
                raise _CliError('Unknown category `{}`.'.format(cat))

            if cat == 'all':
                real_cats += list(unique_cats)
            elif cat == 'uda':
                real_cats += ['uda-actors', 'uda-hosts', 'uda-singers']
            else:
                real_cats.append(cat)

    if args.double_surname and 'std' not in real_cats:
        raise _CliError('Cannot specify `--double-surname` without the `std` category.')

    if args.middle_name and 'std' not in real_cats:
        raise _CliError('Cannot specify `--middle-name` without the `std` category.')

    if args.middle_initial and 'std' not in real_cats:
        raise _CliError('Cannot specify `--middle-initial` without the `std` category.')

    args.cat = real_cats
    return args


def _strip_diacritics(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')


def _normalize_name(name, sep, lower=True):
    name = _strip_diacritics(name)

    if lower:
        name = name.lower()

    return re.sub(r'[^a-zA-Z0-9_]', sep, name)


@enum.unique
class _Format(enum.Enum):
    DEFAULT = 0
    SNAKE = 1
    KEBAB = 2
    CAMEL = 3
    CAP_CAMEL = 4


def _format_name(fullname, fmt=_Format.DEFAULT, with_middle_name_initial=True):
    parts = []

    if fullname.name:
        parts.append(fullname.name);

    if fullname.middle_name:
        middle_initial = fullname.middle_initial

        if fmt == _Format.DEFAULT:
            middle_initial += '.'

        parts.append(middle_initial if with_middle_name_initial else fullname.middle_name)

    if fullname.surname:
        parts.append(fullname.surname);

    raw_name = ' '.join(parts)

    if fmt == _Format.DEFAULT:
        return raw_name
    elif fmt == _Format.SNAKE:
        return _normalize_name(raw_name, '_')
    elif fmt == _Format.KEBAB:
        return _normalize_name(raw_name, '-')
    elif fmt == _Format.CAMEL or fmt == _Format.CAP_CAMEL:
        string = _normalize_name(raw_name, '', False)

        if fmt == _Format.CAMEL:
            string = string[0].lower() + string[1:]

    return string


def _spin_wheel(app, args):
    import time

    x = 0
    prev_name_len = 0

    while True:
        name = _format_name(app.random_full_name(), args.fmt, args.middle_initial)
        sys.stdout.write('\r')
        sys.stdout.write(' ' * prev_name_len)
        sys.stdout.write('\r')
        prev_name_len = len(name)
        sys.stdout.write(name)
        sys.stdout.flush()
        dur = x**10 + .05
        x += .02

        if x <= 1.05:
            time.sleep(dur)
        else:
            break

    print()


def _run(args):
    app = _App(2 if args.double_surname else 1, args.middle_name or args.middle_initial,
               args.gender, set(args.cat))

    if args.wheel:
        _spin_wheel(app, args)
    else:
        print(_format_name(app.random_full_name(), args.fmt, args.middle_initial))


def _main():
    try:
        _run(_parse_args())
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
