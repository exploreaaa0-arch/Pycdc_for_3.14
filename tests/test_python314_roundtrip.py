"""Behavioral regression tests for 3.13/3.14 CALL, generators and formatting.
Run with the Python version being tested and a matching pycdc executable.
Only executes fixtures defined in this file, never arbitrary input .pyc files.
"""
import argparse
import contextlib
import io
import json
import marshal
from pathlib import Path
import subprocess
import sys
import tempfile
import types

CASES = [
 ('print_board', '''def print_board(visible_board):
    print('\\n    ', end='')
    print(' '.join(str(i + 1) for i in range(len(visible_board[0]))))
    for r in range(len(visible_board)):
        print(f'{r + 1}  ', ' '.join(f'{c}' for c in visible_board[r]))
    print()
''', 'print_board', ([['#','#'],['1','*']],)),
 ('board_numeric', '''def f(board):
    return ' '.join(f'{c}' for c in board)
''', 'f', ([1, 0, -1, 3.5],)),
 ('empty_generator', "def f(xs):\n return '|'.join(str(x) for x in xs)\n", 'f', ([],)),
 ('filtered_generator', "def f(xs):\n return '|'.join(str(x) for x in xs if x % 2)\n", 'f', ([0,1,2,3,4,5],)),
 ('negative_filter', "def f(xs):\n return '|'.join(str(x) for x in xs if not x % 2)\n", 'f', ([0,1,2,3,4,5],)),
 ('double_filter', "def f(xs):\n return '|'.join(str(x) for x in xs if x > 0 if x % 2)\n", 'f', ([-3,-2,0,1,2,3],)),
 ('nested_generator', "def f(xs):\n return '|'.join(str(y) for x in xs for y in x)\n", 'f', ([[1,2],[],[3]],)),
 ('keyword_call', "def f(xs):\n print('a',end='!');print('b',end='?');print('c')\n return len(xs)\n", 'f', ([1,2],)),
 ('nested_method', "def f(xs):\n return ','.join(str(x).strip().upper() for x in xs)\n", 'f', ([' a ','b'],)),
 ('format_simple', "def f(x):\n return f'{x}'\n", 'f', (12.5,)),
 ('format_spec', "def f(x):\n return f'{x:08.2f}'\n", 'f', (12.5,)),
 ('format_repr', "def f(x):\n return f'{x!r}'\n", 'f', ('abc',)),
 ('format_ascii_spec', "def f(x):\n return f'{x!a:>12}'\n", 'f', ('\u96ea',)),
 ('inline_listcomp', "def f(xs):\n return [x + 1 for x in xs]\n", 'f', ([1,2,3],)),
 ('nested_listcomp', "def f(xs):\n return [[y + 1 for y in x] for x in xs]\n", 'f', ([[1,2],[3]],)),
 ('loops', "def f(xs):\n out = []\n for x in xs:\n  out.append(x + 1)\n return out\n", 'f', ([1,2,3],)),
 ('generator_function', "def f(xs):\n for x in xs:\n  yield x + 1\n", 'f', ([1,2,3],)),
]

def observe(fn, args):
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            result = fn(*args)
            if isinstance(result, types.GeneratorType):
                result = list(result)
        return {'stdout': out.getvalue(), 'result': repr(result), 'exception': None}
    except Exception as exc:
        return {'stdout': out.getvalue(), 'result': None, 'exception': type(exc).__name__}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pycdc')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    events = []
    with tempfile.TemporaryDirectory(prefix='pycdc-roundtrip-') as tmp:
        for label, source, name, inputs in CASES:
            ns = {}; exec(compile(source, '<fixture>', 'exec'), ns)
            code = ns[name].__code__
            raw = Path(tmp) / (label + '.marshal')
            raw.write_bytes(marshal.dumps(code))
            command = [args.pycdc, '-c', '-v', f'{sys.version_info.major}.{sys.version_info.minor}', str(raw)]
            proc = subprocess.run(command, capture_output=True)
            stdout = proc.stdout.decode('utf-8', 'replace')
            stderr = proc.stderr.decode('utf-8', 'replace')
            expected = observe(ns[name], inputs)
            params = ', '.join(code.co_varnames[:code.co_argcount])
            body = '\n'.join('    ' + line for line in stdout.splitlines() if not line.startswith('#'))
            generated = f'def {name}({params}):\n{body}\n'
            try:
                actual_ns = {}; exec(compile(generated, '<decompiled>', 'exec'), actual_ns)
                actual = observe(actual_ns[name], inputs)
                ok = proc.returncode == 0 and not stderr and expected == actual
                error = None
            except Exception as exc:
                ok = False; actual = None; error = repr(exc)
            event = dict(case=label, command=command, exit=proc.returncode,
                         stdout=stdout, stderr=stderr, input=repr(inputs),
                         expected=expected, actual=actual, error=error, passed=ok)
            events.append(event)
            print(('PASS' if ok else 'FAIL') + ' ' + label)
            if not ok: print(json.dumps(event, ensure_ascii=True))
    print(f'{sum(e["passed"] for e in events)}/{len(events)} passed on Python {sys.version.split()[0]}')
    if args.report:
        args.report.write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding='utf-8')
    return int(not all(e['passed'] for e in events))

if __name__ == '__main__':
    raise SystemExit(main())
