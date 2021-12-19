from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.1.1"
DESCRIPTION = "Perspective label tool for railways"
LONG_DESCRIPTION = (
    "A package that allows to annotate complex scenes on video images from railways."
)

# Setting up
setup(
    name="rail_label",
    version=VERSION,
    author="Florian Hofstetter",
    author_email="<flo.max.hofstetter@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "tabulate",
        "splines",
        "iteration-utilities",
        "PySimpleGUI",
    ],
    keywords=["python", "video", "railway", "rail", "train", "labeling", "pyyaml"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
