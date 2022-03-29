import os
from setuptools import setup, Distribution

VERSION = open('VERSION').read().strip()
LONG_DESCRIPTION = open('README.md').read()


class BinaryDistribution(Distribution):
    """Distribution which enables a binary package with platform name

    Will build `none-any` wheels by default, e.g. -

        hera_workflows-1.8.0-py3-none-any.whl

    If the env var ENABLE_BDIST_EXT_MODULE=yes is defined built wheel will have platform and
    python version info, e.g. -
    Used to create wheels for specific OS and Python version, e.g. -

        hera_workflows-1.8.0-cp37-cp37m-macosx_10_9_x86_64.whl
    """
    def has_ext_modules(self):
        return os.environ.get('ENABLE_BDIST_EXT_MODULE') == 'yes'


setup(
    name='hera-workflows',
    version=VERSION,
    description='Hera is a Python framework for constructing and submitting Argo Workflows. The main goal of Hera is '
                'to make Argo Workflows more accessible by abstracting away some setup that is typically necessary '
                'for constructing Argo workflows.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/argoproj-labs/hera-workflows",
    project_urls={
        "Bug Tracker": "https://github.com/argoproj-labs/hera-workflows/issues",
    },
    author="Flaviu Vadan",
    author_email="flaviu.vadan@dynotx.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["hera"],
    package_dir={'': 'src'},
    package_data={
        'hera': ['py.typed'],
    },
    data_files=[('', ['VERSION', 'README.md', 'CHANGELOG.md', 'LICENSE'])],
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        "argo-workflows==6.3.0rc2",
        "pydantic",
        "python-dateutil",
        "urllib3",
        "certifi",
        "pytz"
    ],
    zip_safe=False,
    distclass=BinaryDistribution
)

