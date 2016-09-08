from setuptools import setup, find_packages


with open('README.rst') as f:
    description = f.read()


classifiers = ["Development Status :: 5 - Production/Stable",
               "Programming Language :: Python",
               "Programming Language :: Python :: 2.7",
               "Programming Language :: Python :: 3.6"]

setup(name='l10n-migration',
      version="0.1",
      url='https://github.com/juliandescottes/devtools-l10n-migration',
      packages=find_packages(),
      long_description=description,
      description="Devtools l10n migration script",
      author="Julian Descottes",
      author_email=" jdescottes@mozilla.com",
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      entry_points="""
      [console_scripts]
      migrate-dtd = migrate.main:main
      """)
