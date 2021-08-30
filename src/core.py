"""Base classes for components and wires"""

from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from typing import List, Optional, Union


class Driver:
    """This class represents a voltage source or sink that might be tristated.

    It drives some associated wire to some voltage level with some strength; higher strength drivers override weaker drivers.
    """
    
    value: bool = False
    strength: int = -1

    def drive(self, value: bool, strength: int = 1) -> Driver:
        """Drive the wire to the given level strongly"""
        self.value = value
        self.strength = strength
        return self

    def pull(self, value: bool) -> Driver:
        """Drive the wire to the given level weakly (e.g., through a resistor)"""
        return self.drive(value, 0)
        
    def release(self) -> Driver:
        """Drive the wire low very weakly; i.e., disconnect the wire"""
        return self.drive(False, -1)

    def connect(self, other: "Wire"):
        """Drive this wire from another wire"""
        self.value = other.value
        self.strength = other.strength
    

    
class Wire:
    value: bool
    strength: int
    drivers: List[Driver]

    def __init__(self, bias = False):
        self.value = self.bias = bias
        self.drivers = []
        
    def commit(self):
        strength = -1
        value = self.bias
        for driver in self.drivers:
            if driver.strength < strength:
                continue
            else if driver.strength > strength:
                value = driver.value
                strength = driver.strength
            else:
                if value != driver.value:
                    # Handle conflict somehow. 
                    pass
        self.value = value
        self.strength = strength

    @property
    def is_hiZ(self) -> bool:
        """Determine whether this wire is high-impedance (i.e., is not driven)"""
        return self.strength < 0

    def connection(self):
        driver = Driver()
        self.drivers.append(driver)
        return driver


class Rail(Wire):
    def commit(self):
        # Nothing can drive a rail hard enough to shift its level
        pass


Rail.GROUND = Rail(False)
Rail.VCC = Rail(True)


class Component(metaclass=ABCMeta):
    """Base class for all components.

    Each component has a set of Wire inputs, and a set of Driver outputs.
    """

    @property
    def virtual(self) -> bool:
        """Returns True if this class's prepare method does not contain any of
        its own logic. This is the case if it simply exists to
        organize lower-level components"""
        return True
    
    def prepare(self):
        """Compute new values for the outputs of this component and apply them
        to the associated drivers."""
        pass

    def elaborate(self):
        """Perform any necessary processing between setup and the beginning of simulation.

        E.g., create internal transisitors, connect drivers to wires, etc."""
        pass
    
    @abstractmethod
    def subcomponents(self) -> Iterator[Component]:
        """Produce a list of the individual components that this component is
        built from"""
        pass

    def subcomponents_recursive(self): Iterator[Component]:
        yield self
        for sub in self.subcomponents():
            yield from sub.subcomponents_recursive()

    @abstractmethod
    def own_wires(self) -> Iterable[Wire]:
        """Produce a list of wires that are directly used as inputs by this
        component."""
        pass
    
    def wires(self) -> Iterator[Wire]:
        for comp in self.subcomponents_recursive():
            yield from comp.own_wires()
        
    
