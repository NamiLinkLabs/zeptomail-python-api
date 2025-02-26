# Contributing

Contributions to the ZeptoMail Python API are welcome! Here's how you can help:

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/NamiLinkLabs/zeptomail-python-api.git
   cd zeptomail-python-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Running Tests

Run the tests using pytest:

```bash
pytest
```

## Building Documentation

The documentation is built using MkDocs with the mkdocstrings plugin:

```bash
mkdocs build
```

To serve the documentation locally:

```bash
mkdocs serve
```

## Code Style

This project follows PEP 8 style guidelines. You can check your code with:

```bash
flake8 zeptomail tests
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Adding New Features

When adding new features:

1. Add appropriate docstrings following Google style
2. Write tests for your new feature
3. Update the documentation if necessary
4. Ensure all tests pass before submitting a PR
