# setup.py
from setuptools import setup, find_packages

setup(
    name='wg-easy-api-wrapper',
    version='1.0.0',
    author='Your Name',
    author_email='a@kadorkin.io',
    description='A CLI tool for managing WireGuard clients via WG-Easy API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/akadorkin/wg-easy-api-wrapper',
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.8.1',
        'python-dotenv>=0.19.2',
        'cairosvg>=2.5.2'
    ],
    entry_points={
        'console_scripts': [
            'wg-cli=cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Change if using a different license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
