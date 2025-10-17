from .generator.symbol_mapper import SymbolMapper
from .generator.problem_templates import (
    Problem,
    ProblemGenerator,
    ProblemDifficulty,
    MathematicalPrinciple
)
from .generator.prompt_builder import PromptBuilder
from .generator.dataset_converter import DatasetConverter
from .evaluator import (
    LLMEvaluator,
    EvaluationResult,
    EvaluationSummary,
    set_api_key,
    get_api_key,
    remove_api_key
)

__version__ = "0.1.0"
__all__ = [
    "SymbolMapper",
    "Problem",
    "ProblemGenerator",
    "ProblemDifficulty",
    "MathematicalPrinciple",
    "PromptBuilder",
    "DatasetConverter",
    "generate_problem",
    "generate_problems",
    "generate_prompt",
    "generate_prompts",
    "LLMEvaluator",
    "EvaluationResult",
    "EvaluationSummary",
    "set_api_key",
    "get_api_key",
    "remove_api_key",
    "evaluate"
]


def generate_problem(principle=None, difficulty="medium", use_novel_notation=True, seed=None):
    if isinstance(difficulty, str):
        difficulty = ProblemDifficulty[difficulty.upper()]

    if principle is None:
        principle = MathematicalPrinciple.BASIC_ARITHMETIC
    elif isinstance(principle, str):
        principle = MathematicalPrinciple[principle.upper()]

    mapper = SymbolMapper(seed=seed)
    mapper.create_complete_mapping(
        numbers=list(range(0, 20)),
        operators=['+', '-', '*', '/'],
        relations=['=', '<', '>', '?']
    )

    generator = ProblemGenerator(seed=seed)
    problem = generator.generate_problem(principle, difficulty, mapper if use_novel_notation else None)

    return problem


def generate_problems(num_problems=10, principles=None, difficulty="medium", balanced=False,
                     use_novel_notation=True, seed=None):
    if isinstance(difficulty, str):
        difficulty = ProblemDifficulty[difficulty.upper()]

    if principles is not None:
        if isinstance(principles, str):
            principles = [MathematicalPrinciple[principles.upper()]]
        else:
            principles = [MathematicalPrinciple[p.upper()] if isinstance(p, str) else p for p in principles]

    mapper = SymbolMapper(seed=seed)
    mapper.create_complete_mapping(
        numbers=list(range(0, 20)),
        operators=['+', '-', '*', '/'],
        relations=['=', '<', '>', '?']
    )

    generator = ProblemGenerator(seed=seed)

    if balanced:
        problems_per_principle = num_problems // len(MathematicalPrinciple.__members__)
        problems = generator.generate_balanced_set(
            problems_per_principle,
            difficulty,
            mapper if use_novel_notation else None
        )
    else:
        problems = generator.generate_problem_set(
            num_problems,
            principles,
            difficulty,
            mapper if use_novel_notation else None
        )

    return problems


def generate_prompt(problem=None, principle=None, difficulty="medium", num_examples=5,
                   include_thinking=False, use_novel_notation=True, seed=None):
    if problem is None:
        problem = generate_problem(principle, difficulty, use_novel_notation, seed)

    if not hasattr(problem, 'novel_notation'):
        return None

    mapper = SymbolMapper(seed=seed)
    mapper.create_complete_mapping(
        numbers=list(range(0, 20)),
        operators=['+', '-', '*', '/'],
        relations=['=', '<', '>', '?']
    )

    builder = PromptBuilder(mapper)

    # Extract symbols from the problem
    notation = problem.novel_notation if use_novel_notation else problem.standard_notation
    required_symbols = builder._extract_symbols_from_expression(notation)

    prompt = builder.build_system_prompt() + "\n\n"
    prompt += builder.build_example_section(num_examples, required_symbols=required_symbols) + "\n"
    prompt += builder.build_problem_prompt(problem, use_novel_notation, include_thinking)

    return prompt


