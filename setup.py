from setuptools import setup

setup(
    name='sphinxcontrib-yaml',
    url='https://github.com/Rayvenden/sphinxcontrib-yaml',
    author='Jakub Pieńkowski',
    author_email='jakski@sealcode.org',
    license='MIT',
    description='Sphinx autodoc extension to generate docs from YAML comments',
    platforms='any',
    version='1.0.0',
    py_modules=['sphinxcontrib_yaml'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Documentation'
    ],
    install_requires=[
        'Sphinx',
    ]
)
