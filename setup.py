from setuptools import find_packages, setup

test_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-django',
    'pytest-flake8',
    'flake8<5',
]

setup(
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements,
    },
)
