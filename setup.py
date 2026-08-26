"""
Setup configuration for ExamTester v2.0

A generic, reusable framework for automatically evaluating student code
through test cases with full OOP architecture.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = """
# ExamTester v2.0

A generic and reusable OOP framework for automatically evaluating student code through test cases.

## Features

- **Full OOP Architecture**: Class-based exercises and test generators
- **Builder Pattern**: Fluent API with method chaining
- **Pre-calculated Test Cases**: Execute correct solution once for 100x performance improvement
- **Flexible Naming**: Support folder names with spaces ("Adriana Amador") and files with underscores ("Adriana_Amador_1.py")
- **Reproducible Testing**: Seed-based random test case generation
- **Custom Comparators**: Pluggable comparison functions for different output types
- **Multi-format Reports**: Generate JSON and Markdown reports
- **Type Safety**: Full type hints throughout the codebase
- **Comprehensive Validation**: Clear exception messages with configuration tracking

## Quick Start

```python
from exam_tester import ExamTester, Exercise
from exam_tester.generators import IntegerPairGenerator

class SumaExercise(Exercise):
    def __init__(self):
        super().__init__(
            name="suma",
            function_name="suma",
            file_suffix=1
        )

    def get_solution(self):
        return lambda a, b: a + b

    def get_test_generator(self):
        return IntegerPairGenerator(
            fixed_cases=[(0, 0), (1, 1), (-1, 1)],
            min_val=-1000,
            max_val=1000
        )

# Configure and run
tester = (ExamTester("My Exam")
    .add_exercise(SumaExercise())
    .set_students_path("./StudentsCode")
    .set_results_path("./Results")
    .generate_test_cases(num_random=100, seed=42)
    .evaluate_all()
    .generate_reports(formats=['json', 'markdown'])
)
```

## Installation

```bash
pip install exam-tester
```

## Documentation

See the `examples/` directory for complete usage examples.
"""

setup(
    # Package metadata
    name="exam-tester",
    version="2.0.0",
    author="ExamTester Contributors",
    author_email="",
    description="A generic OOP framework for automatically evaluating student code through test cases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QuiquiMatCom2004/exam-tester",

    # Package discovery
    packages=find_packages(exclude=["examples", "tests", "StudentsCode", "Results"]),

    # Python version requirement
    python_requires=">=3.7",

    # Dependencies (none required for base package)
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],

    # Optional dependencies for development
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },

    # Package classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education :: Testing",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],

    # Keywords for PyPI search
    keywords=[
        "education",
        "testing",
        "evaluation",
        "automated-testing",
        "student-code",
        "exam",
        "grading",
        "test-cases",
    ],

    # Package data to include
    package_data={
        "exam_tester": ["py.typed"],  # Indicate package has type hints
    },

    # Entry points (if needed in the future)
    entry_points={
        # Could add CLI tool here if desired
        # "console_scripts": [
        #     "exam-tester=exam_tester.cli:main",
        # ],
    },

    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/QuiquiMatCom2004/exam-tester/issues",
        "Source": "https://github.com/QuiquiMatCom2004/exam-tester",
        "Documentation": "https://github.com/QuiquiMatCom2004/exam-tester/blob/main/README.md",
    },

    # License
    license="MIT",

    # Zip safe
    zip_safe=False,
)
