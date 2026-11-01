# Decompyle++ (pycdc) — Python 3.14

## Overview

Decompyle++ 是使用 C++ 编写的 Python 字节码反编译器和反汇编器。本版本基于现有 pycdc 源码，补充 Python 3.13 / 3.14 的部分指令处理，并修复生成器表达式、函数调用和格式化字符串的还原问题。

可以读取 `.pyc` 文件和独立的 marshalled code object。不同 Python 版本和语法的还原程度并不相同，能读取字节码不代表能完整恢复源码。

## Features

- `pycdc`：将 Python 字节码反编译为可读源码。
- `pycdas`：查看字节码指令及代码对象。
- 修复 `RETURN_GENERATOR`、`YIELD_VALUE` 的分支处理。
- 还原生成器表达式、嵌套生成器及过滤条件。
- 修复 `CALL`、`CALL_KW`、`PUSH_NULL` 的栈处理。
- 补充 `FORMAT_SIMPLE`、`FORMAT_WITH_SPEC` 和 `CONVERT_VALUE`。
- 修复部分 `END_FOR` 清理、跳转缓存偏移及 3.14 文档字符串识别。

这些修复来自通用指令和 AST 处理，不依赖特定函数名或修改反编译结果文本。

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
└── README.markdown
```

这里只提供源码、脚本、测试输入和文档，不包含可执行文件、构建目录或 `.pyc` 测试夹具。`tests/compiled`、`tests/xfail` 保留为空目录。

## Installation

### Dependencies

- 支持 C++11 的编译器：GCC、Clang 或 MSVC。
- CMake 3.12 及以上。
- Ninja、Make 或 Visual Studio 构建工具。
- Python 3：仅测试和辅助脚本需要。程序运行不依赖 Python 解释器。

Ubuntu / Debian：

```bash
sudo apt update
sudo apt install build-essential cmake ninja-build python3
```

### Build

在源码根目录（含 `CMakeLists.txt`）执行以下命令。构建文件统一写入当前源码目录下的 `build/` 子目录。

Linux / macOS：

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

Windows / PowerShell（Ninja + GCC）：

```powershell
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

Windows / Visual Studio：

```powershell
cmake -S . -B build
cmake --build build --config Release --parallel
```

部分 MinGW / Ninja 版本无法处理中文路径。遇到路径错误时，可将源码复制到纯英文路径，或使用目录联接后再构建。

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

| 参数 | 说明 |
| --- | --- |
| `-o <文件>` | 将反编译结果写入指定文件 |
| `-c` | 输入为独立的 marshalled code object |
| `-v <版本>` | 指定 code object 的 Python 版本，与 `-c` 配合使用 |
| `-h`, `--help` | 查看帮助 |

Linux / macOS 将上述可执行文件路径换为 `./build/pycdc` 或 `./build/pycdas`。Visual Studio 多配置构建的程序通常位于 `Release` 子目录。

## Tests

使用对应版本的 Python 运行行为回归测试。脚本会生成临时字节码，反编译后执行受控测试函数，比较返回值、标准输出和异常类型。

```powershell
py -3.14 tests\test_python314_roundtrip.py ./build/pycdc.exe
py -3.13 tests\test_python314_roundtrip.py ./build/pycdc.exe
```

Windows 测试示例使用 Python Launcher（`py`）；也可使用对应版本的 Python 解释器。现有 17 项测试在 Python 3.14.0 和 3.13.8 下均通过，覆盖生成器、过滤条件、关键字调用、格式化字符串、列表推导式和普通 `for` 循环。

传统测试使用 `tests/compiled`、`tests/xfail` 中的跨版本 `.pyc` 夹具。此源码目录未附带这些二进制文件；需要从原始测试集补回后再运行 `check`，不能把缺少夹具导致的失败视为反编译器回归。

## Known Limitations

Python 3.14 支持仍不完整。`while` 的识别、复杂跳转、链式比较及异常控制流尚有未解决的问题。扫雷样本中的 `print_board` 已验证，但完整模块仍会出现将 `while` 还原为 `if`、丢失循环头及 `continue` 位于循环外等错误，不能直接运行。

异步生成器、`yield from`、函数属性与默认参数、类构建以及 Python 3.14 新语法不在本次完整验证范围内。程序退出码为 0 也不保证输出语法或语义正确，使用前应检查并测试结果。

## Reporting Issues

反馈时请提供 Python 的准确版本、最小源码或字节码样本、完整命令和错误输出，并说明预期结果与实际结果。原项目地址：[zrax/pycdc](https://github.com/zrax/pycdc)。参考分支：[zrsx/pycdc](https://github.com/zrsx/pycdc)。本地修改的问题需附上当前补丁，便于复现。

## License

GNU General Public License v3.0，详见 [LICENSE](LICENSE)。

## Credits

原作者：Michael Hansen、Darryl Pogue。感谢原项目及相关分支的贡献者。本目录是在现有源码上整理的 Python 3.14 修订版，不改变原项目的许可证和归属。
