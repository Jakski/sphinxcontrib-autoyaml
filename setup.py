from setuptools import setup

setup(
    name='sphinxcontrib-autoyaml',
    url='https://github.com/Rayvenden/sphinxcontrib-autoyaml',
    author='Jakub Pieńkowski',
    author_email='jakski@sealcode.org',
    license='MIT',
    description='Sphinx extension to generate docs from YAML comments',
    platforms='any',
    version='0.2.0',
    py_modules=['sphinxcontrib_autoyaml'],
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
