from os.path import join
from setuptools import setup, find_packages, Extension, Feature

version = '3.0'

base = join('experimental', 'catalogqueryplan')

codeoptimization = Feature("Optional code optimizations",
    standard=True,
      ext_modules=[
        Extension(
          name='experimental.catalogqueryplan.difference',
          sources=[join(base, 'difference.c')]
        ),
        Extension(
          name='experimental.catalogqueryplan.intersection',
          sources=[join(base, 'intersection.c')],
        ),
      ],
)

setup(name='experimental.catalogqueryplan',
      version=version,
      description="Static query optimized with one plan",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone catalog search',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      features = {'codeoptimization': codeoptimization},
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
