#!/usr/bin/env python3
"""Vulcan entry point for the shared semantic art builder."""
from functools import partial
from build_current_art import *
_p=profile('vulcan')
IDS=_p['ids'];SELECT=_p['selection'];MAPPING=_p['mapping'];COMPAT=_p['compatibility']
selection=partial(selection,family='vulcan')
verify_authority=partial(verify_authority,family='vulcan')
derive=partial(derive,family='vulcan')
make_plan=partial(make_plan,family='vulcan')
stage=partial(stage,family='vulcan')
apply=partial(apply,family='vulcan')
check=partial(check,family='vulcan')
if __name__=='__main__':main('vulcan')
