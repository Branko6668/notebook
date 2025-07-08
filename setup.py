from setuptools import setup, find_packages

setup(
    name="personal-notebook",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==2.2.0',
        'PyMySQL==0.9.3',
        'passlib==1.7.4',
        'WTForms==2.2.1',
        'markdown2==2.4.12',
        'PyInstaller>=5.7.0',
    ],
    entry_points={
        'console_scripts': [
            'notebook=app:main',
        ],
    },
    python_requires='>=3.7',
) 