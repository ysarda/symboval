import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from generator.symbol_mapper import SymbolMapper
from generator.dataset_converter import DatasetConverter


def create_sample_dataset():
    sample_problems = [
        {
            "question": "What is 15 + 27?",
            "answer": "42",
            "module": "arithmetic__add_sub"
        },
        {
            "question": "Calculate 8 * 9",
            "answer": "72",
            "module": "arithmetic__mul"
        },
        {
            "question": "If 5 + 3 = 8, then 3 + 5 = ?",
            "answer": "8",
            "module": "algebra__commutativity"
        },
        {
            "question": "Solve (4 + 6) * 2",
            "answer": "20",
            "module": "algebra__multi_step"
        },
        {
            "question": "What is 100 - 35?",
            "answer": "65",
            "module": "arithmetic__add_sub"
        }
    ]

    return sample_problems


def main():
    print("=" * 60)
    print("SYMBOVAL - Dataset Integration Example")
    print("=" * 60)

    print("\n1. Creating Sample Dataset...")
    sample_data = create_sample_dataset()

    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)

    sample_file = data_dir / 'sample_dataset.json'
    with open(sample_file, 'w') as f:
        json.dump(sample_data, f, indent=2)

    print(f"Created sample dataset with {len(sample_data)} problems")
    print(f"Saved to: {sample_file}")

    print("\n2. Creating Symbol Mapper...")
    mapper = SymbolMapper(seed=123)
    mapper.create_complete_mapping(
        numbers=list(range(0, 101)),
        operators=['+', '-', '*', '/'],
        relations=['=', '?']
    )

    print(f"Created mappings for {len(mapper.mappings)} symbols")

    print("\n3. Loading and Converting Dataset...")
    converter = DatasetConverter(symbol_mapper=mapper)

    problems = converter.load_deepmind_dataset(sample_file)

    print(f"\nLoaded {len(problems)} problems")

    print("\n4. Converted Problems:")
    for i, problem in enumerate(problems, 1):
        print(f"\n--- Problem {i} ---")
        print(f"Module: {problem.metadata.get('module', 'N/A')}")
        print(f"Standard: {problem.standard_notation}")
        print(f"Novel:    {problem.novel_notation}")
        print(f"Answer:   {problem.answer}")
        print(f"Principle: {problem.principle.value}")
        print(f"Difficulty: {problem.difficulty.value}")

    print("\n5. Exporting Problems...")
    output_dir = Path(__file__).parent.parent / 'data' / 'generated'
    output_file = output_dir / 'converted_problems.json'

    converter.export_problems(problems, output_file)

    print("\n6. Creating Parallel Datasets...")
    parallel_datasets = converter.create_parallel_datasets(problems, output_dir)

    print("\nParallel datasets created:")
    for dataset_type, path in parallel_datasets.items():
        print(f"  {dataset_type}: {path}")

    print("\n7. Custom Dataset Conversion...")
    custom_data = [
        {"question": "2 + 2 = ?", "answer": "4"},
        {"question": "10 * 5 = ?", "answer": "50"},
        {"question": "100 - 25 = ?", "answer": "75"}
    ]

    custom_problems = converter.convert_custom_dataset(custom_data)
    print(f"\nConverted {len(custom_problems)} custom problems")

    print("\n" + "=" * 60)
    print("Dataset integration example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
