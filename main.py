from typing import Iterable, Sized, Callable, Generic, TypeVar, Self, Sequence, MutableSequence, NamedTuple, Any
from time import perf_counter_ns
from sys import settrace
from types import FrameType
from random import randint

bytecodes = {
    "MISC": [
        "NOP",
        "CACHE",
        "MATCH_MAPPING",
        "MATCH_SEQUENCE",
        "MATCH_KEYS",
        "STORE_NAME",
        "DELETE_NAME",
        "UNPACK_SEQUENCE",
        "UNPACK_EX",
        "STORE_ATTR",
        "DELETE_ATTR",
        "STORE_GLOBAL",
        "DELETE_GLOBAL",
        "LOAD_CONST",
        "LOAD_NAME",
        "BUILD_TUPLE",
        "BUILD_LIST",
        "BUILD_SET",
        "BUILD_MAP",
        "BUILD_CONST_KEY_MAP",
        "BUILD_STRING",
        "LIST_TO_TUPLE",
        "LIST_EXTEND",
        "SET_UPDATE",
        "DICT_UPDATE",
        "DICT_MERGE",
        "LOAD_ATTR",
        "COMPARE_OP",
        "IS_OP",
        "CONTAINS_OP",
        "IMPORT_NAME",
        "IMPORT_FROM",
        "JUMP_FORWARD",
        "JUMP_BACKWARD",
        "JUMP_BACKWARD_NO_INTERRUPT",
        "POP_JUMP_FORWARD_IF_TRUE",
        "POP_JUMP_BACKWARD_IF_TRUE",
        "POP_JUMP_FORWARD_IF_FALSE",
        "POP_JUMP_BACKWARD_IF_FALSE",
        "POP_JUMP_FORWARD_IF_NOT_NONE",
        "POP_JUMP_BACKWARD_IF_NOT_NONE",
        "POP_JUMP_FORWARD_IF_NONE",
        "POP_JUMP_BACKWARD_IF_NONE",
        "JUMP_IF_TRUE_OR_POP",
        "JUMP_IF_FALSE_OR_POP",
        "FOR_ITER",
        "LOAD_GLOBAL",
        "LOAD_FAST",
        "STORE_FAST",
        "DELETE_FAST",
        "MAKE_CELL",
        "LOAD_CLOSURE",
        "LOAD_DEREF",
        "LOAD_CLASSDEREF",
        "STORE_DEREF",
        "DELETE_DEREF",
        "COPY_FREE_VARS",
        "RAISE_VARARGS",
        "CALL",
        "CALL_FUNCTION_EX",
        "LOAD_METHOD",
        "PRECALL",
        "PUSH_NULL",
        "KW_NAMES",
        "MAKE_FUNCTION",
        "BUILD_SLICE",
        "EXTENDED_ARG",
        "FORMAT_VALUE",
        "MATCH_CLASS",
        "RESUME",
        "RETURN_GENERATOR",
        "SEND",
        "ASYNC_GEN_WRAP"
    ],
    "STACK": [
        "POP_TOP",
        "COPY",
        "SWAP"
    ],
    "OPERATORS": {
        "UNARY": [
            "UNARY_POSITIVE",
            "UNARY_NEGATIVE",
            "UNARY_NOT",
            "UNARY_INVERT",
        ],
        "BINARY": [
            "BINARY_OP",

            "BINARY_SUBSCR",
            "STORE_SUBSCR",
            "DELETE_SUBSCR"
        ],
    },
    "CALLS": {
        "PROCEDURES": {
            "GETTERS": [
                "GET_ITER",
                "GET_YIELD_FROM_ITER",
                "PRINT_EXPR",
                "BEFORE_WITH",
                "GET_LEN",
            ],
            "RETURNS": [
                "RETURN_VALUE",
            ],
            "CONSTRUCTORS": [
                "SETUP_ANNOTATIONS",
                "LOAD_BUILD_CLASS",
            ]
        },
        "IMPORTS": [
            "IMPORT_STAR",
        ],
        "EXCEPTIONS": [
            "POP_EXCEPT",
            "RERAISE",
            "PUSH_EXC_INFO",
            "CHECK_EXC_MATCH",
            "CHECK_EG_MATCH",
            "PREP_RERAISE_STAR",
            "WITH_EXCEPT_START",
            "LOAD_ASSERTION_ERROR",
        ],
        "SEQUENCES": {
            "MUTATIONS": [
                "SET_ADD",
                "LIST_APPEND",
                "MAP_ADD",
            ]
        },
        "COROUTINES": {
            "GETTERS": [
                "GET_AWAITABLE",
                "GET_AITER",
                "GET_ANEXT",
                "BEFORE_ASYNC_WITH"
            ],
            "RETURNS": [
                "END_ASYNC_FOR",
                "YIELD_VALUE",
            ]
        }
    },
}

