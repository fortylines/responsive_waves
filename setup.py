from distutils.core import setup
import responsive_waves

setup(
    name='responsive_waves',
    version=responsive_waves.__version__,
    author='Fortylines LLC',
    author_email='support@fortylines.com',
    packages=['responsive_waves',
              'responsive_waves.urls',
              'responsive_waves.backends',
              'responsive_waves.templatetags',
              ],
    package_data={'responsive_waves': [
            'static/css/*',
            'static/img/*',
            'static/js/*',
            'static/vendor/css/*',
            'static/vendor/img/*',
            'static/vendor/js/*',
            'templates/responsive_waves/*.html']},
    url='https://github.com/fortylines/responsive_waves/',
    license='BSD',
    description="Browse HDL simulation traces using the responsive web",
    long_description=open('README.md').read(),
)
