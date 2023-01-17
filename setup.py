from setuptools import setup, find_packages


setup_args = dict(
    name='weatheril',
    version='1.0.0',
    description='Israel Meteorological Service unofficial python api wrapper',
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    author='Tomer Klein',
    author_email='tomer.klein@gmail.com',
    keywords=['ims', 'weatheril', 'Israel Meteorological Service','Meteorological Service','weather'],
    url='https://github.com/t0mer/py-weatheril',
    download_url='https://pypi.org/project/weatheril/'
)

install_requires = [
    'Pillow',
    'pandas',
    'requests',
    'urllib3'
    
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)