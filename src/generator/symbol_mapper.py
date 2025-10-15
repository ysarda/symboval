import random
from enum import Enum

class SymbolType(Enum):
    NUMBER = "number"
    OPERATOR = "operator"
    RELATION = "relation"
    VARIABLE = "variable"
    PARENTHESIS = "parenthesis"

class SymbolMapper:
    UNICODE_NUMBERS = [
        "∰", "∴", "∵", "∃", "∀", "∈", "∉", "⊂", "⊃", "⊆",
        "⊇", "⊕", "⊗", "⊙", "⊚", "⊛", "⊝", "⊞", "⊟", "⊠"
    ]

    UNICODE_OPERATORS = [
        "⊕", "⊖", "⊗", "⊘", "⊙", "⊚", "⊛", "⊜", "⊝", "⊞",
        "∗", "∘", "∙", "√", "∛", "∜", "⨁", "⨂", "⨀", "⊎"
    ]

    UNICODE_RELATIONS = [
        "≜", "≝", "≞", "≟", "≠", "≡", "≢", "≣", "≤", "≥",
        "≦", "≧", "≨", "≩", "⊏", "⊐", "⊑", "⊒", "⋖", "⋗"
    ]

    UNICODE_VARIABLES = [
        "α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ",
        "λ", "μ", "ν", "ξ", "π", "ρ", "σ", "τ", "υ", "φ",
        "χ", "ψ", "ω", "Γ", "Δ", "Θ", "Λ", "Ξ", "Π", "Σ"
    ]

    UNICODE_PARENTHESES = {
        "(": ["⟨", "⟪", "⦃", "⦅", "⦇", "⦉", "⦋", "⦍", "⦏"],
        ")": ["⟩", "⟫", "⦄", "⦆", "⦈", "⦊", "⦌", "⦎", "⦐"],
    }

    def __init__(self, seed=None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.mappings = {}
        self.reverse_mappings = {}
        self.used_symbols = set()

    def create_number_mapping(self, numbers, symbol_pool=None):
        if symbol_pool is None:
            symbol_pool = self.UNICODE_NUMBERS.copy()
        avail = [s for s in symbol_pool if s not in self.used_symbols]
        if len(avail) < len(numbers):
            raise ValueError(f"Not enough unique symbols. Need {len(numbers)}, have {len(avail)}")
        selected_syms = random.sample(avail, len(numbers))
        for num, sym in zip(numbers, selected_syms):
            n = str(num)
            self.mappings[n] = sym
            self.reverse_mappings[sym] = n
            self.used_symbols.add(sym)
        return {str(n): self.mappings[str(n)] for n in numbers}

    def create_operator_mapping(self, operators, symbol_pool=None):
        if symbol_pool is None:
            symbol_pool = self.UNICODE_OPERATORS.copy()
        available = [s for s in symbol_pool if s not in self.used_symbols]
        if len(available) < len(operators):
            raise ValueError(f"Not enough unique symbols. Need {len(operators)}, have {len(available)}")
        selected = random.sample(available, len(operators))
        for op, sym in zip(operators, selected):
            self.mappings[op] = sym
            self.reverse_mappings[sym] = op
            self.used_symbols.add(sym)
        return {op: self.mappings[op] for op in operators}

    def create_relation_mapping(self, relations, symbol_pool=None):
        if symbol_pool is None:
          symbol_pool = self.UNICODE_RELATIONS.copy()
        available = [s for s in symbol_pool if s not in self.used_symbols]
        if len(available) < len(relations):
            raise ValueError(f"Not enough unique symbols. Need {len(relations)}, have {len(available)}")
        selected = random.sample(available, len(relations))
        for rel, sym in zip(relations, selected):
            self.mappings[rel] = sym
            self.reverse_mappings[sym] = rel
            self.used_symbols.add(sym)
        return {rel: self.mappings[rel] for rel in relations}

    def create_variable_mapping(self, variables, symbol_pool=None):
        if symbol_pool is None:
            symbol_pool = self.UNICODE_VARIABLES.copy()
        available = [s for s in symbol_pool if s not in self.used_symbols]
        if len(available) < len(variables):
            raise ValueError(f"Not enough unique symbols")
        selected = random.sample(available, len(variables))
        for var, sym in zip(variables, selected):
            self.mappings[var] = sym
            self.reverse_mappings[sym] = var
            self.used_symbols.add(sym)
        return {var: self.mappings[var] for var in variables}

    def create_complete_mapping(self, numbers=None, operators=None, relations=None, variables=None):
        if numbers:
            self.create_number_mapping(numbers)
        if operators:
            self.create_operator_mapping(operators)
        if relations:
            self.create_relation_mapping(relations)
        if variables:
            self.create_variable_mapping(variables)
        return self.mappings.copy()

    def translate_expression(self, expression, use_mapping=True):
        if not use_mapping:
            return expression
        result = expression
        sorted_mappings = sorted(self.mappings.items(), key=lambda x: len(x[0]), reverse=True)
        for standard, novel in sorted_mappings:
            result = result.replace(standard, novel)
        return result

    def reverse_translate(self, expression):
        result = expression
        sorted_mappings = sorted(self.reverse_mappings.items(), key=lambda x: len(x[0]), reverse=True)
        for novel, standard in sorted_mappings:
            result = result.replace(novel, standard)
        return result

    def get_mapping_examples(self, num_examples=5):
        items = list(self.mappings.items())
        if len(items) <= num_examples:
            return items
        return random.sample(items, num_examples)

    def export_mapping(self):
        return {"seed": self.seed, "mappings": self.mappings.copy(), "reverse_mappings": self.reverse_mappings.copy()}

    @classmethod
    def from_mapping(cls, mapping_dict, seed=None):
        mapper = cls(seed=seed)
        mapper.mappings = mapping_dict.copy()
        mapper.reverse_mappings = {v: k for k, v in mapping_dict.items()}
        mapper.used_symbols = set(mapping_dict.values())
        return mapper
