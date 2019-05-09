# Config Suite #

[![Build Status](https://travis-ci.org/equinor/configsuite.svg?branch=master)](https://travis-ci.org/equinor/configsuite)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

## Introduction ##
_Config Suite_ is the result of recognizing the complexity of software configuration, both from a user and developer perspective. And our main goal is to be transparent about this complexity. In particular we aim at providing the user with confirmation when a valid configuration is given, concrete assistance when the configuration is not valid and up-to-date documentation to assist in this work. For a developer we aim at providing a suite that will handle configuration validity with multiple sources of data in a seamless manner, completely remove the burden of special casing and validity checking and automatically generate documentation that is up to date. We also believe that dealing with the complexity of formally verifying a configuration early in development leads to a better design of your configuration.

## Features ##
- Validate configurations.
- Provide an extensive list of errors when applicable.
- Output a single immutable configuration object where all values are provided.
- Support for multiple data sources, yielding the possibility of default values as well as user and workspace configurations on top of the current configuration.
- Generating documentation that adheres to the technical requirements.
- No exceptions are thrown based on user-input (this is currently not true for
  validatiors).

## Future ##
Have a look at the epics and issues in the _GitHub_ (repository)[https://github.com/equinor/configsuite/issues].

## Installation ##
The simplest way to fetch the newest version of _Config Suite_ is via [PyPI](https://pypi.python.org/pypi/configsuite/).

`pip install configsuite`

## Developer guidelines ##
Contributions to _Config Suite_ is very much welcome! Bug reports, feature requests and improvements to the documentation or code alike. However, if you are planning a bigger chunk of work or to introduce a concept, initiating a discussion in an issue is encouraged.

#### Running the tests ####
The tests can be executed with `python setup.py test`. Note that the code formatting tests will only be executed with Python `3.6` or higher.

#### Code formatting ####
The entire code base is formatted with [black](https://black.readthedocs.io/en/stable/).

#### Pull request expectations ####
We expect a well-written explanation for smaller PR's and a reference to an issue for larger contributions. In addition, we expect the tests to pass on all commits and the commit messages to be written in imperative style. For more on commit messages read [this](https://chris.beams.io/posts/git-commit/).

## Documentation ##

### A first glance ###
For now we will just assume that we have a schema that describes the expected
input. Informally say that we have a very simple configuration where one can
specify ones name and hobby, i.e:

```yaml
name: Espen Askeladd
hobby: collecting stuff
```

You can then instantiate a suite as follows:

```python
import configsuite

with open('config.yml') as f:
    input_config = yaml.load(f)

suite = configsuite.ConfigSuite(input_config, schema)
```

You can now check whether data provided in `input_config` is valid by accessing
`suite.valid`.

```python
if suite.valid:
    print("Congratulations! The config is valid.")
else:
    print("Sorry, the configuration is invalid.")
```

Now, given that the configuration is indeed valid you would probably like to
access the data. This can be done via the `ConfigSuite` member named
`snapshot`. Hence, we could change our example above to:

```python
if suite.valid:
    msg = "Congratulations {name}! The config is valid. Go {hobby}."
    print(msg.format(name=suite.snapshot.name, hobby=suite.snapshot.hobby))
else:
    print("Sorry, the configuration is invalid.")
```

And if feed the example configuration above the output would be:

```
Congratulations Espen Askelad! The config is valid. Go collect stuff.
```

However, if we changed the value of `name` to `13` (or even worse `[My, name, is kind, of odd]`) we would expect the configuration to be invalid and hence that the output would be `Sorry, the configuration is invalid`. And as useful as this is it would be even better to gain more detailed information about the errors.

```
print(suite.errors)
(InvalidTypeError(msg=Is x a string is false on input 13, key_path=('hobby',), layer=None),)
```

```python
if suite.valid:
    msg = "Congratulations {name}! The config is valid. Go {hobby}."
    print(msg.format(name=suite.snapshot.name, hobby=suite.snapshot.hobby))
else:
    print("Sorry, the configuration is invalid.")
```

#### A first schema ####

The below schema is indeed the one used in our example above. It consists of a
single collection containing the two keys `name` and `hobby`, both of which
value should be a string.

```python
from configsuite import types
from configsuite import MetaKeys as MK

schema = {
    MK.Type: types.NamedDict,
    MK.Content: {
        "name": {MK.Type: types.String},
        "hobby": {MK.Type: types.String},
    }
}
```

Notice the usage of the meta key `Type` to specify the type of a specific
element and the usage of `Content` to specify the content of a container.

#### Configuration readiness ####
A very central concept in _configsuite_ is that of configuration readiness.
Given that our configuration is indeed valid we can trust that `suite.snapshot`
will describe all values as defined in the schema and that all the values are
valid. Hence, we do not need to check for availability nor correctness of the
configuration.

### Types ###
In _configsuite_ we differentiate between `basic types` and `collections`.
Basic types are single valued entities, while collections are data structures
that can hold multiple basic types. In our first example the entire
configuration was considered a collection (of type `Named dict`), while `name`
and `hobby` are basic types. And while you can define arbitrary `basic types`,
one cannot create new `collections` while using _Config Suite_.

#### Basic types ####

##### String #####
We have already seen the usage of the `String` type above. It basically accepts
everything considered a string in Python (defined by `six.string_types`).

##### Integer #####
An `Integer` is as the name suggests an integer.

##### Number #####
When a `Number` is specified any integer or floating point value is accepted.

##### Bool #####
Both boolean values `True` and `False` are accepted.

##### Date #####
A date in specified in ISO-format, `[YYYY]-[MM]-[DD]` that is.

##### DateTime #####
A date and time is expected in ISO-format (`[YYYY]-[MM]-[DD]T[hh]:[mm]:[ss]`).

#### Collections ####

##### Named dict #####
We have already seen the usage of a `Named dict`. In particular, it allows for
mapping values (of potentially different types) to names that we know up front.
This allows us to represent them as attributes of the snapshot (or an sub
element of the snapshot). In general, if you know the values of all of the keys
up front, then a named dict is the right container for you.

```python
from configsuite import types
from configsuite import MetaKeys as MK

schema = {
    MK.Type: types.NamedDict,
    MK.Content: {
        "owner": {
            MK.type: types.NamedDict,
            MK.Content: {
                "name": {MK.type: types.String},
                "credit": {MK.type: types.Integer},
                "insured": {MK.type: types.Bool},
            },
        },
        "car": {
            MK.Type: types.NamedDict,
            MK.Content: {
                "brand": {MK.type: types.String},
                "first_registered": {MK.Type: types.Date}
            },
        },
    },
}
```

the above example describes a configuration describing both an `owner` and a
`car`. for the `owner` the `name`, `credit` and whether she is `insured` is to
be specified, while for the `car` the `brand` and date it was
`first_registered` is specified. a valid configuration could look something
like this:

```yaml
owner:
  name: Donald Duck
  credit: -1000
  insured: true

car:
  brand: Belchfire Runabout
  first_registered: 1938-07-01
```

and now, we could validate and access the data as follows:

```python
# ... configuration is loaded into 'input_config' ...

suite = configsuite.ConfigSuite(input_config, schema)

if suite.valid:
    print("name of owner is {}".format(suite.snapshot.owner.name))
    print("car was first registered {}".format(suite.snapshot.car.first_registered))
```

Notice that since keys in a named dict are made attributes in the snapshot,
they all have to be valid Python variable names.

##### List #####
Another supported container is the `List`. The data should be bundled together
either in a Python `list` or a `tuple`. A very concrete difference of a Config
Suite list and a Python list is that in Config Suite all elements are expected
to be of the same type. This makes for an easier format for the user as well as
the programmer when one is dealing with configurations. A very simple example
representing a list of integers would be as follows:

```python
import configsuite
from configsuite import types
from configsuite import MetaKeys as MK

schema = {
    MK.Types: types.List,
    MK.Content: {
        MK.Item: {
            MK.Type: types.Integer,
        },
    },
}

config = [1, 1, 2, 3, 5, 7, 13]

suite = configsuite.ConfigSuite(config, schema)

if suite.valid:
    for idx, value in enumerate(suite.snapshot):
        print("config[{}] is {}".format(idx, value))
```

A more complex example can be made by considering our example from the
`NamedDict` section and imagining that an `owner` could have multiple `cars`
that was to be contained in a list.

```python
from configsuite import types
from configsuite import MetaKeys as MK

schema = {
    MK.Type: types.NamedDict,
    MK.Content: {
        "owner": {
            MK.type: types.NamedDict,
            MK.Content: {
                "name": {MK.type: types.String},
                "credit": {MK.type: types.Integer},
                "insured": {MK.type: types.Bool},
            },
        },
        "cars": {
            MK.Type: types.List,
            MK.Content: {
                MK.Item: {
                    MK.Type: types.NamedDict,
                    MK.Content: {
                        "brand": {MK.type: types.String},
                        "first_registered": {MK.Type: types.Date}
                    },
                },
            },
        },
    },
}

config = {
    "owner": {
      "name": Donald Duck,
      "credit": -1000,
      "insured": True,
    },
    "cars": [
        {
          "brand": "Belchfire Runabout",
          "first_registered": datetime.Date(1938, 7, 1),
        },
        {
          "brand": "Duckworth",
          "first_registered": datetime.Date(1987, 9, 18),
        },
    ]
}

suite = configsuite.ConfigSuite(config, schema)

if suite.valid:
    print("name of owner is {}".format(suite.snapshot.owner.name))
    for car in suite.snapshot.cars:
        print("- {}".format(car.brand))
```

Notice that `suite.snapshot.cars` is returned as a `tuple`-like structure. It
is iterable, indexable (`suite.snapshot.cars[0]`) and immutable.

##### Dict #####
The last of the data structures is the `Dict`. Contrary to the `NamedDict` one
does not need to know the keys upfront and in addition the keys can be of other
types than just `strings`. However, the restriction is that all the keys needs
to be of the same type and all the values needs to be of the same type. The
rationale for this is similar to that one of the list. Uniform types for
arbitrary sized configurations are easier and better, both for the user and the
programmer. A simple example mapping animals to frequencies are displayed below.

```python
import configsuite
from configsuite import types
from configsuite import MetaKeys as MK

schema = {
    MK.Type: types.Dict,
    MK.Content: {
        MK.Key: {MK.Type: types.String},
        MK.Value: {MK.Type: types.Integer},
    },
}

config = {
    "monkey": 13,
    "donkey": 16,
    "horse": 28,
}

suite = configsuite.ConfigSuite(config, schema)
assert suite.valid:

for animal, frequency in suite.snapshot:
    print("{} was observed {} times".format(animal, frequency))
```

As you can see, the elements of a `Dict` is accessible in `(key, value)` pairs
in the same manner `dict.items` would provide for a Python dictionary. The
reason for not supporting indexing by key is `Dict`, contrary to `NamedDict`,
is for dictionaries with an unknown set of keys. Hence, processing them as
key-value-pairs is the only rational thing to do.

#### Readable ####
Recall the concept of configuration readiness from earlier. This meant that if
one specified a value in the schema, one is to expect that that piece of data
is indeed present in the snapshot. But what if the configuration feed to the
suite is not valid? If the errors appear in basic types, one can still access
all the data as expected (i.e. `config.snapshot.owner.name` from the car
example above).  However, if a container is of the wrong type on cannot
guarantee such a thing.  In particular, if we bring back the single-car example
from above and consider the following configuration:

```yaml
owner:
  name: Donald Duck
  credit: -1000
  insured: true

car:
  - my first car
  - my second car
```

The `car` data is completely off and there is no way one could provide a
reasonable value for `config.snapshor.car.brand`. In such scenarios the
configuration is deemed _unreadable_. There is a special marker for this,
namely `ConfigSuite.readable`. If `readable` is true, then the snapshot can be
built and all the entire configuration can be accessed. However, if the suite
is not `readable` and one tries to fetch the snapshot an `AssertionError` will
be raised.

Note that all valid suites also are readable. And that all unreadable suites
also are invalid.

#### Required values ####
So far all entries in your configuration file have been mandatory to fill in.
And if some key in a Named dict would be missing a `MissingKeyError` would be
registered. However, this is not always the wanted behaviour. By using the
`MetaKeys.Required` option you can control whether a key is indeed required.
You could change the `cars` schema above such that `credit` would be optional
as follows:

```python
from configsuite import types
from configsuite import MetaKeys as MK

schema = {
    MK.Type: types.NamedDict,
    MK.Content: {
        "owner": {
            MK.type: types.NamedDict,
            MK.Content: {
                "name": {MK.Type: types.String},
                "credit": {
                    MK.Type: types.Integer,
                    MK.Required: False,
                },
                "insured": {MK.Type: types.Bool},
            },
        },
        "cars": {
            MK.Type: types.List,
            MK.Content: {
                MK.Item: {
                    MK.Type: types.NamedDict,
                    MK.Content: {
                        "brand": {MK.Type: types.String},
                        "first_registered": {MK.Type: types.Date}
                    },
                },
            },
        },
    },
}
```

And then if no `credit` was specified a `MissingKeyError` would not be
registered. However, recall the principle of configuration readiness. Since,
the programmer should not have to special case whether or not the value is
present in the `snapshot`. The `snapshot` is always built based on the schema
and hence `suite.snapshot.owner.credit` would indeed be an attribute
independently of whether the user has configured it. In this scenario the value
of `suite.snapshot.owner.credit` would be `None`. To configure the default
value to something else then `None`, we refer the reader to the next section.

#### Default values ####
We have planned two ways of providing default values in Config Suite. You are
to either specify it in the schema via the keyword `MetaKeys.Default` (NOTE:
This is yet to be implemented!). This has the advantage of being able to provide default
values inside list-elements. The disadvantage is that you would need to edit
the code to change the default values and hence site or project specific
defaults are not suited for this purpose. The second, and currently only
implemented, way of specifying default are via `layers`.

Note that no element should be both required and have a given `Default` value.

#### Layers ####
TODO

#### Validators ####
##### Element validators #####
TODO

##### Context validators #####
TODO

#### Creating your own types ####
TODO

#### Transformations ####
##### Transformations #####
TODO

##### Context transformations #####
TODO

##### Layer transformations #####
TODO

#### Documentation generation ####
TODO
