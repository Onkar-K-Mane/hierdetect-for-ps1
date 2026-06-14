
# 🛡️ HierDetect: Smart PowerShell & LotL Malware Detector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**HierDetect** is an advanced AI tool designed to catch malicious PowerShell and Living-off-the-Land (LotL) scripts before they can do harm. 

Instead of relying on a single AI model that might be too slow or miss hidden threats, HierDetect uses a **3-stage pipeline** to balance lightning-fast speed with deep, accurate inspection.

---

## 🧠 How It Works (The 3 Stages)

Think of HierDetect like a highly secure building:

1. **Stage 1: The Bouncer (Fast Triage)**
   * **What it is:** A fast XGBoost machine learning model.
   * **What it does:** It looks at basic features (like length, entropy, and specific keywords) to immediately wave through clearly safe scripts in less than 1 millisecond. If something looks even slightly suspicious, it gets sent to Stage 2.
2. **Stage 2: The Detectives (Deep Inspection)**
   * **What it is:** Two heavy-duty neural networks working in parallel.
   * **What it does:** * *The Reader (CodeBERT):* Reads the actual text of the script to understand its intent.
     * *The Architect (GATv2):* Analyzes the structural blueprint (AST Graph) of the code to see how it operates under the hood.
3. **Stage 3: The Judge (AI Fusion)**
   * **What it is:** A "Cross-Modal Attention" fusion layer.
   * **What it does:** It takes the opinions from Stage 1 and Stage 2, weighs the evidence, and makes a final, highly accurate decision on whether the script is **MALICIOUS** or **BENIGN**.

---

## 🚀 Installation 

It takes just a few minutes to get HierDetect running. We recommend doing this inside a Python virtual environment.

**1. Download the tool:**
```bash
git clone [https://github.com/Onkar-K-Mane/hierdetect_test.git](https://github.com/Onkar-K-Mane/hierdetect_test.git)
cd hierdetect_test

```

**2. Install the required software:**
*(Note: We recommend installing the CPU version of PyTorch first so it doesn't download massive gigabytes of unnecessary GPU files).*

```bash
pip install torch --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
pip install torch-geometric
pip install -r requirements.txt
pip install -e .

```

**3. Add your AI Models:**

* Download the pre-trained AI models from our official release page.
* Place all of those files into a folder named `models/` right inside the main directory.

---

## 💻 How to Use It

Once installed, you can use the `hierdetect` command from anywhere in your terminal!

**Run a quick health check:**
Make sure everything is loaded properly by testing it on a built-in safe script and a built-in malicious script.

```bash
hierdetect --check --model-dir ./models

```

**Scan a suspicious file:**
Let the AI decide if it should just use Stage 1, or escalate to Stages 2 and 3.

```bash
hierdetect --script path/to/suspicious.ps1 --model-dir ./models

```

**Force a "Deep Scan":**
Want to skip the bouncer and send a script straight to the heavy-duty detectives? Use the `-F` (Full Pipeline) flag.

```bash
hierdetect --script path/to/suspicious.ps1 -F --model-dir ./models

```

**Interactive Mode:**
If you have a lot of scripts to test and don't want to wait for the AI to load every single time, use Interactive Mode! It loads the AI into memory once and gives you a prompt to test as many scripts as you want.

```bash
hierdetect --interactive --model-dir ./models

```

---

## 🔬 For Researchers (Reproducing our work)

If you are an academic peer or researcher reviewing our paper, welcome!

You can find the exact code we used to train these models in the `notebooks/` directory. The Jupyter notebooks are numbered sequentially from `01` to `10` so you can follow our exact workflow from raw data collection all the way to final evaluation.

## 📝 Citation

If this tool or our cross-modal fusion research helps you in your own work, please consider citing us! You can find the exact citation details by clicking the **"Cite this repository"** button on the right side of our GitHub page.

```