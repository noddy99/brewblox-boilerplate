from setuptools import find_packages, setup

setup(
    name='brewblox-ispindel',
    version='0.2.0',
    long_description=open('README.md').read(),
    url='https://github.com/bdelbosc/brewblox-ispindel',
    author='Benoit Delbosc',
    author_email='bdelbosc@free.fr',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: End Users/Desktop',
        'Topic :: System :: Hardware',
    ],
    keywords='brewing brewpi brewblox embedded plugin service ispindel hydrometer',
    packages=find_packages(exclude=['test', 'docker']),
    install_requires=[
        'brewblox-service'
    ],
    python_requires='>=3.7',
    extras_require={'dev': ['pipenv']}
)
