from pathlib import Path

from setuptools import setup

here = Path(__file__).parent

about = {}
about_path = here / 'comment' / '__version__.py'
exec(about_path.read_text(), about)  # nosec # nosemgrep

requires = [
    'aiofiles',
    'alembic',
    'arrow',
    'colorlog',
    'fastapi',
    'mysqlclient',
    'passlib[argon2]',
    'pydantic[email]',
    'python-dotenv',
    'python-jose[cryptography]',
    'requests',
    'sqlalchemy',
    'sqlalchemy-utils',
    'uvicorn[standard]',
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
        'https://github.com/recruitment-cn/recruitment-dev-python-backend-comments-tree-homework-TaotaoLiu'  # noqa:E501
    ),
    setup_requires=['setuptools>=38.6.0'],
    python_requires='>=3.9.5',
    packages=['comment'],
    zip_safe=False,
    install_requires=requires,
    tests_require=tests_require,
)
