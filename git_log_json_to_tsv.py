#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import codecs
from itertools import chain
import json


ENCODING = "utf-8"


def _safe_str(s):
    for a, b in (("\\", "\\\\"), ("\t", "\\t"), ("\n", "\\n"), ("\r", "\\r")):
        s = s.replace(a, b)

    return s


def _tsv_value(x):
    if x is None:
        return ""

    if isinstance(x, str):
        x = x.decode("utf-8")

    return _safe_str(unicode(x))


def main(argv=sys.argv):
    with open(argv[1], "rb") as fp:
        data = json.load(fp, encoding=ENCODING)

    stream = codecs.getwriter(ENCODING)(sys.stdout)

    for item in data:
        row = [item[x] for x in ("hash", "date", "author", "comment")]

        for stat_item in item["stat"]:
            stream.write("\t".join((_tsv_value(x) for x in chain(row, stat_item))))
            stream.write("\n")

    stream.flush()


if __name__ == "__main__":
    sys.exit(main())
