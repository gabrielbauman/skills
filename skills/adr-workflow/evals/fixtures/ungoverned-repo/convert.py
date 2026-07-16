#!/usr/bin/env python3
"""Tiny temperature converter that predates any spec."""
import sys


def c_to_f(c):
    return c * 9 / 5 + 32


def f_to_c(f):
    return (f - 32) * 5 / 9


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("c2f", "f2c"):
        print("usage: convert.py c2f|f2c VALUE")
        return 2
    value = float(sys.argv[2])
    result = c_to_f(value) if sys.argv[1] == "c2f" else f_to_c(value)
    print(round(result, 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
