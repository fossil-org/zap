from setuptools import setup, find_packages

def read_long_description():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

setup(
    name='zap',
    version='1',
    author='dae',
    author_email='pixilreal@gmail.com',
    description='advanced version control with integrated gh compatibility.',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    install_requires=["rich", "colorama"],
    entry_points={
        'console_scripts': [
            'zap=zap.src.handle:entrypoint'
        ]
    },
)
