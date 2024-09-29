from typing import Callable, overload, Any, MutableSequence, Optional
from dataclasses import dataclass
from types import FrameType, FunctionType
from multiprocessing import Process, Manager, Value
from dis import get_instructions, Instruction, show_code, Bytecode, disassemble, disco
from sys import settrace, setprofile
from opcode import opmap
from time import perf_counter_ns
from ast import NodeVisitor, AST, parse
from inspect import getsourcelines
import profile

__all__ = "Algorithm", "analyse"

class Algorithm(Callable):
    """
    Represents a callable object that includes information about an algorithm, and returns the result of the function when called.
    """

    __slots__ = "function", "tracer", "time", "bytecode", "instructions", "ast"

    def __init__(self, function: FunctionType) -> None:
        self.function: FunctionType = function
        self.tracer: list[tuple[int, str, Any]] = []
        self.time: int = 0
        self.bytecode: Bytecode = Bytecode(function)
        self.instructions: list[Instruction] = list(get_instructions(function))
        self.ast: AST = parse(self.source, filename = function.__name__, mode = "exec")

    def __call__(self, *args, **kwargs) -> Any:

        # Trace the function call and time it.
        start = perf_counter_ns()
        settrace(self._trace_function)
        self.function(*args, **kwargs)
        settrace(None)
        end = perf_counter_ns()

        self.time = end - start

        return self.tracer.pop()[2]

    def _trace_function(self, frame: FrameType, code: str, arg: Any) -> None:

        frame.f_trace_lines = False
        frame.f_trace_opcodes = True
        frame.f_trace = lambda f, c, a: self.tracer.append((f.f_lasti, c, a))
        self.tracer.append((frame.f_lasti, code, arg))

    def _get_instruction(self, offset: int):
        ...

    @property
    def instruction_counts(self) -> dict[Instruction, int]:
        result = {instruction: 0 for instruction in self.instructions}
        for index, code, arg in self.tracer:
            for instruction, count in result.items():
                if instruction.offset == index:
                    result[instruction] += 1
                    break
        return result

    @property
    def per_line_instructions(self) -> dict[int, list[tuple[Instruction, int]]]:
        counts = self.instruction_counts
        indexes = [ins.positions.lineno for ins in counts.keys() if ins.positions.lineno is not None]
        result = {i: [] for i in range(min(indexes), max(indexes) + 1)}
        for instruction, count in counts.items():
            if instruction.positions.lineno is not None:
                result[instruction.positions.lineno].append((instruction, count))
        return result

    @property
    def source(self) -> str:
        lines, _ = getsourcelines(self.function)
        for index, line in enumerate(lines):
            if -1 < (beginning := line.find("def")):
                break

        return "".join(map(lambda l: l[beginning:], lines[index:]))

    @property
    def overview(self) -> str:
        lines, start = getsourcelines(self.function)

        for index, line in enumerate(lines):
            if -1 < (beginning := line.find("def")):
                break

        counts = {i: min([count for ins, count in lis]) if len(lis) != 0 else 0 for i, lis in self.per_line_instructions.items()}
        results = {}
        num_offset = 1
        exe_offset = 1

        for step, line in enumerate(lines[index:]):
            line_no = start + index + step
            instruction_no = counts[line_no]
            results[line_no] = (instruction_no, line[beginning:])

            exe_offset = e_off if exe_offset < (e_off := len(str(instruction_no))) else exe_offset
            num_offset = n_off if exe_offset < (n_off := len(str(line_no))) else num_offset

        result = ""
        for index, (num, string) in results.items():
            result += f"{num}{(exe_offset - len(str(num))) * ' '} | {index}{(num_offset - len(str(index))) * ' '} {string}"

        return result

def analyse(algorithm: Callable, multi_processing = False) -> Algorithm:
    if not multi_processing:
        return Algorithm(algorithm)

