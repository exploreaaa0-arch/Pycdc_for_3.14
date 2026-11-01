# Decompyle++ (pycdc) — Python 3.14

## Overview

Decompyle++ is a Python bytecode decompiler and disassembler written in C++. This revision builds on the existing pycdc source, adds support for selected Python 3.13 / 3.14 instructions, and fixes the reconstruction of generator expressions, function calls, and formatted strings.

It reads `.pyc` files and standalone marshalled code objects. Decompilation quality varies by Python version and language feature. Being able to read bytecode does not guarantee complete source recovery.

## Features

- `pycdc`: decompile Python bytecode into readable source.
- `pycdas`: inspect bytecode instructions and code objects.
- Correct handling of `RETURN_GENERATOR` and `YIELD_VALUE` instead of treating them as conditional branches.
- Reconstruction of generator expressions, nested generators, and filter conditions.
- Stack handling fixes for `CALL`, `CALL_KW`, and `PUSH_NULL`.
- Support for `FORMAT_SIMPLE`, `FORMAT_WITH_SPEC`, and `CONVERT_VALUE`.
- Fixes for selected `END_FOR` cleanup sequences, cache-relative jump offsets, and Python 3.14 docstring detection.

These changes operate on bytecode instructions and the AST. They do not special-case application function names or rewrite the generated source text.

## Source Layout

```text
pycdc/
├── .github/
├── bytes/
├── scripts/
├── tests/
│   ├── input/
│   ├── tokenized/
│   ├── compiled/
│   ├── xfail/
│   ├── run_tests.py
│   └── test_python314_roundtrip.py
├── ASTNode.cpp / ASTNode.h
├── ASTree.cpp / ASTree.h
├── bytecode.cpp / bytecode.h
├── bytecode_ops.inl
├── FastStack.h
├── pycdc.cpp
├── pycdas.cpp
├── pyc_*.cpp / pyc_*.h
├── CMakeLists.txt
├── LICENSE
├── README.md
└── README_EN.md
```

This directory contains source code, scripts, test inputs, and documentation only. It does not include executables, build directories, or compiled `.pyc` test fixtures. `tests/compiled` and `tests/xfail` are left empty; empty directories may not be retained when the source is committed to Git.

## Installation

### Dependencies

- A C++11 compiler: GCC, Clang, or MSVC.
- CMake 3.12 or later.
- Ninja, Make, or Visual Studio build tools.
- Python 3 for tests and helper scripts only. The built programs do not require a Python interpreter at runtime.

Ubuntu / Debian:

```bash
sudo apt update
sudo apt install build-essential cmake ninja-build python3
```

### Build

Run these commands from the source directory. Build files are written to its `build/` subdirectory.

Linux / macOS:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

Windows / PowerShell (Ninja + GCC):

```powershell
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

Windows / Visual Studio:

```powershell
cmake -S . -B build
cmake --build build --config Release --parallel
```

Some MinGW / Ninja versions cannot handle non-ASCII paths. If a build fails with a path error, copy the source to an ASCII-only path or build through a directory junction with an ASCII-only path.

## Usage

### Decompile a `.pyc` File

```powershell
& ./build/pycdc.exe input.pyc
& ./build/pycdc.exe -o output.py input.pyc
& ./build/pycdc.exe output.py > input.pyc
```

### Disassemble a `.pyc` File

```powershell
& ./build/pycdas.exe input.pyc
```

### Decompile Marshalled Code

```powershell
& ./build/pycdc.exe -c -v 3.14 input.marshalled
```

| Flag | Description |
| --- | --- |
| `-o <file>` | Write the decompiled source to a file. |
| `-c` | Read a standalone marshalled code object. |
| `-v <version>` | Specify the code object's Python version; use with `-c`. |
| `-h`, `--help` | Show help. |

On Linux / macOS, use `./build/pycdc` or `./build/pycdas` instead of the Windows executable paths. Visual Studio multi-configuration builds usually place executables in the `Release` subdirectory.

## Tests

Run the behavioral regression tests with the Python version you want to test. The script compiles temporary bytecode, decompiles it, executes controlled test functions, and compares return values, standard output, and exception types.

```powershell
py -3.14 tests\test_python314_roundtrip.py ./build/pycdc.exe
py -3.13 tests\test_python314_roundtrip.py ./build/pycdc.exe
```

The Windows examples use Python Launcher (`py`); you can also invoke the matching Python interpreter directly. All 17 existing test cases passed on Python 3.14.0 and 3.13.8 during verification. They cover generators, filter conditions, keyword calls, formatted strings, list comprehensions, and ordinary `for` loops.

The traditional test suite uses cross-version `.pyc` fixtures in `tests/compiled` and `tests/xfail`. These binary files are not included in this source-only directory. Restore them from the original test set before running the `check` target. Failures caused by missing fixtures are not evidence of a decompiler regression.

## Known Limitations

Python 3.14 support is incomplete. There are unresolved issues with `while` recognition, complex jumps, chained comparisons, and exception control flow. The Minesweeper sample's `print_board` function has been verified, but the full module still contains errors such as `while` loops reconstructed as `if` statements, missing loop headers, and `continue` statements outside loops. The full recovered module cannot be run as-is.

Async generators, `yield from`, function attributes and default arguments, class construction, and new Python 3.14 syntax are not comprehensively verified by these tests. An exit status of 0 does not guarantee syntactically or semantically correct output. Inspect and test the recovered source before using it.

## Reporting Issues

Include the exact Python version, a minimal source or bytecode sample, the full command and error output, and the expected and actual results.

Original project: [zrax/pycdc](https://github.com/zrax/pycdc). Reference fork: [zrsx/pycdc](https://github.com/zrsx/pycdc). When reporting issues involving local changes, include the current patch so the behavior can be reproduced.

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).

## Credits

Original authors: Michael Hansen and Darryl Pogue. Thanks to contributors to the original project and related forks. This directory is a source-organized Python 3.14 revision of the existing codebase; the original licensing and attribution remain unchanged.
