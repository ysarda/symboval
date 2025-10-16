import json
import re
from pathlib import Path
from .problem_templates import Problem, MathematicalPrinciple, ProblemDifficulty

class DatasetConverter:
    def __init__(self, symbol_mapper=None):
        self.symbol_mapper = symbol_mapper

    def parse_deepmind_problem(self, problem_data):
        try:
            question = problem_data.get('question', '')
            answer = problem_data.get('answer', '')
            module = problem_data.get('module', 'unknown')
            principle = self._infer_principle(module)
            difficulty = self._infer_difficulty(question, answer)
            requires_reasoning = self._requires_reasoning(question, module)
            if self.symbol_mapper:
                novel_notation = self.symbol_mapper.translate_expression(question)
                novel_answer = self.symbol_mapper.translate_expression(str(answer))
            else:
                novel_notation = question
                novel_answer = str(answer)
            return Problem(question=question, answer=str(answer), principle=principle, difficulty=difficulty,
                requires_reasoning=requires_reasoning, standard_notation=question, novel_notation=novel_notation,
                metadata={'source': 'deepmind_mathematics', 'module': module, 'original_data': problem_data})
        except Exception as e:
            print(f"Error parsing problem: {e}")
            return None

    def _infer_principle(self, module):
        module_lower = module.lower()
        if 'arithmetic' in module_lower or 'add' in module_lower or 'mul' in module_lower:
            return MathematicalPrinciple.BASIC_ARITHMETIC
        elif 'algebra' in module_lower:
            return MathematicalPrinciple.MULTI_STEP
        elif 'comparison' in module_lower:
            return MathematicalPrinciple.TRANSITIVITY
        else:
            return MathematicalPrinciple.BASIC_ARITHMETIC

    def _infer_difficulty(self, question, answer):
        num_operations = len(re.findall(r'[+\-*/]', question))
        numbers = re.findall(r'\d+', question)
        if numbers:
            max_number = max([int(n) for n in numbers])
        else:
            max_number = 0
        if num_operations <= 1 and max_number < 20:
            return ProblemDifficulty.EASY
        elif num_operations <= 2 and max_number < 100:
            return ProblemDifficulty.MEDIUM
        else:
            return ProblemDifficulty.HARD

    def _requires_reasoning(self, question, module):
        if 'if' in question.lower() or 'then' in question.lower():
            return True
        operations = len(re.findall(r'[+\-*/]', question))
        if operations > 1:
            return True
        reasoning_modules = ['algebra', 'calculus', 'polynomials']
        if any(mod in module.lower() for mod in reasoning_modules):
            return True
        return False

    def load_deepmind_dataset(self, dataset_path, max_problems=None, filter_modules=None):
        problems = []
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                if dataset_path.suffix == '.jsonl':
                    for line in f:
                        if max_problems and len(problems) >= max_problems:
                            break
                        try:
                            problem_data = json.loads(line.strip())
                            if filter_modules:
                                module = problem_data.get('module', '')
                                if not any(fm in module for fm in filter_modules):
                                    continue
                            problem = self.parse_deepmind_problem(problem_data)
                            if problem:
                                problems.append(problem)
                        except json.JSONDecodeError:
                            continue
                else:
                    data = json.load(f)
                    if isinstance(data, list):
                        problem_list = data
                    else:
                        problem_list = data.get('problems', [])
                    for problem_data in problem_list:
                        if max_problems and len(problems) >= max_problems:
                            break
                        if filter_modules:
                            module = problem_data.get('module', '')
                            if not any(fm in module for fm in filter_modules):
                                continue
                        problem = self.parse_deepmind_problem(problem_data)
                        if problem:
                            problems.append(problem)
        except FileNotFoundError:
            print(f"Dataset file not found: {dataset_path}")
        except Exception as e:
            print(f"Error loading dataset: {e}")
        return problems

    def convert_custom_dataset(self, problems_data, question_key='question', answer_key='answer'):
        problems = []
        for problem_data in problems_data:
            question = problem_data.get(question_key, '')
            answer = problem_data.get(answer_key, '')
            if not question or not answer:
                continue
            principle = MathematicalPrinciple.BASIC_ARITHMETIC
            difficulty = self._infer_difficulty(question, str(answer))
            requires_reasoning = self._requires_reasoning(question, '')
            if self.symbol_mapper:
                novel_notation = self.symbol_mapper.translate_expression(question)
                novel_answer = self.symbol_mapper.translate_expression(str(answer))
            else:
                novel_notation = question
                novel_answer = str(answer)
            problem = Problem(question=question, answer=str(answer), principle=principle, difficulty=difficulty,
                requires_reasoning=requires_reasoning, standard_notation=question, novel_notation=novel_notation,
                metadata={'source': 'custom', 'original_data': problem_data})
            problems.append(problem)
        return problems

    def export_problems(self, problems, output_path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        problems_data = []
        for problem in problems:
            problem_dict = {
                'question': problem.question,
                'answer': problem.answer,
                'principle': problem.principle.value,
                'difficulty': problem.difficulty.value,
                'requires_reasoning': problem.requires_reasoning,
                'standard_notation': problem.standard_notation,
                'novel_notation': problem.novel_notation,
                'metadata': problem.metadata
            }
            problems_data.append(problem_dict)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(problems_data, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(problems)} problems to {output_path}")

    def create_parallel_datasets(self, problems, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        standard_data = []
        for problem in problems:
            standard_data.append({
                'question': problem.standard_notation,
                'answer': problem.answer,
                'principle': problem.principle.value,
                'difficulty': problem.difficulty.value,
                'metadata': problem.metadata
            })
        standard_path = output_dir / 'dataset_standard.json'
        with open(standard_path, 'w', encoding='utf-8') as f:
            json.dump(standard_data, f, indent=2, ensure_ascii=False)
        novel_data = []
        for problem in problems:
            if self.symbol_mapper:
                answer_val = self.symbol_mapper.translate_expression(problem.answer)
            else:
                answer_val = problem.answer
            novel_data.append({
                'question': problem.novel_notation,
                'answer': answer_val,
                'principle': problem.principle.value,
                'difficulty': problem.difficulty.value,
                'metadata': problem.metadata
            })
        novel_path = output_dir / 'dataset_novel.json'
        with open(novel_path, 'w', encoding='utf-8') as f:
            json.dump(novel_data, f, indent=2, ensure_ascii=False)
        print(f"Created parallel datasets in {output_dir}")
        return {'standard': standard_path, 'novel': novel_path}
