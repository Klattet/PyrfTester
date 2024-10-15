from random import randint
from time import perf_counter_ns
from typing import MutableSequence
from math import log2

def bubble_sort(array: MutableSequence) -> MutableSequence:
    length = len(array) - 1
    for i in range(length):
        for j in range(length):
            if array[j] > array[j + 1]:
                array[j:j + 2] = reversed(array[j:j + 2])
    return array

def insertion_sort(array: MutableSequence[int]) -> None:
    for i in range(1, len(array)):
        for j in range(i - 1, -1, -1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
            else:
                break

def merge_sort(array: MutableSequence[int]) -> None:

    if len(array) < 2:
        return

    center = len(array) // 2

    left = array[:center]
    right = array[center:]

    merge_sort(left)
    merge_sort(right)

    i = j = k = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            array[k] = left[i]
            i += 1
        else:
            array[k] = right[j]
            j += 1
        k += 1

    while i < len(left):
        array[k] = left[i]
        i += 1
        k += 1

    while j < len(right):
        array[k] = right[j]
        j += 1
        k += 1

def radix_sort(array: MutableSequence[int]) -> None:
    digit_arrays = {i: [] for i in range(10)}

    num_length = len(str(max(array)))

    for i in range(num_length):
        for j in range(len(array)):
            index = (array[j] // 10**i) % 10
            digit_arrays[index].append(array[j])

        j = 0
        for k in range(10):
            for l in digit_arrays[k]:
                array[j] = l
                j += 1
            digit_arrays[k].clear()

def quick_sort(array: MutableSequence[int]) -> None:

    def find_partition(array: MutableSequence[int], left: int, right: int):

        start = array[left]

        inner_left = left
        inner_right = right

        while inner_left < inner_right:

            while array[inner_left] <= start and inner_left < inner_right:
                inner_left += 1

            while array[inner_right] > start:
                inner_right -= 1

            if inner_left < inner_right:
                array[inner_left], array[inner_right] = array[inner_right], array[inner_left]

        array[left], array[inner_right] = array[inner_right], array[left]

        return inner_right

    def inner_sort(array: MutableSequence[int], left: int, right: int):
        if right - left > 0:

            partition = find_partition(array, left, right)

            inner_sort(array, left, partition - 1)
            inner_sort(array, partition + 1, right)

    inner_sort(array, 0, len(array) - 1)

algorithms = {
    "insertion": {"function": insertion_sort, "complexity": lambda w, n: n**2, "readable": "n²"},
    "quick": {"function": quick_sort, "complexity": lambda w, n: n * log2(n), "readable": "n * log n"},
    "merge": {"function": merge_sort, "complexity": lambda w, n: n * log2(n), "readable": "n * log n"},
    "radix": {"function": radix_sort, "complexity": lambda w, n: w * n, "readable": "w * n"}
}

if __name__ == "__main__":

    print("---------- Sorting algorithm testing ----------")

    # Get valid array length input
    length = input("Length of the array to sort: ")
    while not length.isdigit():
        length = input("Choose a positive integer length for the array: ")
    length = int(length)

    # Get valid algorithm name
    print("\nAlgorithms:\n-", end = "")
    print("\n-".join(algorithms.keys()))
    algorithm = input("Choose an algorithm to test: ").lower()
    while algorithm not in algorithms.keys():
        algorithm = input("Choose an algorithm from the list: ").lower()

    # Get valid option for viewing
    print("\nOptions:\n1 - Time algorithm\n2 - Estimate time complexity constant")
    option = input("Choose an option: ")
    while option not in ("1", "2"):
        option = input("Choose a number 1 or 2: ")

    # Create array of random numbers
    array_to_sort = [randint(0, 2 * length) for _ in range(length)]

    # Sort the array using the correct function and time the execution
    start = perf_counter_ns()
    algorithms[algorithm]["function"](array_to_sort)
    end = perf_counter_ns()

    timed = (end - start)

    # Display with the chosen option
    if option == "1":
        print(f"\n{algorithm} sort took {round(timed / 1_000_000, 4)}ms to finish with an array of length {length}.")
    elif option == "2":
        num_length = len(str(max(array_to_sort)))
        print(f"\nThe approximate time per operation for {algorithm} sort:")
        print(f"Time complexity: O(C * {algorithms[algorithm]['readable']})")
        print(f"C = {round((timed / algorithms[algorithm]['complexity'](num_length, length)) / 1000, 4)}μs")
