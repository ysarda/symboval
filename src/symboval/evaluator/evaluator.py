"""Evaluation runner for LLM symbolic reasoning tests."""
import re
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from .openrouter_client import OpenRouterClient, ModelResponse
from .config import get_api_key
from ..generator.problem_templates import Problem


@dataclass
class EvaluationResult:
    """Result of evaluating a single problem."""
    problem_id: int
    principle: str
    difficulty: str
    expected_answer: str
    model_response: str
    extracted_answer: Optional[str]
    is_correct: bool
    requires_reasoning: bool
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EvaluationSummary:
    """Summary statistics for an evaluation run."""
    total_problems: int
    correct: int
    incorrect: int
    accuracy: float
    by_principle: Dict[str, Dict[str, Any]]
    by_difficulty: Dict[str, Dict[str, Any]]
    total_tokens: int
    total_cost_estimate: float
    avg_latency: float
    model: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class LLMEvaluator:
    """Evaluator for LLM symbolic reasoning capabilities."""

    def __init__(self, api_key: Optional[str] = None, site_url: Optional[str] = None, app_name: Optional[str] = None):
        """Initialize evaluator.

        Args:
            api_key: OpenRouter API key (if None, will try to load from config)
            site_url: Optional URL for OpenRouter rankings
            app_name: Optional app name for OpenRouter rankings
        """
        if api_key is None:
            api_key = get_api_key()
            if api_key is None:
                raise ValueError(
                    "No API key found. Set it using symboval.set_api_key('your-key') "
                    "or pass it to the evaluator constructor."
                )

        self.client = OpenRouterClient(api_key, site_url, app_name)

    def extract_answer(self, response: str) -> Optional[str]:
        """Extract the answer from model response.

        Looks for patterns like:
        - "answer is X"
        - "= X"
        - "Answer: X"
        - Numbers at the end of response

        Args:
            response: Raw model response

        Returns:
            Extracted answer or None
        """
        response = response.strip()

        # Pattern 1: "answer is X" or "Answer: X"
        match = re.search(r'answer\s*(?:is|:)\s*([+-]?\d+(?:\.\d+)?)', response, re.IGNORECASE)
        if match:
            return match.group(1)

        # Pattern 2: "= X" at end
        match = re.search(r'=\s*([+-]?\d+(?:\.\d+)?)\s*$', response)
        if match:
            return match.group(1)

        # Pattern 3: Last number in the response
        numbers = re.findall(r'([+-]?\d+(?:\.\d+)?)', response)
        if numbers:
            return numbers[-1]

        return None

    def check_answer(self, extracted: Optional[str], expected: str, tolerance: float = 0.01) -> bool:
        """Check if extracted answer matches expected answer.

        Args:
            extracted: Extracted answer from model
            expected: Expected correct answer
            tolerance: Tolerance for numerical comparison

        Returns:
            True if answers match
        """
        if extracted is None:
            return False

        try:
            extracted_num = float(extracted)
            expected_num = float(expected)
            return abs(extracted_num - expected_num) < tolerance
        except (ValueError, TypeError):
            # Fallback to string comparison
            return extracted.strip() == expected.strip()

    def evaluate_problem(
        self,
        problem: Problem,
        prompt: str,
        model: str = "anthropic/claude-3.5-sonnet",
        temperature: float = 0.0,
        problem_id: int = 0,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate a single problem.

        Args:
            problem: Problem to evaluate
            prompt: Full prompt to send to model
            model: Model identifier
            temperature: Sampling temperature
            problem_id: Identifier for this problem
            **kwargs: Additional arguments for model

        Returns:
            EvaluationResult object
        """
        response = self.client.complete(
            prompt=prompt,
            model=model,
            temperature=temperature,
            **kwargs
        )

        extracted = self.extract_answer(response.response)
        is_correct = self.check_answer(extracted, str(problem.answer))

        return EvaluationResult(
            problem_id=problem_id,
            principle=problem.principle.value,
            difficulty=problem.difficulty.value,
            expected_answer=str(problem.answer),
            model_response=response.response,
            extracted_answer=extracted,
            is_correct=is_correct,
            requires_reasoning=problem.requires_reasoning,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            latency=response.latency,
            timestamp=datetime.now().isoformat()
        )

    def evaluate_problems(
        self,
        problems: List[Problem],
        prompts: List[str],
        model: str = "anthropic/claude-3.5-sonnet",
        temperature: float = 0.0,
        delay: float = 0.5,
        verbose: bool = True,
        **kwargs
    ) -> List[EvaluationResult]:
        """Evaluate multiple problems.

        Args:
            problems: List of problems to evaluate
            prompts: List of prompts corresponding to problems
            model: Model identifier
            temperature: Sampling temperature
            delay: Delay between requests in seconds
            verbose: Print progress information
            **kwargs: Additional arguments for model

        Returns:
            List of EvaluationResult objects
        """
        if len(problems) != len(prompts):
            raise ValueError("Number of problems must match number of prompts")

        results = []

        for i, (problem, prompt) in enumerate(zip(problems, prompts)):
            if verbose:
                print(f"Evaluating problem {i+1}/{len(problems)}... ", end="", flush=True)

            try:
                result = self.evaluate_problem(
                    problem=problem,
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    problem_id=i,
                    **kwargs
                )
                results.append(result)

                if verbose:
                    status = "✓" if result.is_correct else "✗"
                    print(f"{status} ({result.extracted_answer} vs {result.expected_answer})")

            except Exception as e:
                import traceback
                if verbose:
                    print(f"Error: {e}")
                    print(f"  Full traceback: {traceback.format_exc()}")
                # Create failed result
                results.append(EvaluationResult(
                    problem_id=i,
                    principle=problem.principle.value,
                    difficulty=problem.difficulty.value,
                    expected_answer=str(problem.answer),
                    model_response=f"ERROR: {str(e)}",
                    extracted_answer=None,
                    is_correct=False,
                    requires_reasoning=problem.requires_reasoning,
                    model=model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    latency=0.0,
                    timestamp=datetime.now().isoformat()
                ))

            # Rate limiting delay
            if i < len(problems) - 1:
                import time
                time.sleep(delay)

        return results

    def summarize_results(self, results: List[EvaluationResult]) -> EvaluationSummary:
        """Generate summary statistics from evaluation results.

        Args:
            results: List of evaluation results

        Returns:
            EvaluationSummary object
        """
        if not results:
            raise ValueError("Cannot summarize empty results")

        total = len(results)
        correct = sum(1 for r in results if r.is_correct)
        incorrect = total - correct
        accuracy = correct / total if total > 0 else 0.0

        # By principle
        by_principle = {}
        for result in results:
            if result.principle not in by_principle:
                by_principle[result.principle] = {"correct": 0, "total": 0}
            by_principle[result.principle]["total"] += 1
            if result.is_correct:
                by_principle[result.principle]["correct"] += 1

        for principle in by_principle:
            stats = by_principle[principle]
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0

        # By difficulty
        by_difficulty = {}
        for result in results:
            if result.difficulty not in by_difficulty:
                by_difficulty[result.difficulty] = {"correct": 0, "total": 0}
            by_difficulty[result.difficulty]["total"] += 1
            if result.is_correct:
                by_difficulty[result.difficulty]["correct"] += 1

        for difficulty in by_difficulty:
            stats = by_difficulty[difficulty]
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0

        # Token and cost statistics
        total_tokens = sum(r.prompt_tokens + r.completion_tokens for r in results)
        # Rough cost estimate: ~$3/M tokens for Claude Sonnet (varies by model)
        cost_per_million = 3.0
        total_cost_estimate = (total_tokens / 1_000_000) * cost_per_million

        # Latency
        avg_latency = sum(r.latency for r in results) / len(results) if results else 0.0

        model = results[0].model if results else "unknown"

        return EvaluationSummary(
            total_problems=total,
            correct=correct,
            incorrect=incorrect,
            accuracy=accuracy,
            by_principle=by_principle,
            by_difficulty=by_difficulty,
            total_tokens=total_tokens,
            total_cost_estimate=total_cost_estimate,
            avg_latency=avg_latency,
            model=model,
            timestamp=datetime.now().isoformat()
        )

    def save_results(self, results: List[EvaluationResult], filename: str, summary: Optional[EvaluationSummary] = None):
        """Save evaluation results to JSON file.

        Args:
            results: List of evaluation results
            filename: Output filename
            summary: Optional summary to include
        """
        output = {
            "results": [r.to_dict() for r in results],
        }

        if summary:
            output["summary"] = summary.to_dict()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_results(filename: str):
        """Load evaluation results from JSON file.

        Args:
            filename: Input filename

        Returns:
            Tuple of (results list, summary or None)
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = [EvaluationResult(**r) for r in data["results"]]
        summary = EvaluationSummary(**data["summary"]) if "summary" in data else None

        return results, summary