def generate_prompts(problems=None, num_problems=10, principles=None, difficulty="medium",
                    num_examples=5, include_thinking=False, use_novel_notation=True, seed=None):
    if problems is None:
        problems = generate_problems(num_problems, principles, difficulty, False, use_novel_notation, seed)

    mapper = SymbolMapper(seed=seed)
    mapper.create_complete_mapping(
        numbers=list(range(0, 20)),
        operators=['+', '-', '*', '/'],
        relations=['=', '<', '>', '?']
    )

    builder = PromptBuilder(mapper)
    prompts = []

    for problem in problems:
        # Extract symbols from this specific problem
        notation = problem.novel_notation if use_novel_notation else problem.standard_notation
        required_symbols = builder._extract_symbols_from_expression(notation)

        prompt = builder.build_system_prompt() + "\n\n"
        prompt += builder.build_example_section(num_examples, required_symbols=required_symbols) + "\n"
        prompt += builder.build_problem_prompt(problem, use_novel_notation, include_thinking)
        prompts.append(prompt)

    return prompts


def evaluate(
    problems=None,
    prompts=None,
    num_problems=10,
    principles=None,
    difficulty="medium",
    num_examples=5,
    model="anthropic/claude-3.5-sonnet",
    temperature=0.0,
    api_key=None,
    save_to=None,
    verbose=True,
    seed=None
):
    """Evaluate LLM performance on symbolic reasoning problems.

    This is a convenience function that generates problems and prompts,
    runs the evaluation, and returns results with summary statistics.

    Args:
        problems: Optional list of existing problems (if None, generates new ones)
        prompts: Optional list of prompts (if None, generates from problems)
        num_problems: Number of problems to generate (if problems is None)
        principles: Principles to test (if None, uses all principles)
        difficulty: Problem difficulty level ("easy", "medium", "hard")
        num_examples: Number of symbol mapping examples in prompts
        model: OpenRouter model identifier
        temperature: Sampling temperature (0.0 for deterministic)
        api_key: OpenRouter API key (if None, uses saved key)
        save_to: Optional filename to save results JSON
        verbose: Print progress information
        seed: Random seed for reproducibility

    Returns:
        Tuple of (results, summary)

    Example:
        >>> import symboval
        >>> symboval.set_api_key("your-key-here")
        >>> results, summary = symboval.evaluate(
        ...     num_problems=20,
        ...     difficulty="medium",
        ...     model="anthropic/claude-3.5-sonnet"
        ... )
        >>> print(f"Accuracy: {summary.accuracy:.2%}")
    """
    # Generate problems if not provided
    if problems is None:
        # Only use balanced if we have enough problems for all principles
        use_balanced = (principles is None and num_problems >= len(MathematicalPrinciple.__members__))

        problems = generate_problems(
            num_problems=num_problems,
            principles=principles,
            difficulty=difficulty,
            balanced=use_balanced,
            use_novel_notation=True,
            seed=seed
        )

    # Generate prompts if not provided
    if prompts is None:
        prompts = generate_prompts(
            problems=problems,
            num_examples=num_examples,
            include_thinking=False,
            use_novel_notation=True,
            seed=seed
        )

    # Create evaluator
    evaluator = LLMEvaluator(api_key=api_key)

    # Run evaluation
    if verbose:
        print(f"Evaluating {len(problems)} problems with {model}...")
        print("=" * 60)

    results = evaluator.evaluate_problems(
        problems=problems,
        prompts=prompts,
        model=model,
        temperature=temperature,
        verbose=verbose
    )

    # Check if we got any results
    if not results:
        raise RuntimeError("Evaluation failed - no results returned. Check API key and network connection.")

    # Generate summary
    summary = evaluator.summarize_results(results)

    if verbose:
        print("=" * 60)
        print(f"\nResults Summary:")
        print(f"  Accuracy: {summary.accuracy:.2%} ({summary.correct}/{summary.total_problems})")
        print(f"  Total tokens: {summary.total_tokens:,}")
        print(f"  Est. cost: ${summary.total_cost_estimate:.4f}")
        print(f"  Avg latency: {summary.avg_latency:.2f}s")
        print(f"\nBy Principle:")
        for principle, stats in summary.by_principle.items():
            print(f"  {principle}: {stats['accuracy']:.2%} ({stats['correct']}/{stats['total']})")
        print(f"\nBy Difficulty:")
        for diff, stats in summary.by_difficulty.items():
            print(f"  {diff}: {stats['accuracy']:.2%} ({stats['correct']}/{stats['total']})")

    # Save if requested
    if save_to:
        evaluator.save_results(results, save_to, summary)
        if verbose:
            print(f"\nResults saved to {save_to}")

    return results, summary
