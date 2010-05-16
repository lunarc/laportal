from distutils.core import setup
from setuptools import find_packages

setup(
    name = "arcgui",
    version = "0.3.0",
    packages = find_packages("./lib"),
    url = "www.lunarc.lu.se",
    package_dir = { '':'lib'},
    scripts = ['./bin/arcgui'],
    
    data_files = [
        ('/usr/share/arcgui/images',
            [
                'share/arcgui/images/archive.png',
                'share/arcgui/images/ARClogo.png',
                'share/arcgui/images/document-new.png',
                'share/arcgui/images/download-all.png',
                'share/arcgui/images/download-job.png',
                'share/arcgui/images/edit-delete.png',
                'share/arcgui/images/edit-find.png',
                'share/arcgui/images/folder-open.png',
                'share/arcgui/images/gtk-edit.png',
                'share/arcgui/images/preview-xrsl.png',
                'share/arcgui/images/process-stop.png',
                'share/arcgui/images/system-run.png',
                'share/arcgui/images/view-refresh.png',
                'share/arcgui/images/LICENSE',
                'share/arcgui/images/README'
            ]
        )
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    #install_requires = ['docutils>=0.3'],

    # metadata for upload to PyPI
    author = "Jonas Lindemann",
    author_email = "jonas.lindemann@lunarc.lu.se",
    description = "ArcGui User interface",
    license = "Apache 2.0",
    keywords = "grid user interface arc"

    # could also include long_description, download_url, classifiers, etc.
)
