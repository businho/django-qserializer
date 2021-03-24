from setuptools import find_packages, setup

setup(
    packages=find_packages(),
    install_requires=[
        'django',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-django',
    ],
)
