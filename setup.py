from setuptools import setup, find_packages

setup(
    name="Ursus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "mistune",
        "klembord"
    ],
    entry_points={
        'console_scripts': [
            'ursus = ursus.__main__:main'
        ]
    },
    include_package_data=True,
    package_data={"": ["resources/*.ttf", "resources/*.png"]},
    author="Claude Henchoz",
    author_email="claude.henchoz@gmail.com",
    description="A *very* minimalist markdown editor",
    keywords="markdown editor pyside6",
    url="http://henchoz.net/ursus",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Desktop Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Text Editors"
    ]
)
