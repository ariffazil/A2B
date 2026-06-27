# Contributing to a2b

Thank you for your interest in the arifOS × AssetOpsBench bridge.

## What is this repo?

`a2b` is the canonical home for arifOS federation's integration with the
[AssetOpsBench](https://github.com/IBM/AssetOpsBench) benchmark. It contains:

- **Eval harness** — runs MCQ scenarios through arifOS governance pipeline
- **Eval results** — disk-verified benchmark runs (no aspirational claims)
- **arifbench agent** — constitutional runner that wraps AssetOpsBench agents with arifOS governance
- **Documentation** — bridge architecture, researcher briefs, project tracker

## How to contribute

### Reporting issues

Use the [issue tracker](https://github.com/ariffazil/a2b/issues). Include:
- What you expected
- What actually happened
- Steps to reproduce
- Your environment (Python version, OS)

### Suggesting improvements

Open an issue with the `enhancement` label. Describe:
- The problem you're trying to solve
- Your proposed approach
- Any alternatives you considered

### Code contributions

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-change`
3. Make your changes
4. Run the linter: `ruff check harness/ src/`
5. Run syntax check: `python3 -c "import ast; ast.parse(open('file.py').read())"`
6. Commit with a clear message
7. Open a PR

### Eval results

If you run the eval harness and want to contribute results:
1. Run: `python3 harness/eval_harness.py --scenarios data/failuresensoriq_standard/sample_50_questions.jsonl --output-dir evals/your_run_name`
2. Include the `eval_aggregate.json` and `eval_results.jsonl` in your PR
3. Document your run configuration (model, governance on/off, any changes)

## Code style

- Python 3.12+
- `ruff` for linting and formatting
- Type hints where practical
- Docstrings for public functions

## License

By contributing, you agree that your contributions will be licensed under the
[Apache License 2.0](LICENSE).

## Code of Conduct

Be respectful. Be honest. Label your uncertainty (OBS/DER/INT/SPEC).
Don't claim things you can't verify.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*
