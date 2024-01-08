from setuptools import find_packages, setup


setup(
    name='anyaclient',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "anyaclient = anyaclient.client:main",
        ]
    },
    url='',
    license='',
    author='',
    author_email='',
    description=''
)
