#!/usr/bin/env python3
import sys


def main():
    name = sys.argv[1]
    # Consumers parse this exact string, so the format is load-bearing (ADR-0002).
    print(f"Hello, {name}!")


if __name__ == "__main__":
    main()