class Evaluator(object):
    def __init__(self) -> None:

        self.results = {}

        def tracer(call_frame: FrameType, *_):
            tag = False
            if call_frame.f_back and "evaluator_measure_id_number" in call_frame.f_back.f_locals:
                id_num = call_frame.f_back.f_locals["evaluator_function_id_number"]
                self.results[id_num]["calls"] += 1
                call_frame.f_trace_opcodes = True
                call_frame.f_trace_lines = False
                tag = True

            def inner(frame: FrameType, event: str, arg: Any):
                code = frame.f_lasti

                """if code in ("COMPARE_OP", "BINARY_OP"):
                    self.results[id_num]["comparisons"] += 1
                elif code in ("LOAD_FAST", "LOAD_ATTR", "LOAD_CONST", "LOAD_GLOBAL", "LOAD_METHOD", "BINARY_SUBSCR"):
                    self.results[id_num]["memory access"] += 1
                elif code in ("STORE_ATTR", "STORE_FAST", "STORE_SUBSCR"):
                    self.results[id_num]["memory mutations"] += 1
                elif code in ("CALLS", "PRECALL"):
                    self.results[id_num]["helper calls"] += 1
                else:
                    self.codes.add(code)
                    self.results[id_num]["other"] += 1"""

                return inner

            if tag:
                return inner

        settrace(tracer)

    """Add a new algorithm function to test."""

    def add_function(self, function: Callable):

        if id(function) not in self.results.keys():
            self.results[id(function)] = {
                "file": function.__code__.co_filename,
                "name": function.__name__,
                "line": function.__code__.co_firstlineno,
                "function": function,
                "calls": 0,
                "helper calls": 0,
                "comparisons": 0,
                "memory access": 0,
                "memory mutations": 0,
                "memory usage": [],
                "other": 0,
                "time": 0,
                "valid": False
            }

    """Decorate a function in order to measure details about an algorithm."""

    def measure(self, algorithm: Callable) -> Callable:

        self.add_function(algorithm)

        def inner(iterable: MutableSequence):

            # Needed to get the IDs from tracing.
            evaluator_function_id_number = id(algorithm)
            evaluator_measure_id_number = id(self.measure)

            start = perf_counter_ns()
            sorted_result = algorithm(iterable)
            end = perf_counter_ns()

            self.results[id(algorithm)]["time"] = end - start

            # Validation
            for i in range(len(iterable) - 1):
                if iterable[i] > iterable[i + 1]:
                    break
            else:
                self.results[id(algorithm)]["valid"] = True

            return sorted_result

        return inner

    """Get the results from the name or ID of the function."""

    def __getitem__(self, item: str | Callable) -> dict:
        if isinstance(item, Callable):
            item = item.__closure__[0].cell_contents.__name__

        if item in self.results:
            return self.results[item]

        for result in self.results.values():
            if result["name"] == item:
                return result

        else:
            raise KeyError(f"{item} could not be found in results.")

    def format(self, item: str | Callable) -> str:
        algorithm = self[item]

        if len(algorithm["memory usage"]) == 0:
            memory = 0
        else:
            memory = sum(values for memory in algorithm["memory usage"] for values in memory.values()) // len(algorithm["memory usage"])
        representation = f"""{algorithm["name"]}:
    File: {algorithm["file"]}
    Line: {algorithm["line"]}
    Performance:
        Calls: {algorithm["calls"]}
        Helper function calls: {algorithm["helper calls"]}
        Comparisons: {algorithm["comparisons"]}
        Memory accesses: {algorithm["memory access"]}
        Memory mutations: {algorithm["memory mutations"]}
        Memory usage: {memory} bytes
        Other operations: {algorithm["other"]}
        Time: {algorithm["time"] / 1_000_000} ms
    Validation: {"Passed" if algorithm["valid"] else "Failed"}"""
        return representation

if __name__ == "__main__":

    def bubble_sort(iterable: MutableSequence) -> MutableSequence:
        length = len(iterable) - 1
        for i in range(length):
            for j in range(length):
                if iterable[j] > iterable[j + 1]:
                    iterable[j:j + 2] = reversed(iterable[j:j + 2])
        return iterable

