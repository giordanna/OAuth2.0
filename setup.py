from setuptools import setup

setup(
    name="catalogo",
    author="Giordanna De Gregoriis",
    author_email="gior.grs@gmail.com",
    url="https://github.com/giordanna/projeto-catalogo",
    packages=["catalogo"],
    include_package_data=True,
    install_requires=[
        "flask"
    ],
)