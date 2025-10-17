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

## Evaluation

Symboval includes built-in LLM evaluation using OpenRouter, which provides access to multiple LLM providers through a single API.

### Setup API Key

```python
import symboval

# Set your OpenRouter API key (only need to do this once)
symboval.set_api_key("sk-or-v1-your-key-here")

# Or set via environment variable
# export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

Get your API key at: https://openrouter.ai/keys

### Quick Evaluation

```python
import symboval

# Simple evaluation with default settings
results, summary = symboval.evaluate(
    num_problems=20,
    difficulty="medium",
    model="anthropic/claude-3.5-sonnet",
    save_to="results.json"
)

print(f"Accuracy: {summary.accuracy:.2%}")
print(f"Correct: {summary.correct}/{summary.total_problems}")
```

### `evaluate()`

Convenience function for running complete evaluations.

**Parameters:**
- `problems` (list): Optional list of existing problems (generates if None)
- `prompts` (list): Optional list of prompts (generates if None)
- `num_problems` (int): Number of problems to generate (default: 10)
- `principles` (list): Principles to test (default: all)
- `difficulty` (str): Problem difficulty (default: "medium")
- `num_examples` (int): Number of symbol mapping examples (default: 5)
- `model` (str): OpenRouter model identifier (default: "anthropic/claude-3.5-sonnet")
- `temperature` (float): Sampling temperature (default: 0.0)
- `api_key` (str): OpenRouter API key (default: uses saved key)
- `save_to` (str): Optional filename to save results JSON
- `verbose` (bool): Print progress information (default: True)
- `seed` (int): Random seed for reproducibility

**Returns:** Tuple of (results, summary)

### Advanced Evaluation

```python
import symboval

# Create evaluator instance
evaluator = symboval.LLMEvaluator()

# Generate problems and prompts
problems = symboval.generate_problems(num_problems=10, seed=42)
prompts = symboval.generate_prompts(problems=problems, num_examples=5)

# Run evaluation
results = evaluator.evaluate_problems(
    problems=problems,
    prompts=prompts,
    model="anthropic/claude-3.5-sonnet",
    temperature=0.0
)

# Generate summary statistics
summary = evaluator.summarize_results(results)

# Save results
evaluator.save_results(results, "output.json", summary)
```

### Available Models

Common OpenRouter model identifiers:
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `anthropic/claude-3-haiku` - Claude 3 Haiku (faster, cheaper)
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo
- `google/gemini-pro` - Gemini Pro
- `meta-llama/llama-3-70b-instruct` - Llama 3 70B

See full list at: https://openrouter.ai/models

### Evaluation Results

The `EvaluationSummary` object contains:
- `total_problems`: Total number of problems evaluated
- `correct`: Number of correct answers
- `accuracy`: Overall accuracy (0.0 to 1.0)
- `by_principle`: Accuracy breakdown by mathematical principle
- `by_difficulty`: Accuracy breakdown by difficulty level
- `total_tokens`: Total tokens used
- `total_cost_estimate`: Estimated API cost in USD
- `avg_latency`: Average response time in seconds

### Example: Model Comparison

```python
import symboval

# Generate problems once
problems = symboval.generate_problems(num_problems=20, seed=42)
prompts = symboval.generate_prompts(problems=problems)

# Test multiple models
models = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4-turbo",
    "google/gemini-pro"
]

for model in models:
    results, summary = symboval.evaluate(
        problems=problems,
        prompts=prompts,
        model=model
    )
    print(f"{model}: {summary.accuracy:.2%}")
```

### API Key Management

```python
import symboval

# Set API key
symboval.set_api_key("sk-or-v1-your-key")

# Get current API key
key = symboval.get_api_key()

# Remove API key
symboval.remove_api_key()
```

API keys are stored in `~/.symboval/config.json`

## Notes

- All functions support random seeding for reproducibility
- Novel notation uses Unicode mathematical symbols
- Problem difficulties map to different number ranges:
  - Easy: 1-20
  - Medium: 10-100
  - Hard: 50-500
- Available principles: basic_arithmetic, commutativity, associativity, distributivity, identity, multi_step
- Evaluation uses OpenRouter for unified access to multiple LLM providers
- No external dependencies required beyond Python standard library
