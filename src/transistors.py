"""
Transistors, the basic element for digital electronics.

In this module, we define how transistors behave at their lowest level, so everything else can be built on top of them.
This is the only place where abstract logic such as +, -, and, or, provided by the Python language, can be used (since
we need SOME way to simulate how a transistor behaves in the real world!).
"""
from abc import ABCMeta, abstractmethod
from typing import Union, List
from src.core import Wire, Component, Driver


class BaseTransistor(Component):
    """
    Base class for all transistors.

    Transistors are composed by the gate, source, and drain terminals.
    https://en.wikipedia.org/wiki/MOSFET
    """

    gate: Wire
    source: Wire
    drain: Wire
    _drain_driver: Driver

    def __init__(self) -> None:
        """
        Constructor.
        """
        self.gate = Wire()
        self.source = Wire()
        self.drain = Wire()
        self._drain_driver = Driver() # Not actually connected until elaboration

    @property
    def virtual(self):
        return False

    def elaborate(self):
        self._drain_driver = self.drain.connection()

    def subcomponents(self):
        return []

    def own_wires(self):
        yield self.gate
        yield self.source


class PChanTransistor(BaseTransistor):
    """
    Implementation of a P-Channel MOSFET
    """

    def prepare(self):
        if self.gate.value < self.source.value:
            self._drain_driver.connect(self.source)
        else:
            self._drain_driver.release()

class NChanTransistor(BaseTransistor):
    """
    Implementation of an N-Channel MOSFET
    """

    def prepare(self):
        if self.gate.value > self.source.value:
            self._drain_driver.connect(self.source)
        else:
            self._drain_driver.release()

