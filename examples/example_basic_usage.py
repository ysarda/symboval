import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from generator.symbol_mapper import SymbolMapper
from generator.problem_templates import (
    ProblemGenerator,
    MathematicalPrinciple,
    ProblemDifficulty
)
from generator.prompt_builder import PromptBuilder


def main():
    print("=" * 60)
    print("SYMBOVAL - Basic Problem Generation Example")
    print("=" * 60)

    print("\n1. Creating Symbol Mapper...")
    mapper = SymbolMapper(seed=42)

    numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    operators = ['+', '-', '*', '/']
    relations = ['=', '<', '>']

    mapper.create_complete_mapping(
        numbers=numbers,
        operators=operators,
        relations=relations
    )

    print("\nSymbol Mappings Created:")
    for standard, novel in list(mapper.mappings.items())[:10]:
        print(f"  {standard} -> {novel}")

    print("\n2. Generating Problems...")
    generator = ProblemGenerator(seed=42)

    principles_to_test = [
        MathematicalPrinciple.BASIC_ARITHMETIC,
        MathematicalPrinciple.COMMUTATIVITY,
        MathematicalPrinciple.DISTRIBUTIVITY,
        MathematicalPrinciple.MULTI_STEP
    ]

    problems = []
    for principle in principles_to_test:
        problem = generator.generate_problem(
            principle=principle,
            difficulty=ProblemDifficulty.MEDIUM,
            symbol_mapper=mapper
        )
        problems.append(problem)

    print("\n3. Generated Problems:")
    for i, problem in enumerate(problems, 1):
        print(f"\n--- Problem {i} ({problem.principle.value}) ---")
        print(f"Standard notation: {problem.standard_notation}")
        print(f"Novel notation:    {problem.novel_notation}")
        print(f"Answer:            {problem.answer}")
        print(f"Difficulty:        {problem.difficulty.value}")
        print(f"Requires reasoning: {problem.requires_reasoning}")

    print("\n4. Building LLM Prompts...")
    prompt_builder = PromptBuilder(mapper)

    test_problem = problems[0]
    prompt = prompt_builder.build_problem_prompt(
        test_problem,
        use_novel_notation=True,
        include_thinking=True
    )

    print("\nExample Prompt for LLM:")
    print("-" * 60)
    example_section = prompt_builder.build_example_section(num_examples=5)
    print(example_section)
    print(prompt)
    print("-" * 60)

    print("\n5. Generating Balanced Problem Set...")
    balanced_set = generator.generate_balanced_set(
        problems_per_principle=2,
        difficulty=ProblemDifficulty.MEDIUM,
        symbol_mapper=mapper
    )

    print(f"\nGenerated {len(balanced_set)} problems")
    print("Distribution by principle:")
    from collections import Counter
    principle_counts = Counter(p.principle for p in balanced_set)
    for principle, count in principle_counts.items():
        print(f"  {principle.value}: {count}")

    print("\n6. Few-Shot Learning Sequence...")
    test_problem = problems[1]
    few_shot_prompts = prompt_builder.build_few_shot_learning_sequence(
        test_problem,
        example_counts=[0, 1, 3, 5]
    )

    print("\nGenerated prompts with varying example counts:")
    for count, prompt in few_shot_prompts.items():
        print(f"  - {count} examples: {len(prompt)} characters")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
