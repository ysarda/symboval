class PromptBuilder:
    def __init__(self, symbol_mapper):
        self.symbol_mapper = symbol_mapper

    def build_system_prompt(self):
        return ("You are a mathematical reasoning assistant. You will be given problems "
            "using novel mathematical notation. Your task is to solve these problems "
            "by understanding the underlying mathematical relationships. "
            "Provide only the final answer in the same notation as the problem.")

    def build_example_section(self, num_examples=5, simple_only=True):
        if num_examples == 0:
            return "You will solve mathematical problems using novel notation. No examples are provided.\n"
        exs = self.symbol_mapper.get_mapping_examples(num_examples)
        txt = "You will be given mathematical problems using a novel notation system. "
        txt += "Here are the basic symbol mappings:\n\n"
        for std, nov in exs:
            if std.isdigit():
                txt += f"  {nov} represents {std}\n"
            elif std in ['+', '-', '*', '/']:
                op_names = {'+': 'plus', '-': 'minus', '*': 'times', '/': 'divided by'}
                txt += f"  {nov} represents {op_names.get(std, std)}\n"
            elif std == '=':
                txt += f"  {nov} represents equals\n"
            else:
                txt += f"  {nov} represents {std}\n"
        txt += "\nUsing these mappings, solve the following problems.\n"
        return txt

    def build_problem_prompt(self, problem, use_novel_notation=True, include_thinking=False):
        question = problem.novel_notation if use_novel_notation else problem.standard_notation
        prompt = f"Problem: {question}\n"
        if include_thinking:
            prompt += "\nPlease show your reasoning step-by-step, then provide your final answer.\n"
            prompt += "Format your response as:\nReasoning: [your step-by-step work]\nAnswer: [final answer]\n"
        else:
            prompt += "\nAnswer: "
        return prompt

    def build_batch_prompt(self, problems, num_examples=5, use_novel_notation=True, include_thinking=False):
        prompt = self.build_system_prompt() + "\n\n"
        prompt += self.build_example_section(num_examples) + "\n"
        for i, problem in enumerate(problems, 1):
            prompt += f"\n--- Problem {i} ---\n"
            prompt += self.build_problem_prompt(problem, use_novel_notation, include_thinking)
            prompt += "\n"
        return prompt

    def build_principle_test_prompt(self, principle, test_problems, num_examples=3):
        principle_descriptions = {"commutativity": "the order of operations doesn't change the result",
            "associativity": "how operations are grouped doesn't change the result",
            "distributivity": "multiplication distributes over addition",
            "identity": "certain elements don't change values when applied",
            "basic_arithmetic": "basic mathematical operations",
            "multi_step": "problems requiring multiple sequential operations"}
        prompt = self.build_system_prompt() + "\n\n"
        desc = principle_descriptions.get(principle.value if hasattr(principle, 'value') else principle, principle)
        prompt += f"These problems test your understanding of {desc}.\n\n"
        prompt += self.build_example_section(num_examples) + "\n"
        for i, problem in enumerate(test_problems, 1):
            prompt += f"\n--- Problem {i} ---\n"
            prompt += self.build_problem_prompt(problem, use_novel_notation=True, include_thinking=True)
            prompt += "\n"
        return prompt

    def build_zero_shot_prompt(self, problem):
        prompt = self.build_system_prompt() + "\n\n"
        prompt += "Solve the following problem using the novel notation. "
        prompt += "Infer the meaning from context.\n\n"
        prompt += self.build_problem_prompt(problem, use_novel_notation=True, include_thinking=True)
        return prompt

    def build_comparative_prompt(self, problem, num_examples=5):
        standard_prompt = self.build_system_prompt() + "\n\n"
        standard_prompt += "Solve the following problem:\n\n"
        standard_prompt += self.build_problem_prompt(problem, use_novel_notation=False, include_thinking=True)
        novel_prompt = self.build_system_prompt() + "\n\n"
        novel_prompt += self.build_example_section(num_examples) + "\n"
        novel_prompt += self.build_problem_prompt(problem, use_novel_notation=True, include_thinking=True)
        return {"standard": standard_prompt, "novel": novel_prompt}

    def build_few_shot_learning_sequence(self, test_problem, example_counts=[0, 1, 3, 5, 10]):
        prompts = {}
        for count in example_counts:
            if count == 0:
                prompts[count] = self.build_zero_shot_prompt(test_problem)
            else:
                prompt = self.build_system_prompt() + "\n\n"
                prompt += self.build_example_section(count) + "\n"
                prompt += self.build_problem_prompt(test_problem, use_novel_notation=True, include_thinking=True)
                prompts[count] = prompt
        return prompts

    def extract_answer_from_response(self, response, include_reasoning=False):
        result = {}
        if include_reasoning:
            if "Reasoning:" in response and "Answer:" in response:
                parts = response.split("Answer:")
                reasoning_part = parts[0].replace("Reasoning:", "").strip()
                answer_part = parts[1].strip() if len(parts) > 1 else ""
                result["reasoning"] = reasoning_part
                result["answer"] = answer_part
            else:
                lines = response.strip().split('\n')
                result["reasoning"] = '\n'.join(lines[:-1])
                result["answer"] = lines[-1].strip()
        else:
            result["answer"] = response.strip()
        return result

    def export_prompt_config(self):
        return {"system_prompt": self.build_system_prompt(), "symbol_mappings": self.symbol_mapper.export_mapping()}
