from setuptools import setup, find_packages
from os import path


# extract version
path = path.realpath("raman_control/_version.py")
version_ns = {}
with open(path, encoding="utf8") as f:
    exec(f.read(), {}, version_ns)
version = version_ns["__version__"]

setup(
    name="raman_control",
    version=version,
    packages=find_packages(),
    install_requires=[
        "ipywidgets>=7.5.0,<8",
        "matplotlib",
        "ipympl>=0.5.7",
        "packaging",
        "mpl-interactions>=0.6.0",
        "nidaqmx",
        "pythonnet",
    ],
    author="Ian Hunt-Isaak",
    author_email="ianhuntisaak@gmail.com",
    license="BSD",
    # platforms="Linux, Mac OS X, Windows", # i think if I restrict to windows here i won't be able to test on my laptop
    description="highly automated system to poke yeast with half million dollar lasers",
    # keywords=["Jupyter", "Widgets", "IPython", "Matplotlib"],
    # classifiers=[
    #     "Intended Audience :: Developers",
    #     "Intended Audience :: Science/Research",
    #     "License :: OSI Approved :: BSD License",
    #     "Programming Language :: Python",
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3.4",
    #     "Programming Language :: Python :: 3.5",
    #     "Programming Language :: Python :: 3.6",
    #     "Programming Language :: Python :: 3.7",
    #     "Framework :: Jupyter",
    #     "Framework :: Matplotlib",
    # ],
    # url="https://github.com/ianhi/mpl-interactions",
    extras_require={
        "dev": [
            "black",
        ],
    },
)