"""One module per research API: a `client(dry_run=False)` factory and the calls the tools make.

Tools reach a provider through its module (`searchapi.search(...)`, never `from ... import
search`) so tests can replace a call or a client by monkeypatching the module attribute.
"""
