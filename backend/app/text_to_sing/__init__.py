"""Simple Text-to-Sing module package.

This package provides a minimal, pure-Python `TextToSing` class
that converts input lyrics into a very basic sung waveform (WAV)
as a proof-of-concept. It is intentionally self-contained and
does not modify existing application code.
"""

from .text_to_sing import TextToSing

__all__ = ["TextToSing"]
