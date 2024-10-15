from analyser import analyse, Analyser
from sorting_algorithms import insertion_sort

def foo(bar: int,
    baz: str) -> None:
    yep: str = "stinky"


    nop: int = 2

if __name__ == "__main__":

    analyser = Analyser(foo)

    print(analyser)
