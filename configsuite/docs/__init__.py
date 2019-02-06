"""Copyright 2019 Equinor ASA and The Netherlands Organisation for
Applied Scientific Research TNO.

Licensed under the MIT license.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the conditions stated in the LICENSE file in the project root for
details.

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.
"""


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


def generate(schema, level=0):
    indent = level*4*" "
    element_sep = "\n\n"

    docs = [
        indent + schema.get(MK.Description, ""),
    ]

    elem_vals = schema.get(MK.ElementValidators, ())
    if len(elem_vals) > 0:
        try:
            docs += [
                indent + ":requirement: {}".format(
                    ", ".join([elem_val.msg for elem_val in elem_vals])
                )
            ]
        except AttributeError:
            raise Exception(elem_vals[0].__name__)

    if schema[MK.Type] == types.NamedDict:
        req_child_marker = lambda key: (
            "*" if schema[MK.Content][key].get(MK.Required, True) else ""
        )

        docs += [
            "\n".join((
                indent + "**{key}{req}:**".format(
                    key=key,
                    req=req_child_marker(key)
                    ),
                generate(value, level=level+1)
            ))
            for key, value in schema[MK.Content].items()
        ]
    elif schema[MK.Type] == types.List:
        docs += [
            "\n".join([
                indent + "**<list_item>:**",
                generate(schema[MK.Content][MK.Item], level=level+2),
            ])
        ]
    elif schema[MK.Type] == types.Dict:
        docs += [
            "\n".join([
                indent + "**<key>:**",
                generate(schema[MK.Content][MK.Key], level=level+2),
                indent + "**<value>:**",
                generate(schema[MK.Content][MK.Value], level=level+2),
            ])
        ]
    elif isinstance(schema[MK.Type], types.BasicType):
        docs += [
            indent + ":type: {_type}".format(_type=schema[MK.Type].name)
        ]
    else:
        err_msg = "Unexpected type ({}) in schema while generating documentation."
        raise TypeError(err_msg.format(schema[MK.Type]))

    return element_sep.join(docs)


def _generate_main_page(main_page, project_name, schema):
    doc_body = generate(schema)
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
    @configsuite.validator_msg("Score should be non-negative")
    def _non_negative_score(elem):
        return elem > 0

    schema = {
        MK.Type: types.NamedDict,
        MK.Description: (
            "The PetMeet configuration is to give an overview of you and your "
            "pet to better be able to find a matching pet owner."
        ),
        MK.Content: {
            'name': {
                MK.Type: types.String,
                MK.Description: "Your full name.",
            },
            'pet': {
                MK.Type: types.NamedDict,
                MK.Description: "Information about your pet.",
                MK.Content: {
                    'name': {
                        MK.Type: types.String,
                        MK.Description: "Name of the pet.",
                    },
                    'favourite_food': {
                        MK.Type: types.String,
                        MK.Description: "Favourite food of the pet.",
                    },
                    'weight': {
                        MK.Type: types.Number,
                        MK.Description: "Weight of pet in tons.",
                    },
                    'nkids': {
                        MK.Type: types.Integer,
                        MK.Description: "Number of kids.",
                    },
                    'likeable': {
                        MK.Type: types.Bool,
                        MK.Description: "Is the pet likeable?",
                    },
                },
            },
            'playgrounds': {
                MK.Type: types.List,
                MK.Description: "List of all playgrounds you take your pet to.",
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Description: "Information about a playground.",
                        MK.Content: {
                            'name': {
                                MK.Type: types.String,
                                MK.Description: "Name of the playground.",
                            },
                            'score': {
                                MK.Type: types.Integer,
                                MK.Description: "Your score for the playground.",
                            },
                        },
                    },
                },
            },
            'veterinary_scores': {
                MK.Type: types.Dict,
                MK.Description: (
                    "List of all veterinaries you have taken your pet to. "
                ),
                MK.Content: {
                    MK.Key: {
                        MK.Type: types.String,
                        MK.Description: "Name of the veterinary.",
                    },
                    MK.Value: {
                        MK.ElementValidators: (_non_negative_score,),
                        MK.Type: types.Number,
                        MK.Description: "Your score of the vet.",
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
