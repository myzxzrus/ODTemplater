from setuptools import setup, find_packages

setup(name='odtemplater',
      version='0.0.1',
      description='ODT file template engine',
      packages=['odtemplater', 'odtemplater.config', 'odtemplater.lib', 'odtemplater.odtapplysettings'],
      author_email='myzxzrus@gmail.com',
      zip_safe=False,
      install_requires=['Pillow>=8.0.1'])
