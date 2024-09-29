from typing import Callable, Any
from types import FrameType
from time import perf_counter
from sys import settrace
from dis import get_instructions, Instruction, Bytecode
from inspect import getsourcelines
from functools import cached_property

class Algorithm(Callable):

    def __init__(self, function: Callable) -> None:
        self.function = function
        self.timings: list[dict] = []

        self.bytecode: Bytecode = Bytecode(function)
        self.instructions: list[Instruction] = list(get_instructions(function))

    def __call__(self, *args, **kwargs) -> Any:

        self.timings.append({"operations": []})

        start = perf_counter()
        settrace(self._trace_function)
        self.function(*args, **kwargs)
        settrace(None)
        end = perf_counter()

        self.timings[-1]["time"] = end - start

        return self.timings[-1]["operations"].pop()[2]

    def _trace_function(self, frame: FrameType, code: str, arg: Any) -> None:
        frame.f_trace_lines = True
        frame.f_trace_opcodes = True

        frame.f_trace = lambda f, c, a: self.timings[-1]["operations"].append((f.f_lasti, c, a))
        self.timings[-1]["operations"].append((frame.f_lasti, code, arg))

    @cached_property
    def source_lines(self) -> list[str]:
        lines = getsourcelines(self.function)[0]
        spaces = len(lines[0]) - len(lines[0].strip(" "))
        return [line[spaces:] for line in lines]

    @cached_property
    def source(self) -> str:
        return "".join(self.source_lines)

    def line_operations(self, run_index: int = 0) -> dict[int, list[int]]:
        line_operations = [operation for operation in self.timings[run_index]["operations"] if operation[1] == "line"]
        lines_dict = {ins.positions.lineno: [] for ins in self.instructions if ins.positions.lineno is not None}

        for operation in line_operations:
            for instruction in self.instructions:
                if operation[0] == instruction.offset and instruction.positions.lineno is not None:
                    lines_dict[instruction.positions.lineno].append(operation[0])
                    break

        return lines_dict

    def operations(self, run_index: int = 0) -> dict[int, list[int]]:
        operations = [operation for operation in self.timings[run_index]["operations"] if operation[1] == "opcode"]
        lines_dict = {ins.positions.lineno: [] for ins in self.instructions if ins.positions.lineno is not None}

        for operation in operations:
            for instruction in self.instructions:
                if operation[0] == instruction.offset and instruction.positions.lineno is not None:
                    lines_dict[instruction.positions.lineno].append(operation[0])
                    break

        return lines_dict

    def overview(self, run_index: int = 0) -> str:
        raw_lines, start = getsourcelines(self.function)
        line_operations = self.line_operations(run_index)



        line_num_padding = len("line")
        if (max_num_length := len(str(max(line_operations.keys())))) > line_num_padding:
            line_num_padding = max_num_length

        line_visit_padding = len("visitations")
        if (max_num_length := len(str(max(map(len, line_operations.values()))))) > line_visit_padding:
            line_visit_padding = max_num_length

        result = f"{max(map(len, self.source_lines)) * '-'}\n"
        result += "line | visitations | source\n"
        result += f"{max(map(len, self.source_lines)) * '-'}\n"

        for line_num, visitations in line_operations.items():
            for source_line in range(start, start + len(raw_lines)):
                if source_line == line_num:
                    result += f"{(line_num_padding - len(str(line_num))) * ' '}{line_num}"
                    result += f" | {(line_visit_padding - len(str(len(visitations)))) * ' '}{len(visitations)}"
                    result += f" | {self.source_lines[line_num - start]}"
                    break

        return result

def analyse(function: Callable) -> Algorithm:
    return Algorithm(function)