from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="lincore",
    version="0.1.0",
    author="Sahil Khutey",
    author_email="sahilkhutey@example.com",
    description="A Mission-Grade Solar Sail Simulation Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SahilKhutey/-Solar-Sail-Mission-Simulation-SSMS-",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "solar-sail=run_mission:main",
        ],
    },
)
