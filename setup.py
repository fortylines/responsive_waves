# Copyright (c) 2012-2014, Fortylines LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
