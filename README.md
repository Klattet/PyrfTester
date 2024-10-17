# Performance profiler and bytecode analyser for functions and callable objects in Python.

## Goal
Create a tool to:
- Display the underlying bytecode instructions of a Python object in an intuitive way.
- Profile the performance of a function or an algorithm with minimal extra code requirement.
- Automatically analyse the time complexity of an algorithm and calculate the Little-O constants based on run-time performance.

## Background
To gain a deeper understanding of how Python works, I wanted to learn how the language is translated into its intermediate bytecode representation. I wanted to understand what the Python interpreter actually reads and how it compares to the standard human-readable Python we all know and love.\
\
I then received an assignment in college for the Algorithms and Datastructures course, where I had to implement a few different sorting algorithms, and measure the Little-O constants knowing their time complexity (Little-O is the same as Big-O except constants are not ignored). I asked the professor if I could do the assignment in Python instead of Java, since I already had an ongoing project that could be helpful. He gave me free reins to do what I wanted as long as I completed the assignment requirements.\
\
The project is now much more ambitious than simply playing around with Python bytecode. There is still a lot of work to do, and I am still learning new things about the underlying mechanisms of Python.

## Dependencies
Only tested on Python version 3.12+ and I have no clue how it performs differently on older Python versions. Researching version compatibility is on the to-do list. Until the project is more mature, expect the program to break.
