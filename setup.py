from setuptools import setup, find_packages

setup(author="CCG, Murdoch University",
      author_email="info@ccg.murdoch.edu.au",
      description="Export CKAN data to a flat filesystem structure",
      license="GPL3",
      keywords="",
      url="https://github.com/muccg/bpa-ckan-export",
      name="bpackanexport",
      version="0.1.0",
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      entry_points={
          'console_scripts': [
              'bpa-ckan-export=bpackanexport.cli:main',
          ],
      })
