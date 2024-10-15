import inspect, dis, ast, re, textwrap
from dis import Instruction
from typing import Callable
from types import FunctionType, MethodType, CodeType

__all__ = "Analyser", "analyse"

class Analyser[**ARGS, RET](Callable):
    """
    Break
    """
    __slots__ = (
        "function",
        "bytecode",
        "lines",
        "ast",
        "reduced_code",
        "overview"
    )

    def __init__(self, code_object: MethodType | FunctionType | CodeType | type) -> None:

        self.function: FunctionType = code_object
        self.bytecode: dis.Bytecode = dis.Bytecode(code_object)
        self.lines: dict[int, dict[str, str | list[dis.Instruction]]] = {}
        self.ast: ast.Module = ast.parse(textwrap.dedent(inspect.getsource(code_object)), inspect.getabsfile(code_object), optimize = 0)
        self.reduced_code: str = re.sub("\n\n+", "\n", ast.unparse(self.ast))

        # Wonky workaround to map the original line numbers to the reduced ones.
        line_mapping: dict[int, int] = {}
        start_line_number = inspect.getsourcelines(code_object)[1]
        for i, j in zip(ast.walk(self.ast), ast.walk(ast.parse(self.reduced_code, inspect.getabsfile(code_object), optimize = 0))):
            if hasattr(i, "lineno") and hasattr(j, "lineno"):
                line_mapping[i.lineno + start_line_number - 1] = j.lineno + start_line_number - 1


        # Fill the lines dict with info.
        code_lines = self.reduced_code.splitlines()
        for instruction in self.bytecode:
            if instruction.line_number is None:
                continue
            if instruction.line_number not in self.lines.keys():
                self.lines[instruction.line_number] = {
                    "code": code_lines[line_mapping[instruction.line_number] - start_line_number],
                    "instructions": []
                }
            self.lines[instruction.line_number]["instructions"].append(instruction)

        # TODO: Fix a bug that causes the reduced code lines to be duplicated.
        # Happens when a single line of code is spread over multiple lines.
        # Example: The expression assigned to overview directly below.

        # Create an overview of the function.
        self.overview = "\n".join(
            f"{line_number:-{len(str(tuple(self.lines.keys())[-1]))}} | "
            f"{info["code"]:{max(len(val["code"]) for val in self.lines.values())}} | "
            f"{", ".join(ins.opname for ins in info["instructions"])}" for line_number, info in self.lines.items()
        )

    def __call__(self, *args: ARGS.args, **kwargs: ARGS.kwargs) -> RET:
        return self.function(*args, **kwargs)

    def __repr__(self) -> str:
        return self.overview

def analyse(algorithm: Callable) -> Analyser:
    return Analyser(algorithm)

