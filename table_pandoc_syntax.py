# table_pandoc_syntax.py - Pandoc table syntax

# Copyright (C) 2012  Free Software Foundation, Inc.

# Author: Valery Kocubinsky
# Package: SublimeTableEditor
# Homepage: https://github.com/vkocubinsky/SublimeTableEditor

# This file is part of SublimeTableEditor.

# SublimeTableEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# SublimeTableEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with SublimeTableEditor.  If not, see <http://www.gnu.org/licenses/>.



from __future__ import print_function
from __future__ import division


try:
    from . import table_base as tbase
    from . import table_border_syntax as tborder
except ValueError:
    import table_base as tbase
    import table_border_syntax as tborder


def create_syntax(table_configuration=None):
    return PandocTableSyntax(table_configuration)


class PandocTableSyntax(tbase.TableSyntax):

    def __init__(self, table_configuration):
        tbase.TableSyntax.__init__(self, "Pandoc", table_configuration)

        self.table_parser = PandocTableParser(self)
        self.table_driver = tborder.BorderTableDriver(self)

        self.hline_out_border = '+'
        self.hline_in_border = '+'


class PandocAlignRow(tborder.SeparatorRow):
    """Separator row with alignment colons, e.g. '+:===+===:+:==:+'."""

    def new_empty_column(self):
        return PandocAlignColumn(self, self.separator)

    def create_column(self, text):
        return PandocAlignColumn(self, text)

    def is_align(self):
        return True


class PandocAlignColumn(tbase.Column):

    def __init__(self, row, text):
        tbase.Column.__init__(self, row)
        text = text.strip()
        left, right = text.startswith(':'), text.endswith(':')
        if left and right:
            self._align_follow = tbase.Column.ALIGN_CENTER
        elif left:
            self._align_follow = tbase.Column.ALIGN_LEFT
        elif right:
            self._align_follow = tbase.Column.ALIGN_RIGHT
        else:
            self._align_follow = None

    def min_len(self):
        # ':=:' or ':==' or '==:' or '==='
        return 3

    def render(self):
        sep = self.row.separator
        align = self._align_follow
        lead = ':' if align in (tbase.Column.ALIGN_LEFT, tbase.Column.ALIGN_CENTER) else sep
        tail = ':' if align in (tbase.Column.ALIGN_RIGHT, tbase.Column.ALIGN_CENTER) else sep
        return lead + sep * (self.col_len - 2) + tail

    def align_follow(self):
        return self._align_follow


class PandocTableParser(tborder.BorderTableParser):

    def create_row(self, table, line):
        # Pandoc reads alignment only from the header separator (first '='
        # row) or, without a header, from the top border; ignore other colons
        str_cols = line.str_cols()
        if any(':' in col for col in str_cols):
            for sep in '-=':
                if self.columns_match_regex(str_cols, r"^\s*:?" + sep + r"+:?\s*$"):
                    if self.is_align_position(table, sep):
                        return PandocAlignRow(table, sep)
                    return tborder.SeparatorRow(table, sep)
        return tborder.BorderTableParser.create_row(self, table, line)

    def is_align_position(self, table, sep):
        if not table.rows:
            return True
        return sep == '=' and not any(
            isinstance(r, tborder.SeparatorRow) and r.separator == '='
            for r in table.rows)
