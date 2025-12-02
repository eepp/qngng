# MIT License
#
# Copyright (c) 2018 Antoine Busque
# Copyright (c) 2018-2025 Philippe Proulx
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

import enum
import importlib.resources
import msgspec
import pydantic
import qngng
import random
import sys
import time
import typer
import typing
import unicodedata


@enum.unique
class Gender(enum.StrEnum):
    MALE = 'male'
    FEMALE = 'female'


@enum.unique
class Format(enum.StrEnum):
    DEFAULT = 'default'
    SNAKE = 'snake'
    KEBAB = 'kebab'
    CAMEL = 'camel'
    CAP_CAMEL = 'cap-camel'


@enum.unique
class Category(enum.StrEnum):
    STD = 'std'
    UDA_ACTORS = 'uda-actors'
    UDA_HOSTS = 'uda-hosts'
    UDA_SINGERS = 'uda-singers'
    UDA = 'uda'
    LBL = 'lbl'
    SN = 'sn'
    ICIP = 'icip'
    D31 = 'd31'
    DUG = 'dug'
    ALL = 'all'


_UNIQUE_CATS: frozenset[Category] = frozenset({
    Category.STD,
    Category.UDA_ACTORS,
    Category.UDA_HOSTS,
    Category.UDA_SINGERS,
    Category.LBL,
    Category.SN,
    Category.ICIP,
    Category.D31,
    Category.DUG,
})


class JsonEntry(msgspec.Struct, frozen=True):
    name: str | None = None
    surname: str | None = None


class PartialName(pydantic.BaseModel, frozen=True):
    name: str
    gender: Gender | None = None


class FullName(pydantic.BaseModel, frozen=True):
    name: str
    surname: str
    gender: Gender
    middle_name: str | None = None

    @property
    def middle_initial(self) -> str:
        if self.middle_name is None:
            raise ValueError('No middle name')

        return self.middle_name[0].upper()


class NameGenerator:
    def __init__(self, surname_count: typing.Literal[1, 2] = 1, with_middle_name: bool = False,
                 gender: Gender | None = None,
                 categories: frozenset[Category] = frozenset({Category.STD})) -> None:
        self._surname_count = surname_count
        self._with_middle_name = with_middle_name
        self._gender = gender
        self._cat_objs: dict[Category, list[FullName]] = {}
        self._name_objs: list[PartialName] = []
        self._surname_objs: list[PartialName] = []
        self._create_objs(categories)

    def random_full_name(self) -> FullName:
        rand_cat = random.choice(list(self._cat_objs.keys()))

        if rand_cat == Category.STD:
            return self._random_std_full_name()

        return random.choice(self._cat_objs[rand_cat])

    def _random_std_full_name(self) -> FullName:
        rand_name_objs = random.sample(self._name_objs, 2 if self._with_middle_name else 1)
        rand_surname_objs = random.sample(self._surname_objs, self._surname_count)
        surname = '-'.join(obj.name for obj in rand_surname_objs)
        first = rand_name_objs[0]

        return FullName(name=first.name, surname=surname, gender=first.gender or Gender.MALE,
                        middle_name=rand_name_objs[1].name if self._with_middle_name else None)

    def _load_json_entries(self, cat_filename: str) -> list[JsonEntry]:
        resource_path = f'cats/{cat_filename}.json'

        try:
            ref = importlib.resources.files('qngng').joinpath(resource_path)
            content = ref.read_bytes()
        except (FileNotFoundError, TypeError):
            return []

        return msgspec.json.decode(content, type=list[JsonEntry])

    def _get_cat_objs(self, cat: Category) -> list[FullName]:
        objs: list[FullName] = []

        if self._gender is None or self._gender == Gender.MALE:
            for entry in self._load_json_entries(f'{cat}-m'):
                if entry.name and entry.surname:
                    objs.append(FullName(name=entry.name, surname=entry.surname,
                                         gender=Gender.MALE))

        if self._gender is None or self._gender == Gender.FEMALE:
            for entry in self._load_json_entries(f'{cat}-f'):
                if entry.name and entry.surname:
                    objs.append(FullName(name=entry.name, surname=entry.surname,
                                gender=Gender.FEMALE))

        return objs

    def _create_std_objs(self) -> None:
        if self._gender is None or self._gender == Gender.MALE:
            for entry in self._load_json_entries('std-names-m'):
                if entry.name:
                    self._name_objs.append(PartialName(name=entry.name, gender=Gender.MALE))

        if self._gender is None or self._gender == Gender.FEMALE:
            for entry in self._load_json_entries('std-names-f'):
                if entry.name:
                    self._name_objs.append(PartialName(name=entry.name, gender=Gender.FEMALE))

        for entry in self._load_json_entries('std-surnames'):
            if entry.surname:
                self._surname_objs.append(PartialName(name=entry.surname))

    def _create_objs(self, categories: frozenset[Category]) -> None:
        self._create_std_objs()

        if Category.STD in categories:
            self._cat_objs[Category.STD] = []

        for cat in categories - {Category.STD}:
            self._cat_objs[cat] = self._get_cat_objs(cat)


def _strip_diacritics(s: str) -> str:
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')


def _normalize_name(name: str, sep: str, lower: bool = True) -> str:
    name = _strip_diacritics(name)

    if lower:
        name = name.lower()

    result: list[str] = []

    for char in name:
        if char.isalnum() or char == '_':
            result.append(char)
        else:
            result.append(sep)

    return ''.join(result)


