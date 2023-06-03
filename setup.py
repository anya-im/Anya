from setuptools import find_packages, setup


def _requires_from_file():
    return open("requirements.txt").read().splitlines()


setup(
    name='anya',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=_requires_from_file(),
    entry_points={
        "console_scripts": [
            "anya = anya.server:main",
        ]
    },
    url='',
    license='',
    author='',
    author_email='',
    description=''
)
