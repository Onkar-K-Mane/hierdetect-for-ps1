from setuptools import setup, find_packages

setup(
    name="hierdetect",
    version="1.0.0",
    description="Hierarchical PowerShell & LotL Detection Tool",
    author="Onkar K. Mane",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        # This ensures your PowerShell script gets bundled with the python code
        "hierdetect.extractors": ["*.ps1"],
    },
    entry_points={
        "console_scripts": [
            "hierdetect=hierdetect.cli:main",
        ],
    },
)