def format_name(fullname: FullName, fmt: Format = Format.DEFAULT,
                with_middle_initial: bool = True) -> str:
    parts: list[str] = []

    if fullname.name:
        parts.append(fullname.name)

    if fullname.middle_name:
        if with_middle_initial:
            initial = fullname.middle_initial

            if fmt == Format.DEFAULT:
                initial += '.'

            parts.append(initial)
        else:
            parts.append(fullname.middle_name)

    if fullname.surname:
        parts.append(fullname.surname)

    raw_name = ' '.join(parts)

    match fmt:
        case Format.DEFAULT:
            return raw_name
        case Format.SNAKE:
            return _normalize_name(raw_name, '_')
        case Format.KEBAB:
            return _normalize_name(raw_name, '-')
        case Format.CAMEL:
            s = _normalize_name(raw_name, '', False)
            return s[0].lower() + s[1:] if s else s
        case Format.CAP_CAMEL:
            return _normalize_name(raw_name, '', False)


def _spin_wheel(generator: NameGenerator, fmt: Format, middle_initial: bool) -> None:
    x = 0.0
    prev_name_len = 0

    while True:
        name = format_name(generator.random_full_name(), fmt, middle_initial)
        sys.stdout.write('\r')
        sys.stdout.write(' ' * prev_name_len)
        sys.stdout.write('\r')
        prev_name_len = len(name)
        sys.stdout.write(name)
        sys.stdout.flush()
        dur = x**10 + 0.05
        x += 0.02

        if x <= 1.05:
            time.sleep(dur)
        else:
            break

    print()


_app = typer.Typer(
    name='qngng',
    help=qngng.__description__,
    add_completion=True,
    pretty_exceptions_enable=False,
)


def _expand_categories(cats: list[Category] | None) -> frozenset[Category]:
    if not cats:
        return frozenset({Category.STD})

    result: set[Category] = set()

    for cat in cats:
        match cat:
            case Category.ALL:
                result |= set(_UNIQUE_CATS)
            case Category.UDA:
                result |= {Category.UDA_ACTORS, Category.UDA_HOSTS, Category.UDA_SINGERS}
            case _:
                result.add(cat)

    return frozenset(result)


def _version_callback(value: bool) -> None:
    if value:
        print(f'qngng {qngng.__version__}')
        raise typer.Exit()


@_app.command()
def _main(  # pyright: ignore[reportUnusedFunction]
    gender: typing.Annotated[
        Gender | None, typer.Option('--gender', '-g', help='Generate a male or female name'),
    ] = None,
    male: typing.Annotated[
        bool, typer.Option('--male', '-m', help='Shorthand for `--gender=male`'),
    ] = False,
    female: typing.Annotated[
        bool, typer.Option('--female', '-f', help='Shorthand for `--gender=female`'),
    ] = False,
    fmt: typing.Annotated[
        Format, typer.Option('--format', '-F', help='Output format'),
    ] = Format.DEFAULT,
    cat: typing.Annotated[
        list[Category] | None, typer.Option('--cat', '-c', help='Category name (can be repeated)'),
    ] = None,
    double_surname: typing.Annotated[
        bool, typer.Option('--double-surname', '-d',
                           help='Create a double-barrelled surname (only for the `std` category)'),
    ] = False,
    middle_initial: typing.Annotated[
        bool, typer.Option('--middle-initial', '-I',
                           help='Generate a middle initial (only for `std` category)'),
    ] = False,
    middle_name: typing.Annotated[
        bool, typer.Option('--middle-name', '-M',
                           help='Generate a middle name (only for `std` category)'),
    ] = False,
    wheel: typing.Annotated[
        bool, typer.Option('--wheel', '-w',
                           help='Spin a wheel to find a name (interactive use only)'),
    ] = False,
    version: typing.Annotated[
        bool, typer.Option('--version', '-V', callback=_version_callback, is_eager=True,
                           help='Show version and exit'),
    ] = False,
) -> None:
    gender_opts = sum([gender is not None, male, female])

    if gender_opts > 1:
        raise typer.BadParameter('Cannot specify more than one option amongst `--gender`, `--male`, and `--female`.')

    if middle_name and middle_initial:
        raise typer.BadParameter('Cannot specify both `--middle-initial` and `--middle-name`.')

    resolved_gender: Gender | None = gender

    if male:
        resolved_gender = Gender.MALE
    elif female:
        resolved_gender = Gender.FEMALE
    elif resolved_gender is None:
        resolved_gender = random.choice([Gender.MALE, Gender.FEMALE])

    categories = _expand_categories(cat)

    if double_surname and Category.STD not in categories:
        raise typer.BadParameter('Cannot specify `--double-surname` without the `std` category.')

    if middle_name and Category.STD not in categories:
        raise typer.BadParameter('Cannot specify `--middle-name` without the `std` category.')

    if middle_initial and Category.STD not in categories:
        raise typer.BadParameter('Cannot specify `--middle-initial` without the `std` category.')

    generator = NameGenerator(2 if double_surname else 1, middle_name or middle_initial,
                              resolved_gender, categories)

    if wheel:
        _spin_wheel(generator, fmt, middle_initial)
    else:
        print(format_name(generator.random_full_name(), fmt, with_middle_initial=middle_initial))
