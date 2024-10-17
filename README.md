# Cobra Lint (COLINT)

This repository defines a robust linter for maintaining high-quality code standards across our project. 
Our linter leverages the power of several well-established tools:

- **Flake8**: Identifies and reports on various coding errors and stylistic issues.
- **Black**: Provides consistent code formatting by automatically reformatting code to adhere to standard style guides.
- **isort**: Ensures that imports are properly sorted and organized within each file.

### Additional Linting Features

In addition to the primary linting utilities, our linter performs the following checks:

- **Newline at End of Files**: Verifies that every file in the project ends with a newline character, ensuring compatibility with various tools and editors.
- **Cleaned Jupyter Notebooks**: Ensures that all Jupyter notebooks are free from any output or unnecessary metadata, keeping the notebooks lightweight and easy to review.

## Installation

Colint can be easily installed via `pip`. 
However, we **strongly** suggest you install `colint` in a separate environment from your production/development one.

### In a venv environment.

- Create a new environment using `venv`, and activate it.

  Example:
  ```sh
  python3 -m venv colint_env
  source colint_env/bin/activate
  ```

- Install `colint` in the new environment:

  ```sh
  pip install git+ssh://git@github.com/secomind/colint.git
  ```

### In a conda environment

- Create and activate a new conda environment.

  Example:
  ```sh
  conda create -n colint
  conda activate colint
  ```

- Install `git` and `pip` in the new environment.
  ```sh
  conda install git pip
  ```

- Install `colint`
  ```sh
  pip install git+ssh://git@github.com/secomind/colint.git
  ```

## Usage

The `colint` script provides several commands for maintaining code quality and cleanliness across Python scripts and Jupyter notebooks.

```
usage: colint [-h] [--check] [--clean-notebooks]
              command
              path_to_dir
```

### Positional Arguments
- **command**: Specify the command to execute. Options include:
  - `sort-libraries`: Sorts and organizes the library imports, it uses the `isort` library.
  - `code-format`: Formats the code according to defined style guides, it uses the `black` library.
  - `grammar-check`: Checks for and corrects grammatical/styling errors in code and docstrings, it uses the `flake8` library.
  - `newline-fix`: Fixes newline inconsistencies in the files.
  - `clean-jupyter`: Cleans Jupyter notebook files by removing unnecessary metadata and outputs.
  - `lint`: Performs all the above operations except `clean-jupyter`. To include `clean-jupyter`, use the `--clean-notebooks` flag.
  - `docformat`: **Experimental** Formats docstrings and commented lines to adhere to the google docstring standard, breaks lines so that 
    their length adheres to the style guide. Please read the section "Experimental Commands" before using this.

- `path_to_dir`: Provide the path to the directory that needs linting.

### Options
- `-h`, `--help`: Show an help message and exit.
- `--check`: Enable check mode.
  In this mode, linting will not modify files; it will only check for issues.
- `--clean-notebooks`: Enable clean-notebooks mode.
  If the lint command is selected, this adds a procedure to clean Jupyter notebooks.
  If another command is used, this option has no effect.

### Examples

**Lint a Directory**
```sh
colint lint /path/to/your/project
```

**Check Code Format Without Modifying Files**
```sh
colint code-format /path/to/your/project --check
```

**Sort Libraries in Directory**
```sh
colint sort-libraries /path/to/your/project
```

**Clean Jupyter Notebooks and Lint**
```sh
colint lint /path/to/your/project --clean-notebooks
```

**Grammar Check**
```sh
colint grammar-check /path/to/your/project
```

### Experimental Commands

The following commands are right now **experimental** and are not meant to be used in a production environment:
- `docformat`

**Docformat**
Formats a document so that it adheres the google (and only google!) docstring standard. It will break lines so that their length is the same as
the one you have set in the style guide. It will try to "guess" the indentation of each paragraph.

__If there are multiple indentation levels in the same paragraph, it will remove them__

The command will work only on a single file at the time, because you should always check "by hand" the results of the doc-formatting, and you
__should not take the results as granted__.

## Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
