This file serves as the instruction manual for anyone who wants to help improve your code.

Markdown
# Contributing to HierDetect

First off, thank you for considering contributing to HierDetect! It's people like you that make the open-source cybersecurity community so powerful. 

We welcome contributions of all kinds, including bug fixes, new fusion strategies, improved documentation, and new LotL dataset samples.

## 🛠️ Development Setup

To set up your local environment for development:

1. **Fork and Clone:** Fork the repository to your own GitHub account, then clone it locally.
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/hierdetect_test.git
   cd hierdetect_test
Create a Virtual Environment: We highly recommend developing in an isolated environment using Python 3.8 to 3.12.

Bash
python -m venv dev_env
source dev_env/bin/activate  # On Windows use: .\dev_env\Scripts\activate
Install Dependencies:

Bash
# Install CPU-only PyTorch for faster local testing
pip install torch --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
pip install torch-geometric
pip install -r requirements.txt
pip install -e .
Fetch the Models: Download the models.zip from the latest GitHub Release and extract it into a local models/ directory in the project root.

🚀 How to Contribute
Reporting Bugs
If you find a bug, please open an Issue on GitHub.

Security Vulnerabilities: If you find a way to bypass the detection engine or a flaw in the AST parser, do not open a public issue. Please refer to our SECURITY.md for safe reporting instructions.

Standard Bugs: Include your OS, Python version, the exact command you ran, and the error traceback.

Submitting Pull Requests (PRs)
Create a branch: git checkout -b feature/your-feature-name or fix/your-bug-fix.

Make your changes: Keep your commits focused and provide clear commit messages.

Run the Health Check: Ensure your changes don't break the core pipeline by running:

Bash
hierdetect --check --model-dir ./models
Push and Open a PR: Push your branch to your fork and open a Pull Request against our main branch. Describe your changes in detail in the PR description.

🧑‍💻 Coding Standards
Follow standard PEP-8 formatting for Python code.

If you are adding a new Stage 3 Fusion strategy, ensure it is added to the FusionLayer class in src/hierdetect/models/fusion.py and properly registered in the CLI argparse options.

Keep imports clean and avoid adding massive new dependencies unless absolutely necessary.