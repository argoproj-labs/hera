from setuptools import find_namespace_packages, setup

VERSION = open('VERSION').read().strip()
LONG_DESCRIPTION = open('README.md').read()

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
        "argo-workflows",
        "pydantic",
        "python-dateutil",
        "urllib3",
        "certifi"
    ],
    zip_safe=False
)

