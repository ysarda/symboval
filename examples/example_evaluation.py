"""Example of using Symboval's evaluation functionality with OpenRouter."""
import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import symboval


def example_1_simple_evaluation():
    """Example 1: Simple evaluation with default settings."""
    print("=" * 70)
    print("Example 1: Simple Evaluation")
    print("=" * 70)
    print()

    # Set your API key (only need to do this once)
    # symboval.set_api_key("api-key")

    # Check if API key is set
    if not symboval.get_api_key():
        print("No API key found!")
        print("Please set your OpenRouter API key:")
        print('  symboval.set_api_key("sk-or-v1-your-key-here")')
        return

    # Generate problems and prompts to access the full details
    problems = symboval.generate_problems(
        num_problems=2,
        difficulty="easy",
        seed=42
    )

    prompts = symboval.generate_prompts(
        problems=problems,
        num_examples=5,
        seed=42
    )

    print("\n" + "=" * 70)
    print("Problem Details:")
    print("=" * 70)
    for i, problem in enumerate(problems):
        print(f"\nProblem {i+1}:")
        print(f"  Standard notation: {problem.standard_notation}")
        print(f"  Novel notation:    {problem.novel_notation}")
        print(f"  Expected answer:   {problem.answer}")
        print(f"  Principle:         {problem.principle.value}")
        print(f"  Difficulty:        {problem.difficulty.value}")

    print("\n" + "=" * 70)
    print("Prompts Sent to Model:")
    print("=" * 70)
    for i, prompt in enumerate(prompts):
        print(f"\nPrompt {i+1}:")
        print("-" * 70)
        print(prompt)
        print("-" * 70)

    # Run evaluation
    results, summary = symboval.evaluate(
        problems=problems,
        prompts=prompts,
        model="meta-llama/llama-3.3-70b-instruct:free",
        temperature=0.0,
        save_to="evaluation_results.json"
    )

    print("\n" + "=" * 70)
    print("Model Responses:")
    print("=" * 70)
    for result in results:
        print(f"\nProblem {result.problem_id + 1}:")
        print(f"  Status: {'✓ CORRECT' if result.is_correct else '✗ INCORRECT'}")
        print(f"  Expected: {result.expected_answer}")
        print(f"  Extracted: {result.extracted_answer}")
        print(f"\n  Full Response:")
        print("  " + "-" * 66)
        for line in result.model_response.split('\n'):
            print(f"  {line}")
        print("  " + "-" * 66)

    print(f"\nCompleted! Check evaluation_results.json for detailed results.")


def example_2_principle_focused():
    """Example 2: Evaluate specific mathematical principles."""
    print("\n" + "=" * 70)
    print("Example 2: Principle-Focused Evaluation")
    print("=" * 70)
    print()

    if not symboval.get_api_key():
        print("Please set your OpenRouter API key first!")
        return

    # Test only commutativity and distributivity
    results, summary = symboval.evaluate(
        num_problems=10,
        principles=["commutativity", "distributivity"],
        difficulty="hard",
        num_examples=10,  # More examples for harder problems
        model="anthropic/claude-3.5-sonnet",
        save_to="principle_results.json"
    )

    # Print detailed per-problem results
    print("\n" + "=" * 70)
    print("Detailed Results:")
    print("=" * 70)
    for result in results:
        status = "✓ CORRECT" if result.is_correct else "✗ INCORRECT"
        print(f"\nProblem {result.problem_id + 1} [{result.principle}] - {status}")
        print(f"  Expected: {result.expected_answer}")
        print(f"  Got: {result.extracted_answer}")
        print(f"  Tokens: {result.prompt_tokens + result.completion_tokens}")


def example_3_model_comparison():
    """Example 3: Compare different models on the same problems."""
    print("\n" + "=" * 70)
    print("Example 3: Model Comparison")
    print("=" * 70)
    print()

    if not symboval.get_api_key():
        print("Please set your OpenRouter API key first!")
        return

    # Generate problems once
    problems = symboval.generate_problems(
        num_problems=10,
        balanced=True,
        difficulty="medium",
        seed=42
    )

    # Generate prompts once
    prompts = symboval.generate_prompts(
        problems=problems,
        num_examples=5,
        seed=42
    )

    models_to_test = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-haiku",
        "openai/gpt-4-turbo",
    ]

    print(f"Testing {len(problems)} problems across {len(models_to_test)} models...\n")

    results_by_model = {}
    for model in models_to_test:
        print(f"\nTesting {model}...")
        print("-" * 70)

        results, summary = symboval.evaluate(
            problems=problems,
            prompts=prompts,
            model=model,
            temperature=0.0,
            verbose=False
        )

        results_by_model[model] = summary

        print(f"  Accuracy: {summary.accuracy:.2%}")
        print(f"  Tokens: {summary.total_tokens:,}")
        print(f"  Latency: {summary.avg_latency:.2f}s")

    # Print comparison
    print("\n" + "=" * 70)
    print("Model Comparison Summary:")
    print("=" * 70)
    for model, summary in results_by_model.items():
        print(f"\n{model}:")
        print(f"  Accuracy: {summary.accuracy:.2%}")
        print(f"  Total tokens: {summary.total_tokens:,}")
        print(f"  Cost estimate: ${summary.total_cost_estimate:.4f}")
        print(f"  Avg latency: {summary.avg_latency:.2f}s")


