# MIT License
#
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

import re
import pytest
import qngng.qngng as q


class TestFormatNameDefault:
    _NAME_PART_RE = r'[a-zA-ZÀ-ÿ\' -]+'

    def test_simple(self):
        gen = q.NameGenerator()
        name = q.format_name(gen.random_full_name())
        assert re.fullmatch(rf'{self._NAME_PART_RE} {self._NAME_PART_RE}', name)

    def test_double_surname(self):
        gen = q.NameGenerator(surname_count=2)
        name = q.format_name(gen.random_full_name())
        assert re.fullmatch(rf'{self._NAME_PART_RE} {self._NAME_PART_RE}-{self._NAME_PART_RE}', name)

    def test_middle_initial(self):
        gen = q.NameGenerator(with_middle_name=True)
        name = q.format_name(gen.random_full_name(), with_middle_initial=True)
        assert re.fullmatch(rf'{self._NAME_PART_RE} [A-Z]\. {self._NAME_PART_RE}', name)

    def test_middle_name(self):
        gen = q.NameGenerator(with_middle_name=True)
        name = q.format_name(gen.random_full_name(), with_middle_initial=False)
        assert re.fullmatch(rf'{self._NAME_PART_RE} {self._NAME_PART_RE} {self._NAME_PART_RE}', name)

    def test_double_surname_and_middle_initial(self):
        gen = q.NameGenerator(surname_count=2, with_middle_name=True)
        name = q.format_name(gen.random_full_name(), with_middle_initial=True)
        assert re.fullmatch(rf'{self._NAME_PART_RE} [A-Z]\. {self._NAME_PART_RE}-{self._NAME_PART_RE}', name)


class TestFormatNameSnake:
    def test_simple(self):
        gen = q.NameGenerator()
        name = q.format_name(gen.random_full_name(), q.Format.SNAKE)
        assert re.fullmatch(r'[a-z0-9_]+', name)
        assert '_' in name

    def test_double_surname(self):
        gen = q.NameGenerator(surname_count=2)
        name = q.format_name(gen.random_full_name(), q.Format.SNAKE)
        assert re.fullmatch(r'[a-z0-9_]+', name)

    def test_middle_initial(self):
        gen = q.NameGenerator(with_middle_name=True)
        name = q.format_name(gen.random_full_name(), q.Format.SNAKE, with_middle_initial=True)
        assert re.fullmatch(r'[a-z0-9_]+', name)


class TestFormatNameKebab:
    def test_simple(self):
        gen = q.NameGenerator()
        name = q.format_name(gen.random_full_name(), q.Format.KEBAB)
        assert re.fullmatch(r'[a-z0-9\-]+', name)
        assert '-' in name

    def test_double_surname(self):
        gen = q.NameGenerator(surname_count=2)
        name = q.format_name(gen.random_full_name(), q.Format.KEBAB)
        assert re.fullmatch(r'[a-z0-9\-]+', name)

    def test_middle_initial(self):
        gen = q.NameGenerator(with_middle_name=True)
        name = q.format_name(gen.random_full_name(), q.Format.KEBAB, with_middle_initial=True)
        assert re.fullmatch(r'[a-z0-9\-]+', name)


class TestFormatNameCamel:
    def test_simple(self):
        gen = q.NameGenerator()
        name = q.format_name(gen.random_full_name(), q.Format.CAMEL)
        assert re.fullmatch(r'[a-z][a-zA-Z0-9]*', name)

    def test_double_surname(self):
        gen = q.NameGenerator(surname_count=2)
        name = q.format_name(gen.random_full_name(), q.Format.CAMEL)
        assert re.fullmatch(r'[a-z][a-zA-Z0-9]*', name)

    def test_middle_initial(self):
        gen = q.NameGenerator(with_middle_name=True)
        name = q.format_name(gen.random_full_name(), q.Format.CAMEL, with_middle_initial=True)
        assert re.fullmatch(r'[a-z][a-zA-Z0-9]*', name)


class TestFormatNameCapCamel:
    def test_simple(self):
        gen = q.NameGenerator()
        name = q.format_name(gen.random_full_name(), q.Format.CAP_CAMEL)
        assert re.fullmatch(r'[A-Z][a-zA-Z0-9]*', name)

    def test_double_surname(self):
        gen = q.NameGenerator(surname_count=2)
        name = q.format_name(gen.random_full_name(), q.Format.CAP_CAMEL)
        assert re.fullmatch(r'[A-Z][a-zA-Z0-9]*', name)

    def test_middle_initial(self):
        gen = q.NameGenerator(with_middle_name=True)
        name = q.format_name(gen.random_full_name(), q.Format.CAP_CAMEL, with_middle_initial=True)
        assert re.fullmatch(r'[A-Z][a-zA-Z0-9]*', name)


class TestGender:
    def test_male(self):
        gen = q.NameGenerator(gender=q.Gender.MALE)
        fullname = gen.random_full_name()
        assert fullname.gender == q.Gender.MALE

    def test_female(self):
        gen = q.NameGenerator(gender=q.Gender.FEMALE)
        fullname = gen.random_full_name()
        assert fullname.gender == q.Gender.FEMALE


class TestFullNameModel:
    def test_middle_initial_property(self):
        fullname = q.FullName(name='Jean', surname='Tremblay', gender=q.Gender.MALE,
                              middle_name='Pierre')
        assert fullname.middle_initial == 'P'

    def test_middle_initial_raises_without_middle_name(self):
        fullname = q.FullName(name='Jean', surname='Tremblay', gender=q.Gender.MALE)

        with pytest.raises(ValueError):
            _ = fullname.middle_initial
