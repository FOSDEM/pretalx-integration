import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="pretalx-auditlog",
    version="0.0.0",
    description="Log changes to pretalx models",
    long_description=long_description,
    url="GitHub repository URL",
    author="Johan Van de Wauw",
    author_email="johanvdw@fosdem.org",
    license="Apache Software License",
    install_requires=[],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretalx.plugin]
pretalx_auditlog=pretalx_auditlog:PretalxPluginMeta
""",
)
