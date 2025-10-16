# Symboval

A tool for evaluating LLM symbolic reasoning capabilities through novel mathematical notation.

## Research Question

> **When AI models encounter novel mathematical notation with minimal examples, do they rely primarily on symbol translation strategies or demonstrate genuine mathematical reasoning capabilities?**

Symboval tests whether language models can perform mathematical reasoning when familiar symbols are replaced with novel Unicode characters. By providing varying amounts of few-shot examples (0, 1, 3, 5, 10+), we can measure the boundary between pattern matching and true mathematical understanding.

## Installation

### Install from source (development mode)

```bash
git clone https://github.com/ysarda/symboval.git
cd symboval
pip install -e .
```

### Install via pip (when published)

```bash
pip install symboval
```

## Quick Start

```python
import symboval

# Generate a single problem
problem = symboval.generate_problem(
    principle="commutativity",
    difficulty="medium",
    use_novel_notation=True,
    seed=42
)
print(problem.standard_notation)
print(problem.novel_notation)
print(problem.answer)
```

## API Reference

### `generate_problem()`

Generate a single mathematical problem.

**Parameters:**
- `principle` (str or MathematicalPrinciple): The mathematical principle to test
  - Options: "basic_arithmetic", "commutativity", "associativity", "distributivity", "identity", "multi_step"
  - Default: "basic_arithmetic"
- `difficulty` (str or ProblemDifficulty): Problem difficulty level
  - Options: "easy", "medium", "hard"
  - Default: "medium"
- `use_novel_notation` (bool): Whether to use novel Unicode symbols
  - Default: True
- `seed` (int): Random seed for reproducibility
  - Default: None

**Returns:** Problem object with attributes: `question`, `answer`, `standard_notation`, `novel_notation`, `principle`, `difficulty`

### `generate_problems()`

Generate multiple mathematical problems.

**Parameters:**
- `num_problems` (int): Number of problems to generate
  - Default: 10
- `principles` (list): List of principles to use (if None, random selection)
  - Default: None
- `difficulty` (str): Problem difficulty level
  - Default: "medium"
- `balanced` (bool): Whether to balance problems across all principles
  - Default: False
- `use_novel_notation` (bool): Whether to use novel symbols
  - Default: True
- `seed` (int): Random seed for reproducibility
  - Default: None

**Returns:** List of Problem objects

### `generate_prompt()`

Generate a prompt for LLM evaluation.

**Parameters:**
- `problem` (Problem): Existing problem to use (if None, generates new one)
  - Default: None
- `principle` (str): Principle for new problem (if problem is None)
  - Default: None
- `difficulty` (str): Difficulty for new problem (if problem is None)
  - Default: "medium"
- `num_examples` (int): Number of symbol mapping examples to include
  - Default: 5
- `include_thinking` (bool): Whether to request chain-of-thought reasoning
  - Default: False
- `use_novel_notation` (bool): Whether to use novel symbols
  - Default: True
- `seed` (int): Random seed
  - Default: None

**Returns:** String containing the full prompt

### `generate_prompts()`

Generate multiple prompts for batch evaluation.

**Parameters:**
- `problems` (list): List of existing problems (if None, generates new ones)
  - Default: None
- `num_problems` (int): Number of problems to generate (if problems is None)
  - Default: 10
- `principles` (list): Principles to use for new problems
  - Default: None
- `difficulty` (str): Difficulty level
  - Default: "medium"
- `num_examples` (int): Number of mapping examples per prompt
  - Default: 5
- `include_thinking` (bool): Request chain-of-thought reasoning
  - Default: False
- `use_novel_notation` (bool): Use novel symbols
  - Default: True
- `seed` (int): Random seed
  - Default: None

**Returns:** List of prompt strings

## Examples

### Example 1: Generate problems of different difficulties

```python
import symboval

easy = symboval.generate_problem(difficulty="easy", seed=42)
medium = symboval.generate_problem(difficulty="medium", seed=42)
hard = symboval.generate_problem(difficulty="hard", seed=42)
```

### Example 2: Generate balanced problem set

```python
import symboval

problems = symboval.generate_problems(
    num_problems=12,
    balanced=True,
    use_novel_notation=True,
    seed=42
)

# This will generate 2 problems of each principle type
```

### Example 3: Generate prompts for specific principles

```python
import symboval

prompts = symboval.generate_prompts(
    num_problems=5,
    principles=["commutativity", "associativity"],
    difficulty="medium",
    num_examples=10,
    include_thinking=True,
    seed=42
)
```

### Example 4: Use standard notation only

```python
import symboval

problem = symboval.generate_problem(
    principle="distributivity",
    use_novel_notation=False,
    seed=42
)
# problem.standard_notation == problem.novel_notation
```

## Advanced Usage

### Accessing Problem Attributes

```python
problem = symboval.generate_problem(seed=42)

print(f"Question: {problem.question}")
print(f"Answer: {problem.answer}")
print(f"Principle: {problem.principle}")
print(f"Difficulty: {problem.difficulty}")
print(f"Standard: {problem.standard_notation}")
print(f"Novel: {problem.novel_notation}")
```

### Using the Low-Level API

```python
from symboval import SymbolMapper, ProblemGenerator, MathematicalPrinciple, ProblemDifficulty

# Create custom symbol mapper
mapper = SymbolMapper(seed=42)
mapper.create_complete_mapping(
    numbers=list(range(0, 20)),
    operators=['+', '-', '*'],
    relations=['=']
)

# Generate problems with custom mapper
generator = ProblemGenerator(seed=42)
problem = generator.generate_problem(
    MathematicalPrinciple.COMMUTATIVITY,
    ProblemDifficulty.HARD,
    mapper
)
```

## Notes

- All functions support random seeding for reproducibility
- Novel notation uses Unicode mathematical symbols
- Problem difficulties map to different number ranges:
  - Easy: 1-20
  - Medium: 10-100
  - Hard: 50-500
- Available principles: basic_arithmetic, commutativity, associativity, distributivity, identity, multi_step
