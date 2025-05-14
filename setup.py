from setuptools import setup

setup(
    name="fleck",
    version="0.1",
    packages=["fleck"],
    install_requires=[
        'appdirs==1.4.4',
        'click==8.1.8',
        'colorama==0.4.6',     # For Windows terminal colors
        'GitPython==3.1.44',
        'psutil==7.0.0',
        'PyGetWindow==0.0.9',
        'PyRect==0.2.0',
        'pywin32==310',        # Only needed if you're doing Windows-specific automation
        'rich==14.0.0'
    ],
    entry_points={
        "console_scripts": [
            "fleck = fleck.cli_new_1:cli",
            # "fleck = fleck.cli:cli",
        ],
    },
)