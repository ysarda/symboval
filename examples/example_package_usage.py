import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

import symboval

def main():
    print("=" * 60)
    print("SYMBOVAL - Package Usage Examples")
    print("=" * 60)

    print("\n1. Generate a single problem")
    problem = symboval.generate_problem(
        principle="commutativity",
        difficulty="medium",
        use_novel_notation=True,
        seed=42
    )
    print(f"Standard: {problem.standard_notation}")
    print(f"Novel: {problem.novel_notation}")
    print(f"Answer: {problem.answer}")

    print("\n2. Generate multiple problems")
    problems = symboval.generate_problems(
        num_problems=5,
        difficulty="easy",
        use_novel_notation=True,
        seed=42
    )
    print(f"Generated {len(problems)} problems")
    for i, p in enumerate(problems[:3], 1):
        print(f"  {i}. {p.novel_notation} (Answer: {p.answer})")

    print("\n3. Generate balanced problem set")
    balanced = symboval.generate_problems(
        num_problems=12,
        difficulty="medium",
        balanced=True,
        use_novel_notation=True,
        seed=42
    )
    print(f"Generated {len(balanced)} balanced problems")
    from collections import Counter
    counts = Counter(p.principle.value for p in balanced)
    for principle, count in counts.items():
        print(f"  {principle}: {count}")

    print("\n4. Generate a single prompt")
    prompt = symboval.generate_prompt(
        principle="distributivity",
        difficulty="medium",
        num_examples=3,
        include_thinking=True,
        seed=42
    )
    print(f"Prompt length: {len(prompt)} characters")
    print("First 200 chars:")
    print(prompt[:200] + "...")

    print("\n5. Generate multiple prompts")
    prompts = symboval.generate_prompts(
        num_problems=3,
        principles=["basic_arithmetic", "commutativity"],
        difficulty="easy",
        num_examples=5,
        include_thinking=False,
        seed=42
    )
    print(f"Generated {len(prompts)} prompts")
    for i, prompt in enumerate(prompts, 1):
        print(f"  Prompt {i}: {len(prompt)} characters")

    print("\n6. Generate prompt from existing problem")
    existing_problem = symboval.generate_problem(
        principle="identity",
        difficulty="hard",
        seed=42
    )
    prompt_from_problem = symboval.generate_prompt(
        problem=existing_problem,
        num_examples=10,
        include_thinking=True
    )
    print(f"Custom prompt length: {len(prompt_from_problem)} characters")

    print("\n7. Generate problems with specific principles")
    specific_problems = symboval.generate_problems(
        num_problems=5,
        principles=["commutativity", "associativity", "distributivity"],
        difficulty="hard",
        seed=42
    )
    print(f"Generated {len(specific_problems)} problems with specific principles")
    for p in specific_problems:
        print(f"  - {p.principle.value}: {p.standard_notation}")

    print("\n" + "=" * 60)
    print("Package usage examples completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
