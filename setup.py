from setuptools import find_namespace_packages, setup

VERSION = open('VERSION').read()
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

    packages=find_namespace_packages(include=['hera.*'], where="src"),
    package_dir={'': 'src'},
    package_data={
        'hera': ['py.typed'],
    },
    data_files=[('', ['VERSION', 'README.md', 'CHANGELOG.md', 'LICENSE'])],
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        "pydantic",
        "python-dateutil",
        "urllib3",
        "certifi"
    ],
    dependency_links=[
        # TODO: argo_workflows did not make it into a release that would have published an official
        # TODO: PyPi version. Once that happens, which is likely in 3.2+, this dependency can be changed safely
        # TODO: Also, move this to `install_requires`
        "git+https://github.com/argoproj/argo-workflows@master#subdirectory=sdks/python/client"
    ],
    zip_safe=False
)
