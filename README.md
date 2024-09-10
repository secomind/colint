# Colint

Colint is a command-line utility designed to streamline code formatting and linting for Python projects. It integrates popular tools like `Black`, `Flake8`, and `isort` to help you maintain clean and consistent code with ease.

## Features

- **Code Formatting**: Uses [Black](https://black.readthedocs.io/en/stable/) for automatic code formatting.
- **Linting**: Employs [Flake8](https://flake8.pycqa.org/) to identify and report coding style violations.
- **Import Sorting**: Utilizes [isort](https://pycqa.github.io/isort/) to sort and organize imports.
- **Cleaning**: Removes Python bytecode and cache files.

## Installation

You can install Colint from your local machine or directly from PyPI once it’s published. For now, you can install it using pip from the local directory:

```bash
pip install .
```

## Usage
Once installed, you can use Colint to run various tasks. The available commands are:

- `code-format`: Format the code using Black.
- `flake-lint`: Lint the code using Flake8.
- `isort`: Sort imports using isort.
- `lint`: Run all linting tools in sequence (isort, Black, Flake8).
- `clean`: Remove Python bytecode and cache files.

## Running Tasks
You can run tasks via the command line. Here are examples of how to use each command:

1. Code Formatting:
```bash
colint code-format
```

2. Linting:
```bash
colint flake-lint
```

3. Import Sorting:
```bash
colint isort
```

4. Run All Linters:
```bash
colint lint
```

5. Clean Up:
```bash
colint clean
```

## Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [Black](https://black.readthedocs.io/en/stable/) for code formatting.
- [Flake8](https://flake8.pycqa.org/) for linting.
- [isort](https://pycqa.github.io/isort/)  for import sorting.
