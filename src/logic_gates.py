"""
Implementation of the several logic gates we can use to build the world.
"""
from abc import ABCMeta, abstractmethod
from src.core import Wire, Component
from src.transistors import NChanTransistor, PChanTransistor


class _BaseLogicGate(Component):
    """
    Base class for all Logic Gates.
    """

    inputs: List[Wire]
    output: Wire
    transistors: List[Component]
    internal_wires: List[Wire]
    
    def __init__(self) -> None:
        """
        Constructor.
        """
        self.inputs = []
        self.output = Wire()

    def components(self):
        return self.transistors

    def own_wires(self):
        yield from self.inputs
        yield from self.internal_wires

    def add_input(self, *inputs: List[Wire]):
        self.inputs.extend(inputs)

        
class Inverter(Component):
    """
    Implementation of an Inverter (NOT Gate).
    """

    input: Wire
    output: Wire

    def __init__(self) -> None:
        """
        Constructor.
        """
        self.ntran = NChanTransistor()
        self.ptran = PChanTransistor()

        self.input = Wire()
        self.output = Wire()

    def elaborate(self):
        self.ntran.source = Rail.GROUND
        self.ptran.source = Rail.VCC

        self.ntran.gate = self.ptran.gate = self.input
        self.ntran.drain = self.output.connection()
        self.ptran.gate = self.output.connection()
        
        self.ntran.elaborate()
        self.ptran.elaborate()
        
    def subcomponents(self):
        yield self.ntran
        yield self.ptran

    def own_wires(self):
        yield self.input

class NandGate(_BaseLogicGate):
    """
    Implementation of an AND Gate using 2 transistors in series.
    """

    def elaborate(self):
        nchain = None
        for input in self.inputs():
            ptran = PChanTransistor()
            ptran.source = Rail.VCC
            ptran.gate = input
            ptran.drain = self.output
            self.transistors.append(ptran)

            ntran = NChanTransistor()
            if nchain is not None:
                wire = nchain.drain = ntran.source = Wire()
                self.internal_wires.append(wire)
            else:
                ntran.source = Rail.GROUND
            ntran.gate = input
            nchain = ntran
            self.transistors.append(ntran)
        nchain.drain = output

        for tr in self.transistors:
            tr.elaborate()

    
class NORGate(_BaseLogicGate):
    """
    Implementation of an OR Gate using 2 transistors in parallel.
    """

        pchain = None
        for input in self.inputs():
            ntran = PChanTransistor()
            ntran.source = Rail.GROUND
            ntran.gate = input
            ntran.drain = self.output
            self.transistors.append(ntran)

            ptran = NChanTransistor()
            if pchain is not None:
                wire = pchain.drain = ptran.source = Wire()
                self.internal_wires.append(wire)
            else:
                ptran.source = Rail.VCC
            ptran.gate = input
            pchain = ptran
            self.transistors.append(ptran)
        pchain.drain = output

        for tr in self.transistors:
            tr.elaborate()


class AndGate(_BaseLogicGate):
    """
    Implementation of a AND Gate using an NAND Gate and an Inverter.
    """

    def __init__(self) -> None:
        """Constructor."""
        super().__init__()

        self.nand_gate = NANDGate()
        self.inverter = Inverter()

    def elaborate(self):
        self.inverter.output = self.output
        self.nand_gate.add_input(*self.inputs)
        self.inverter.input = self.nand_gate.output
        self.inverter.elaborate()
        self.nand_gate.elaborate()

    def subcomponents(self):
        yield self.inverter
        yield self.nand_gate

        
class OrGate(_BaseLogicGate):
    """
    Implementation of an Or Gate using an NOR Gate and an Inverter.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super().__init__()

        self.nor_gate = NORGate()
        self.inverter = Inverter()

    def elaborate(self):
        self.inverter.output = self.output
        self.nor_gate.add_input(*self.inputs)
        self.inverter.input = self.nor_gate.output
        self.inverter.elaborate()
        self.nor_gate.elaborate()

    def subcomponents(self):
        yield self.inverter
        yield self.nor_gate


class XORGate(_BaseLogicGate):
    """
    Implementation of a XOR Gate using an AND, OR, and NAND Gates.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super().__init__()

        self.and_gate = AndGate()
        self.or_gate = OrGate()
        self.nand_gate = NANDGate()

    def elaborate(self):
        assert len(self.inputs) == 2
        self.or_gate.add_input(*self.inputs)
        self.nand_gate.add_input(*self.inputs)
        self.and_gate.add_input(self.or_gate.output, self.nand_gate.output)

        self.or_gate.elaborate()
        self.nand_gate.elaborate()
        self.and_gate.elaborate()

    def subcomponents(self):
        yield self.or_gate
        yield self.nand_gate
        yield self.and_gate


class XNORGate(_BaseLogicGate):
    """
    Implementation of a XNOR Gate using a XOR Gate and an Inverter.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super().__init__()

        self.xor_gate = XORGate()
        self.inverter = Inverter()

    def elaborate(self):
        self.inverter.output = self.output
        self.xor_gate.add_input(*self.inputs)
        self.inverter.input = self.xor_gate.output
        self.inverter.elaborate()
        self.xor_gate.elaborate()

    def subcomponents(self):
        yield self.inverter
        yield self.xor_gate
