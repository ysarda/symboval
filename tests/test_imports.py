"""Quick test to verify all imports work correctly."""
import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("Testing imports...")

# Test generator imports
print("  ✓ Testing generator imports...", end=" ")
from symboval import (
    SymbolMapper,
    Problem,
    ProblemGenerator,
    ProblemDifficulty,
    MathematicalPrinciple,
    PromptBuilder,
    DatasetConverter,
    generate_problem,
    generate_problems,
    generate_prompt,
    generate_prompts
)
print("OK")

# Test evaluator imports
print("  ✓ Testing evaluator imports...", end=" ")
from symboval import (
    LLMEvaluator,
    EvaluationResult,
    EvaluationSummary,
    set_api_key,
    get_api_key,
    remove_api_key,
    evaluate
)
print("OK")

# Test basic functionality
print("\n  ✓ Testing problem generation...", end=" ")
problem = generate_problem(seed=42)
assert problem is not None
assert hasattr(problem, 'answer')
print("OK")

print("  ✓ Testing prompt generation...", end=" ")
prompt = generate_prompt(problem=problem, seed=42)
assert prompt is not None
assert len(prompt) > 0
print("OK")

print("  ✓ Testing API key management...", end=" ")
# Test key management (without actual key)
original_key = get_api_key()
set_api_key("test-key-123")
assert get_api_key() == "test-key-123"
remove_api_key()
assert get_api_key() is None
# Restore original if it existed
if original_key:
    set_api_key(original_key)
print("OK")

print("\n✓ All imports successful!")
print("\nPackage is ready to use. Try running:")
print("  python examples/example_package_usage.py")
print("  python examples/example_evaluation.py")
