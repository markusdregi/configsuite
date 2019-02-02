import configsuite
import subprocess
import os

from configsuite import MetaKeys as MK
from configsuite import types


class chdir(object):
    def __init__(self, path):
        self._old_path = os.getcwd()
        self._path = path

    def __enter__(self):
        os.chdir(self._path)

    def __exit__(self, _type, value, traceback):
        os.chdir(self._old_path)


_MAIN_TEMPLATE = """
Welcome to {project_name}'s documentation!
========================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

{doc_body}

"""

def _init_docs(build_dir, project_name, author, release):
    cmd_fmt = (
        "sphinx-quickstart {build_dir} --sep --dot=. "
        "--project='{project_name}' --author='{author}' --release='{release}' "
        "--language=en --suffix=.rst --master=index --ext-doctest --makefile "
        "--use-make-mode --no-batchfile"
    )
    subprocess.check_output(
        cmd_fmt.format(
            build_dir=build_dir,
            project_name=project_name,
            author=author,
            release=release,
        ),
        shell=True,
    )


def doc_builder(schema, level=0):
    indent = level*4*" "
    if schema[MK.Type] == types.NamedDict:
        return "\n\n".join([
            "\n".join((
                indent + "**{key}:**".format(key=key),
                doc_builder(value, level=level+1)
            ))
            for key, value in schema[MK.Content].items()
        ])
    else:
        return (
            indent +
            ":type: {_type}".format(_type=schema[MK.Type].name)
        )


def _generate_main_page(main_page, project_name, schema):
    doc_body = doc_builder(schema)
    with open(main_page, 'w') as f:
        f.write(_MAIN_TEMPLATE.format(
            project_name=project_name,
            doc_body=doc_body,
            )
        )


def make_docs(build_dir, project_name, author, release, schema):
    _init_docs(build_dir, project_name, author, release)

    main_page = os.path.join(build_dir, 'source', 'index.rst')
    _generate_main_page(main_page, project_name, schema)


def _build(build_dir, build_type):
    with chdir(build_dir):
        subprocess.check_output(
            "make {build_type}".format(build_type=build_type),
            shell=True,
        )


def build_html(build_dir):
    _build(build_dir, 'html')


def build_man(build_dir):
    _build(build_dir, 'man')


if __name__ == '__main__':
    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            'name': {
                MK.Type: types.String,
                MK.Description: (
                    "This is a very long line "
                    "that at some point should be broken into multiple "
                    "lines. Hoping that this would work..."
                ),
            },
            'pet': {
                MK.Type: types.NamedDict,
                MK.Content: {
                    'name': {
                        MK.Type: types.String,
                    },
                    'favourite_food': {
                        MK.Type: types.String,
                    },
                    'weight': {
                        MK.Type: types.Number,
                    },
                    'nkids': {
                        MK.Type: types.Integer,
                    },
                    'likeable': {
                        MK.Type: types.Bool,
                    },
                },
            },
            'playgrounds': {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            'name': {
                                MK.Type: types.String,
                            },
                            'score': {
                                MK.Type: types.Integer,
                            },
                        },
                    },
                },
            },
            'veterinary_scores': {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: { MK.Type: types.String },
                    MK.Value: {
                        MK.Type: types.Number,
                    },
                },
            },
        },
    }

    build_dir = os.path.realpath('docs')
    make_docs(
            build_dir,
            'configsuite',
            'Software Innovation Bergen, Equinor & TNO',
            configsuite.__version__,
            schema,
            )
    build_html(build_dir)
    build_man(build_dir)
