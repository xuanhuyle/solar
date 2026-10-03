"""Knowledge engine v0: a ledger, a forward vault, a referee and an AI researcher loop.

The engine sits on top of ``solarbench`` and never changes its behaviour. Every
byte of data it reads goes through ``engine.data``, which enforces the zones in
``engine.zones``; every result it produces is appended to the hash-chained
ledger in ``engine.ledger``.
"""
