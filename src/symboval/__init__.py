from .generator.symbol_mapper import SymbolMapper
from .generator.problem_templates import (
    Problem,
    ProblemGenerator,
    ProblemDifficulty,
    MathematicalPrinciple
)
from .generator.prompt_builder import PromptBuilder
from .generator.dataset_converter import DatasetConverter

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
    "generate_prompts"
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
    prompt = builder.build_system_prompt() + "\n\n"
    prompt += builder.build_example_section(num_examples) + "\n"
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
        prompt = builder.build_system_prompt() + "\n\n"
        prompt += builder.build_example_section(num_examples) + "\n"
        prompt += builder.build_problem_prompt(problem, use_novel_notation, include_thinking)
        prompts.append(prompt)

    return prompts
