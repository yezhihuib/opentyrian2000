#!/usr/bin/env python3
"""Independent extracted-production tests for random records260–262, base43.

See asteroid1_random_static_harness.py for the explicit input read allowlist and
bounded loader/source/record/quadrant/clipping/sticky-fallback checks.
"""
import sys
sys.dont_write_bytecode = True
from asteroid1_random_static_harness import main


if __name__ == '__main__':
    main(base=43, first=260, last=262)
