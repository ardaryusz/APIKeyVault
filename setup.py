from setuptools import setup

setup(
    name='keyvault',
    version='1.0',
    py_modules=['keyvault'],
    install_requires=[
        'cryptography',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'keyvault=keyvault:main',
        ],
    },
)