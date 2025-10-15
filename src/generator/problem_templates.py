import random
from dataclasses import dataclass
from enum import Enum

class ProblemDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class MathematicalPrinciple(Enum):
    COMMUTATIVITY = "commutativity"
    ASSOCIATIVITY = "associativity"
    DISTRIBUTIVITY = "distributivity"
    IDENTITY = "identity"
    INVERSE = "inverse"
    TRANSITIVITY = "transitivity"
    BASIC_ARITHMETIC = "basic_arithmetic"
    MULTI_STEP = "multi_step"

@dataclass
class Problem:
    question: str
    answer: str
    principle: MathematicalPrinciple
    difficulty: ProblemDifficulty
    requires_reasoning: bool
    standard_notation: str
    novel_notation: str
    metadata: dict

class ProblemTemplate:
    def __init__(self, principle, difficulty):
        self.principle = principle
        self.difficulty = difficulty
    def generate(self, symbol_mapper=None):
        raise NotImplementedError

class CommutativityTemplate(ProblemTemplate):
    def __init__(self, difficulty=ProblemDifficulty.EASY):
        super().__init__(MathematicalPrinciple.COMMUTATIVITY, difficulty)

    def generate(self, symbol_mapper=None):
        if self.difficulty == ProblemDifficulty.EASY:
            a, b = random.randint(1, 10), random.randint(1, 10)
        elif self.difficulty == ProblemDifficulty.MEDIUM:
            a, b = random.randint(10, 50), random.randint(10, 50)
        else:
            a, b = random.randint(50, 200), random.randint(50, 200)
        op = random.choice(['+', '*'])
        if op == '+':
            ans = a + b
        else:
            ans = a * b
        std_q = f"If {a} {op} {b} = C, then {b} {op} {a} = ?"
        std_ans = str(ans)
        if symbol_mapper:
            novel_q = symbol_mapper.translate_expression(std_q)
            novel_ans = symbol_mapper.translate_expression(std_ans)
        else:
            novel_q = std_q
            novel_ans = std_ans
        return Problem(question=std_q, answer=std_ans, principle=self.principle,
                      difficulty=self.difficulty, requires_reasoning=True, standard_notation=std_q,
                      novel_notation=novel_q, metadata={"a": a, "b": b, "operator": op})

class AssociativityTemplate(ProblemTemplate):
    def __init__(self, difficulty=ProblemDifficulty.MEDIUM):
        super().__init__(MathematicalPrinciple.ASSOCIATIVITY, difficulty)

    def generate(self, symbol_mapper=None):
        if self.difficulty == ProblemDifficulty.EASY:
            a, b, c = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)
        elif self.difficulty == ProblemDifficulty.MEDIUM:
          a, b, c = random.randint(10, 30), random.randint(10, 30), random.randint(10, 30)
        else:
            a, b, c = random.randint(30, 100), random.randint(30, 100), random.randint(30, 100)
        operator = random.choice(['+', '*'])
        if operator == '+':
            answer = a + b + c
        else:
            answer = a * b * c
        standard_question = f"({a} {operator} {b}) {operator} {c} = ?"
        standard_answer = str(answer)
        if symbol_mapper:
            novel_question = symbol_mapper.translate_expression(standard_question)
            novel_answer = symbol_mapper.translate_expression(standard_answer)
        else:
            novel_question = standard_question
            novel_answer = standard_answer
        return Problem(question=standard_question, answer=standard_answer, principle=self.principle,
                      difficulty=self.difficulty, requires_reasoning=True, standard_notation=standard_question,
                      novel_notation=novel_question, metadata={"a": a, "b": b, "c": c, "operator": operator})

class DistributivityTemplate(ProblemTemplate):
    def __init__(self, difficulty=ProblemDifficulty.MEDIUM):
        super().__init__(MathematicalPrinciple.DISTRIBUTIVITY, difficulty)

    def generate(self, symbol_mapper=None):
        if self.difficulty == ProblemDifficulty.EASY:
            a, b, c = random.randint(2, 5), random.randint(1, 10), random.randint(1, 10)
        elif self.difficulty == ProblemDifficulty.MEDIUM:
            a, b, c = random.randint(2, 10), random.randint(5, 20), random.randint(5, 20)
        else:
            a, b, c = random.randint(5, 20), random.randint(10, 50), random.randint(10, 50)
        answer = a * (b + c)
        standard_question = f"{a} * ({b} + {c}) = ?"
        standard_answer = str(answer)
        if symbol_mapper:
            novel_question = symbol_mapper.translate_expression(standard_question)
            novel_answer = symbol_mapper.translate_expression(standard_answer)
        else:
            novel_question = standard_question
            novel_answer = standard_answer
        return Problem(question=standard_question, answer=standard_answer, principle=self.principle,
                      difficulty=self.difficulty, requires_reasoning=True, standard_notation=standard_question,
                      novel_notation=novel_question, metadata={"a": a, "b": b, "c": c})

