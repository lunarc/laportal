from distutils.core import setup
from setuptools import find_packages

setup(
    name = "arcjobtool",
    version = "0.3.0",
    packages = find_packages("./lib"),
    url = "www.lunarc.lu.se",
    package_dir = { '':'lib'},
    scripts = ['./bin/arcjobtool', './bin/ui-cert-request'],
    
    data_files = [
        ('/usr/share/arcjobtool/images',
            [
                'share/arcjobtool/images/archive.png',
                'share/arcjobtool/images/ARClogo.png',
                'share/arcjobtool/images/document-new.png',
                'share/arcjobtool/images/download-all.png',
                'share/arcjobtool/images/download-job.png',
                'share/arcjobtool/images/edit-delete.png',
                'share/arcjobtool/images/edit-find.png',
                'share/arcjobtool/images/folder-open.png',
                'share/arcjobtool/images/gtk-edit.png',
                'share/arcjobtool/images/preview-xrsl.png',
                'share/arcjobtool/images/process-stop.png',
                'share/arcjobtool/images/system-run.png',
                'share/arcjobtool/images/kill-threads.png',
                'share/arcjobtool/images/view-refresh.png',
                'share/arcjobtool/images/LICENSE',
                'share/arcjobtool/images/README'
            ]
        )
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    #install_requires = ['docutils>=0.3'],

    # metadata for upload to PyPI
    author = "Jonas Lindemann",
    author_email = "jonas.lindemann@lunarc.lu.se",
    description = "ARC Job Submission Tool",
    license = "Apache 2.0",
    keywords = "grid user interface arc"

    # could also include long_description, download_url, classifiers, etc.
)
