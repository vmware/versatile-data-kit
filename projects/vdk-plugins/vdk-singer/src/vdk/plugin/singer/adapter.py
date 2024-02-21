# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

import pytz
import simplejson as json

# Due to conflicts with different versions of singer-python and taps and singer-python logger complexity
# it's better to adapt necessary singer classes here.
# Changes from original
# Logging is changed/removed
# For parsing dates we are using datetime.isofomat and fromisoformat instead singer custom solution

# These are standard keys defined in the JSON Schema spec
STANDARD_KEYS = [
    "selected",
    "inclusion",
    "description",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "maxLength",
    "minLength",
    "format",
    "type",
    "additionalProperties",
    "anyOf",
    "patternProperties",
]


class Schema:  # pylint: disable=too-many-instance-attributes
    """Object model for JSON Schema.

    Tap and Target authors may find this to be more convenient than
    working directly with JSON Schema data structures.

    """

    # pylint: disable=too-many-locals
    def __init__(
        self,
        type=None,
        format=None,
        properties=None,
        items=None,
        selected=None,
        inclusion=None,
        description=None,
        minimum=None,
        maximum=None,
        exclusiveMinimum=None,
        exclusiveMaximum=None,
        multipleOf=None,
        maxLength=None,
        minLength=None,
        additionalProperties=None,
        anyOf=None,
        patternProperties=None,
    ):
        self.type = type
        self.properties = properties
        self.items = items
        self.selected = selected
        self.inclusion = inclusion
        self.description = description
        self.minimum = minimum
        self.maximum = maximum
        self.exclusiveMinimum = exclusiveMinimum
        self.exclusiveMaximum = exclusiveMaximum
        self.multipleOf = multipleOf
        self.maxLength = maxLength
        self.minLength = minLength
        self.anyOf = anyOf
        self.format = format
        self.additionalProperties = additionalProperties
        self.patternProperties = patternProperties

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        pairs = [k + "=" + repr(v) for k, v in self.__dict__.items()]
        args = ", ".join(pairs)
        return "Schema(" + args + ")"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_dict(self):
        """Return the raw JSON Schema as a (possibly nested) dict."""
        result = {}

        if self.properties is not None:
            result["properties"] = {
                k: v.to_dict()
                for k, v in self.properties.items()  # pylint: disable=no-member
            }

        if self.items is not None:
            result["items"] = self.items.to_dict()  # pylint: disable=no-member

        for key in STANDARD_KEYS:
            if self.__dict__.get(key) is not None:
                result[key] = self.__dict__[key]

        return result

    @classmethod
    def from_dict(cls, data, **schema_defaults):
        """Initialize a Schema object based on the JSON Schema structure.

        :param schema_defaults: The default values to the Schema
        constructor."""
        kwargs = schema_defaults.copy()
        properties = data.get("properties")
        items = data.get("items")

        if properties is not None:
            kwargs["properties"] = {
                k: Schema.from_dict(v, **schema_defaults) for k, v in properties.items()
            }
        if items is not None:
            kwargs["items"] = Schema.from_dict(items, **schema_defaults)
        for key in STANDARD_KEYS:
            if key in data:
                kwargs[key] = data[key]
        return Schema(**kwargs)


class Message:
    """Base class for messages."""

    def asdict(self):  # pylint: disable=no-self-use
        raise Exception("Not implemented")

    def __eq__(self, other):
        return isinstance(other, Message) and self.asdict() == other.asdict()

    def __repr__(self):
        pairs = [f"{k}={v}" for k, v in self.asdict().items()]
        attrstr = ", ".join(pairs)
        return f"{self.__class__.__name__}({attrstr})"

    def __str__(self):
        return str(self.asdict())


class StateMessage(Message):
    """STATE message.

    The STATE message has one field:

      * value (dict) - The value of the state.

    msg = singer.StateMessage(
        value={'users': '2017-06-19T00:00:00'})

    """

    def __init__(self, value):
        self.value = value

    def asdict(self):
        return {"type": "STATE", "value": self.value}


class SchemaMessage(Message):
    """SCHEMA message.

    The SCHEMA message has these fields:

      * stream (string) - The name of the stream this schema describes.
      * schema (dict) - The JSON schema.
      * key_properties (list of strings) - List of primary key properties.

    msg = singer.SchemaMessage(
        stream='users',
        schema={'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'}
                }
               },
        key_properties=['id'])

    """

    def __init__(self, stream, schema, key_properties, bookmark_properties=None):
        self.stream = stream
        self.schema = schema
        self.key_properties = key_properties

        if isinstance(bookmark_properties, (str, bytes)):
            bookmark_properties = [bookmark_properties]
        if bookmark_properties and not isinstance(bookmark_properties, list):
            raise Exception("bookmark_properties must be a string or list of strings")

        self.bookmark_properties = bookmark_properties

    def asdict(self):
        result = {
            "type": "SCHEMA",
            "stream": self.stream,
            "schema": self.schema,
            "key_properties": self.key_properties,
        }
        if self.bookmark_properties:
            result["bookmark_properties"] = self.bookmark_properties
        return result


