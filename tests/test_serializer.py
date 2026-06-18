import tempfile
import unittest

from src.reporting.serializer import JsonSerializer, SerializerFactory, XmlSerializer


class TestJsonSerializer(unittest.TestCase):

    def test_extension(self):
        self.assertEqual(JsonSerializer().extension(), "json")

    def test_serialize(self):
        report = {"name": "John"}

        result = JsonSerializer().serialize(report)

        self.assertIn("John", result)


class TestXmlSerializer(unittest.TestCase):

    def test_extension(self):
        self.assertEqual(XmlSerializer().extension(), "xml")

    def test_serialize_simple(self):
        report = {"name": "John"}

        result = XmlSerializer().serialize(report)

        self.assertIn("<name>John</name>", result)

    def test_serialize_nested(self):
        report = {"students": [{"name": "John"}, {"name": "Jane"}]}

        result = XmlSerializer().serialize(report)

        self.assertIn("John", result)
        self.assertIn("Jane", result)


class TestSerializerFactory(unittest.TestCase):

    def test_create_json(self):
        serializer = SerializerFactory.create("json")

        self.assertIsInstance(serializer, JsonSerializer)

    def test_create_xml(self):
        serializer = SerializerFactory.create("xml")

        self.assertIsInstance(serializer, XmlSerializer)

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            SerializerFactory.create("csv")

    def test_supported_formats(self):
        formats = SerializerFactory.supported_formats()

        self.assertIn("json", formats)
        self.assertIn("xml", formats)

    def test_write(self):
        serializer = JsonSerializer()

        report = {"hello": "world"}

        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name

        from pathlib import Path

        serializer.write(report, Path(path))

        content = Path(path).read_text()

        self.assertIn("world", content)
