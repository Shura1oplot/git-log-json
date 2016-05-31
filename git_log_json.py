#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import json
import subprocess
from lxml import etree


GIT_LOG_FORMAT = ("]]></stat></commit><commit><hash>%H</hash><author>%an</author>"
                  "<date>%aI</date><comment><![CDATA[%B]]></comment><stat><![CDATA[")
SKEW_STR = "]]></stat></commit>"
ENCODING = "utf-8"


def parse_stat(data):
    def _safe_int(s):
        try:
            return int(s)
        except ValueError:
            return s

    def _parse_path(s):
        s = s.strip().strip('"')
        s = s.encode("ascii")
        s = s.decode("string_escape")
        s = s.decode("utf-8")
        return s

    stat = []

    for line in data.split("\n"):
        line = line.strip()

        if not line:
            continue

        added, deleted, path = line.split("\t", 2)
        stat.append((_parse_path(path),
                     _safe_int(added),
                     _safe_int(deleted)))

    return stat


def main(argv=sys.argv):
    args = ["git", "log", "--numstat", "--pretty=format:" + GIT_LOG_FORMAT]
    args.extend(argv[2:])

    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    so, se = p.communicate()

    if p.returncode != 0:
        print(se)
        return 1

    xml = "\n".join(('<?xml version="1.0" encoding="UTF-8"?>',
                     '<history>',
                     so.decode(ENCODING, errors="replace")[len(SKEW_STR):],
                     SKEW_STR,
                     '</history>')).encode(ENCODING)

    tree = etree.fromstring(xml)
    history = []

    for elem in tree.xpath("/history/commit"):
        item = {}

        for child in elem:
            if child.tag == "stat":
                item["stat"] = parse_stat(child.text)
            else:
                item[child.tag] = child.text.strip()

        history.append(item)

    content = json.dumps(history, encoding=ENCODING, ensure_ascii=False)
    sys.stdout.write(content.encode(ENCODING))


if __name__ == "__main__":
    sys.exit(main())