class BasicArithmeticTemplate(ProblemTemplate):
    def __init__(self, difficulty=ProblemDifficulty.EASY):
        super().__init__(MathematicalPrinciple.BASIC_ARITHMETIC, difficulty)

    def generate(self, symbol_mapper=None):
        if self.difficulty == ProblemDifficulty.EASY:
            a, b = random.randint(1, 20), random.randint(1, 20)
        elif self.difficulty == ProblemDifficulty.MEDIUM:
            a, b = random.randint(10, 100), random.randint(10, 100)
        else:
            a, b = random.randint(50, 500), random.randint(50, 500)
        operator = random.choice(['+', '-', '*', '/'])
        if operator == '+':
            answer = a + b
        elif operator == '-':
            answer = a - b
        elif operator == '*':
            answer = a * b
        else:
            if self.difficulty == ProblemDifficulty.EASY:
                b = random.randint(1, 10)
                a = b * random.randint(1, 10)
            answer = a // b
        standard_question = f"{a} {operator} {b} = ?"
        standard_answer = str(answer)
        if symbol_mapper:
            novel_question = symbol_mapper.translate_expression(standard_question)
            novel_answer = symbol_mapper.translate_expression(standard_answer)
        else:
            novel_question = standard_question
            novel_answer = standard_answer
        return Problem(question=standard_question, answer=standard_answer, principle=self.principle,
                      difficulty=self.difficulty, requires_reasoning=False, standard_notation=standard_question,
                      novel_notation=novel_question, metadata={"a": a, "b": b, "operator": operator})

class MultiStepTemplate(ProblemTemplate):
    def __init__(self, difficulty=ProblemDifficulty.HARD):
        super().__init__(MathematicalPrinciple.MULTI_STEP, difficulty)

    def generate(self, symbol_mapper=None):
        if self.difficulty == ProblemDifficulty.MEDIUM:
            num_ops = 2
        else:
            num_ops = 3
        if self.difficulty == ProblemDifficulty.MEDIUM:
            numbers = [random.randint(1, 20) for _ in range(num_ops + 1)]
        else:
            numbers = [random.randint(5, 50) for _ in range(num_ops + 1)]
        operators = random.choices(['+', '-', '*'], k=num_ops)
        expression = str(numbers[0])
        result = numbers[0]
        for i, op in enumerate(operators):
            expression += f" {op} {numbers[i + 1]}"
            if op == '+':
                result += numbers[i + 1]
            elif op == '-':
                result -= numbers[i + 1]
            else:
                result *= numbers[i + 1]
        standard_question = f"{expression} = ?"
        standard_answer = str(result)
        if symbol_mapper:
            novel_question = symbol_mapper.translate_expression(standard_question)
            novel_answer = symbol_mapper.translate_expression(standard_answer)
        else:
            novel_question = standard_question
            novel_answer = standard_answer
        return Problem(question=standard_question, answer=standard_answer, principle=self.principle,
                      difficulty=self.difficulty, requires_reasoning=True, standard_notation=standard_question,
                      novel_notation=novel_question, metadata={"numbers": numbers, "operators": operators})

class IdentityTemplate(ProblemTemplate):
    def __init__(self, difficulty=ProblemDifficulty.EASY):
        super().__init__(MathematicalPrinciple.IDENTITY, difficulty)

    def generate(self, symbol_mapper=None):
        a = random.randint(1, 100)
        identity_type = random.choice(['additive', 'multiplicative'])
        if identity_type == 'additive':
            operator = '+'
            identity = 0
            answer = a
        else:
            operator = '*'
            identity = 1
            answer = a
        if random.choice([True, False]):
            standard_question = f"{a} {operator} {identity} = ?"
        else:
            standard_question = f"{identity} {operator} {a} = ?"
        standard_answer = str(answer)
        if symbol_mapper:
            novel_question = symbol_mapper.translate_expression(standard_question)
            novel_answer = symbol_mapper.translate_expression(standard_answer)
        else:
            novel_question = standard_question
            novel_answer = standard_answer
        return Problem(question=standard_question, answer=standard_answer, principle=self.principle,
                      difficulty=self.difficulty, requires_reasoning=True, standard_notation=standard_question,
                      novel_notation=novel_question, metadata={"a": a, "identity_type": identity_type})

class ProblemGenerator:
    TEMPLATE_MAP = {
        MathematicalPrinciple.COMMUTATIVITY: CommutativityTemplate,
        MathematicalPrinciple.ASSOCIATIVITY: AssociativityTemplate,
        MathematicalPrinciple.DISTRIBUTIVITY: DistributivityTemplate,
        MathematicalPrinciple.BASIC_ARITHMETIC: BasicArithmeticTemplate,
        MathematicalPrinciple.MULTI_STEP: MultiStepTemplate,
        MathematicalPrinciple.IDENTITY: IdentityTemplate,
    }

    def __init__(self, seed=None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def generate_problem(self, principle, difficulty=ProblemDifficulty.MEDIUM, symbol_mapper=None):
        template_class = self.TEMPLATE_MAP.get(principle)
        if not template_class:
            raise ValueError(f"No template found for principle: {principle}")
        template = template_class(difficulty=difficulty)
        return template.generate(symbol_mapper=symbol_mapper)

    def generate_problem_set(self, num_problems, principles=None, difficulty=ProblemDifficulty.MEDIUM, symbol_mapper=None):
        if principles is None:
            principles = list(self.TEMPLATE_MAP.keys())
        problems = []
        for _ in range(num_problems):
            principle = random.choice(principles)
            problem = self.generate_problem(principle, difficulty, symbol_mapper)
            problems.append(problem)
        return problems

    def generate_balanced_set(self, problems_per_principle, difficulty=ProblemDifficulty.MEDIUM, symbol_mapper=None):
        problems = []
        for principle in self.TEMPLATE_MAP.keys():
            for _ in range(problems_per_principle):
                problem = self.generate_problem(principle, difficulty, symbol_mapper)
                problems.append(problem)
        random.shuffle(problems)
        return problems
