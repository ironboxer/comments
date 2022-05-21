from pathlib import Path

from setuptools import setup

here = Path(__file__).parent

about = {}
about_path = here / 'comment' / '__version__.py'
exec(about_path.read_text(), about)  # nosec # nosemgrep

requires = [
    'requests',
    'fastapi',
    'uvicorn[standard]',
    'pydantic[email]',
    'colorlog',
    'passlib[argon2]',
    'python-jose[cryptography]',
    'python-dotenv',
    'sqlalchemy',
    'sqlalchemy-utils',
    'alembic',
    'mysqlclient',
    'arrow',
]

tests_require = ['pytest']

setup(
    name='comment',
    version=about['__version__'],
    description='API for Comment System',
    long_description=(here / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    author='Liu Taotao',
    author_email='lttzzlll@gmail.com',
    url=(
        'https://github.com/ironboxer/'
        'recruitment-dev-python-backend-comments-tree-homework-TaotaoLiu'
    ),
    setup_requires=['setuptools>=38.6.0'],
    python_requires='==3.9.6',
    packages=['comment'],
    zip_safe=False,
    install_requires=requires,
    tests_require=tests_require,
)