class RecordMessage(Message):
    """RECORD message.

    The RECORD message has these fields:

      * stream (string) - The name of the stream the record belongs to.
      * record (dict) - The raw data for the record
      * version (optional, int) - For versioned streams, the version
        number. Note that this feature is experimental and most Taps and
        Targets should not need to use versioned streams.

    msg = singer.RecordMessage(
        stream='users',
        record={'id': 1, 'name': 'Mary'})

    """

    def __init__(self, stream, record, version=None, time_extracted=None):
        self.stream = stream
        self.record = record
        self.version = version
        self.time_extracted = time_extracted
        if time_extracted and not time_extracted.tzinfo:
            raise ValueError(
                "'time_extracted' must be either None "
                + "or an aware datetime (with a time zone)"
            )

    def asdict(self):
        result = {
            "type": "RECORD",
            "stream": self.stream,
            "record": self.record,
        }
        if self.version is not None:
            result["version"] = self.version
        if self.time_extracted:
            as_utc = self.time_extracted.astimezone(pytz.utc)
            result["time_extracted"] = as_utc.isoformat()
        return result

    def __str__(self):
        return str(self.asdict())


class CatalogEntry:
    def __init__(
        self,
        tap_stream_id=None,
        stream=None,
        key_properties=None,
        schema=None,
        replication_key=None,
        is_view=None,
        database=None,
        table=None,
        row_count=None,
        stream_alias=None,
        metadata=None,
        replication_method=None,
    ):
        self.tap_stream_id = tap_stream_id
        self.stream = stream
        self.key_properties = key_properties
        self.schema = schema
        self.replication_key = replication_key
        self.replication_method = replication_method
        self.is_view = is_view
        self.database = database
        self.table = table
        self.row_count = row_count
        self.stream_alias = stream_alias
        self.metadata = metadata

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_dict(self):
        result = {}
        if self.tap_stream_id:
            result["tap_stream_id"] = self.tap_stream_id
        if self.database:
            result["database_name"] = self.database
        if self.table:
            result["table_name"] = self.table
        if self.replication_key is not None:
            result["replication_key"] = self.replication_key
        if self.replication_method is not None:
            result["replication_method"] = self.replication_method
        if self.key_properties is not None:
            result["key_properties"] = self.key_properties
        if self.schema is not None:
            schema = self.schema.to_dict()  # pylint: disable=no-member
            result["schema"] = schema
        if self.is_view is not None:
            result["is_view"] = self.is_view
        if self.stream is not None:
            result["stream"] = self.stream
        if self.row_count is not None:
            result["row_count"] = self.row_count
        if self.stream_alias is not None:
            result["stream_alias"] = self.stream_alias
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result


class Catalog:
    def __init__(self, streams):
        self.streams = streams

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def load(cls, filename):
        with open(filename) as fp:  # pylint: disable=invalid-name
            return Catalog.from_dict(json.load(fp))

    @classmethod
    def from_dict(cls, data):
        # TODO: We may want to store streams as a dict where the key is a
        # tap_stream_id and the value is a CatalogEntry. This will allow
        # faster lookup based on tap_stream_id. This would be a breaking
        # change, since callers typically access the streams property
        # directly.
        streams = []
        for stream in data["streams"]:
            entry = CatalogEntry()
            entry.tap_stream_id = stream.get("tap_stream_id")
            entry.stream = stream.get("stream")
            entry.replication_key = stream.get("replication_key")
            entry.key_properties = stream.get("key_properties")
            entry.database = stream.get("database_name")
            entry.table = stream.get("table_name")
            entry.schema = Schema.from_dict(stream.get("schema"))
            entry.is_view = stream.get("is_view")
            entry.stream_alias = stream.get("stream_alias")
            entry.metadata = stream.get("metadata")
            entry.replication_method = stream.get("replication_method")
            streams.append(entry)
        return Catalog(streams)

    def to_dict(self):
        return {"streams": [stream.to_dict() for stream in self.streams]}

    def get_stream(self, tap_stream_id):
        for stream in self.streams:
            if stream.tap_stream_id == tap_stream_id:
                return stream
        return None


def parse_message(msg):
    """Parse a message string into a Message object."""

    def _required_key(msg, k):
        if k not in msg:
            raise Exception(f"Message is missing required key '{k}': {msg}")

        return msg[k]

    # We are not using Decimals for parsing here.
    # We recognize that exposes data to potentially
    # lossy conversions.  However, this will affect
    # very few data points and we have chosen to
    # leave conversion as is for now.
    obj = json.loads(msg, use_decimal=True)
    msg_type = _required_key(obj, "type")

    if msg_type == "RECORD":
        time_extracted = obj.get("time_extracted")
        if time_extracted:
            try:
                time_extracted = datetime.fromisoformat(time_extracted).astimezone(
                    pytz.utc
                )
            except:
                time_extracted = None

        return RecordMessage(
            stream=_required_key(obj, "stream"),
            record=_required_key(obj, "record"),
            version=obj.get("version"),
            time_extracted=time_extracted,
        )

    elif msg_type == "SCHEMA":
        return SchemaMessage(
            stream=_required_key(obj, "stream"),
            schema=_required_key(obj, "schema"),
            key_properties=_required_key(obj, "key_properties"),
            bookmark_properties=obj.get("bookmark_properties"),
        )

    elif msg_type == "STATE":
        return StateMessage(value=_required_key(obj, "value"))

    elif msg_type == "ACTIVATE_VERSION":
        return ActivateVersionMessage(
            stream=_required_key(obj, "stream"), version=_required_key(obj, "version")
        )
    else:
        return None
