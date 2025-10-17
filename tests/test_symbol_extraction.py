"""Test that all symbols in problems are included in prompt examples."""
import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / 'src'))

import symboval

# Generate a problem
prob = symboval.generate_problem(seed=42)
print("Problem Details:")
print(f"  Standard: {prob.standard_notation}")
print(f"  Novel:    {prob.novel_notation}")
print(f"  Answer:   {prob.answer}")

# Generate prompt
prompt = symboval.generate_prompt(problem=prob, num_examples=5, seed=42)

print("\n" + "=" * 70)
print("Generated Prompt:")
print("=" * 70)
print(prompt)

# Extract symbols from problem
print("\n" + "=" * 70)
print("Symbol Coverage Check:")
print("=" * 70)

# Get all unicode characters from the novel notation
problem_symbols = set()
for char in prob.novel_notation:
    if ord(char) > 127:  # Unicode character
        problem_symbols.add(char)

print(f"Symbols in problem: {problem_symbols}")

# Check if all symbols are in the prompt
missing_symbols = set()
for symbol in problem_symbols:
    if symbol not in prompt:
        missing_symbols.add(symbol)

if missing_symbols:
    print(f"\n✗ MISSING SYMBOLS: {missing_symbols}")
    print("These symbols appear in the problem but not in the prompt examples!")
else:
    print("\n✓ All symbols from the problem are included in the prompt examples!")
