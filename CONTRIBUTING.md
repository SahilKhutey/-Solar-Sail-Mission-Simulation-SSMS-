# Contributing to Solar Sail Simulation

Thank you for your interest in contributing! We welcome all contributions, from bug fixes to new features and documentation improvements.

## Development Setup

1.  **Fork** the repo on GitHub.
2.  **Clone** your fork.
3.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
4.  **Install dev dependencies**:
    ```bash
    pip install -r requirements.txt
    pip install pytest black flake8
    ```

## Development Standards

-   **Code Style**: We follow PEP 8. Please use `black` to format your code.
-   **Testing**: All new features must include unit tests in `tests/`. Run tests with `pytest` or `python -m unittest discover tests`.
-   **Documentation**: Update docstrings and the README if you change functionality.

## Pull Request Process

1.  Create a feature branch (`git checkout -b feature/amazing-feature`).
2.  Commit your changes.
3.  Run tests to ensure no regressions.
4.  Push to your fork.
5.  Open a Pull Request against the `main` branch.

## Reporting Bugs

Please use the GitHub Issues tab to report bugs. Include:
-   Steps to reproduce.
-   Expected vs actual behavior.
-   Your environment details.
