"""
A very small stub of the historic ``pkg_resources`` module.

Only the functionality required by ``webrtcvad`` is provided:
- ``get_distribution(name)`` returns an object with a ``version`` attribute.
- ``parse_version`` simply returns the version string.
- ``Distribution`` class mimics the real API enough for the import.

This file is placed at the repository root, so Python will import it
before looking for a system‑wide package, fixing the import error
without affecting any other libraries.
"""

class _SimpleDist:
    def __init__(self, version: str = "0"):
        self.version = version

def get_distribution(name: str):
    """
    Return a dummy distribution object.
    ``webrtcvad`` only asks for ``.version`` – we return “0”.
    """
    return _SimpleDist()

def parse_version(version):
    """Return the version string unchanged – sufficient for our use‑case."""
    return version

# Optional: expose a placeholder ``Distribution`` name that some code may import.
Distribution = _SimpleDist
