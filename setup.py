from setuptools import setup

with open('README.md') as f:
    long_description = f.read()


setup(
    name='Numkdoc',
    packages=['numkdoc'],
    version='0.4.1',
    license='MIT',

    description='Mkdoc plugin to autodoc your numpy docstring',
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!

    author='Thomas FEL',
    author_email='thomas.fel@protonmail.com',
    url='https://github.com/napolar/numkdoc',

    install_requires=['mkdocs', 'numpydoc'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    entry_points={
        'mkdocs.plugins': [
            'numkdoc = numkdoc:Numkdoc',
        ]
    },
)