def example_4_few_shot_analysis():
    """Example 4: Analyze how performance varies with number of examples."""
    print("\n" + "=" * 70)
    print("Example 4: Few-Shot Learning Analysis")
    print("=" * 70)
    print()

    if not symboval.get_api_key():
        print("Please set your OpenRouter API key first!")
        return

    # Generate problems once
    problems = symboval.generate_problems(
        num_problems=15,
        balanced=True,
        difficulty="medium",
        seed=42
    )

    example_counts = [0, 1, 3, 5, 10]
    results_by_count = {}

    for count in example_counts:
        print(f"\nTesting with {count} examples...")
        print("-" * 70)

        # Generate prompts with specific example count
        prompts = symboval.generate_prompts(
            problems=problems,
            num_examples=count,
            seed=42
        )

        results, summary = symboval.evaluate(
            problems=problems,
            prompts=prompts,
            model="anthropic/claude-3.5-sonnet",
            temperature=0.0,
            verbose=False
        )

        results_by_count[count] = summary
        print(f"  Accuracy: {summary.accuracy:.2%}")

    # Print analysis
    print("\n" + "=" * 70)
    print("Few-Shot Learning Analysis:")
    print("=" * 70)
    print("\nExamples | Accuracy | Tokens")
    print("-" * 40)
    for count, summary in results_by_count.items():
        print(f"{count:8d} | {summary.accuracy:7.2%} | {summary.total_tokens:,}")


def example_5_custom_evaluator():
    """Example 5: Using the evaluator directly for custom workflows."""
    print("\n" + "=" * 70)
    print("Example 5: Custom Evaluation Workflow")
    print("=" * 70)
    print()

    if not symboval.get_api_key():
        print("Please set your OpenRouter API key first!")
        return

    # Create evaluator instance
    evaluator = symboval.LLMEvaluator()

    # Generate a single problem
    problem = symboval.generate_problem(
        principle="multi_step",
        difficulty="hard",
        seed=42
    )

    # Generate prompt
    prompt = symboval.generate_prompt(
        problem=problem,
        num_examples=10,
        include_thinking=True,  # Request chain-of-thought
        seed=42
    )

    print("Problem:")
    print(f"  {problem.novel_notation}")
    print(f"  Expected answer: {problem.answer}")
    print()

    # Evaluate with custom settings
    print("Evaluating with chain-of-thought reasoning...")
    result = evaluator.evaluate_problem(
        problem=problem,
        prompt=prompt,
        model="anthropic/claude-3.5-sonnet",
        temperature=0.3,  # Slightly higher temperature
        max_tokens=2048,  # More tokens for reasoning
    )

    print(f"\nModel Response:")
    print("-" * 70)
    print(result.model_response)
    print("-" * 70)

    print(f"\nExtracted Answer: {result.extracted_answer}")
    print(f"Correct: {result.is_correct}")
    print(f"Tokens used: {result.prompt_tokens + result.completion_tokens}")
    print(f"Latency: {result.latency:.2f}s")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("SYMBOVAL - Evaluation Examples")
    print("=" * 70)
    print()
    print("This script demonstrates various evaluation capabilities.")
    print()
    print("Before running, make sure to set your OpenRouter API key:")
    print('  import symboval')
    print('  symboval.set_api_key("sk-or-v1-your-key-here")')
    print()
    print("Or set the OPENROUTER_API_KEY environment variable.")
    print()

    # Uncomment the examples you want to run
    # Note: Some examples will make API calls and incur costs

    example_1_simple_evaluation()
    # example_2_principle_focused()
    # example_3_model_comparison()
    # example_4_few_shot_analysis()
    # example_5_custom_evaluator()

    print("\n" + "=" * 70)
    print("To run an example, uncomment it in the main() function.")
    print("=" * 70)


if __name__ == "__main__":
    main()
