"""
Report serialization framework.

Provides serializers for converting analytical reports
into different output formats such as JSON and XML.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from pathlib import Path
from xml.dom import minidom


class ReportSerializer(ABC):
    """
    Base class for report serializers.

    Defines the interface for converting report data into
    a specific output format.
    """

    @abstractmethod
    def serialize(self, report: dict) -> str:
        """
        Convert a report dictionary into a formatted string.

        Args:
            report: Report data to serialize.

        Returns:
            Serialized representation of the report.
        """

    @abstractmethod
    def extension(self) -> str:
        """
        Return the file extension associated with the serializer.

        Returns:
            File extension without a leading dot.
        """

    def write(self, report: dict, path: Path) -> None:
        """
        Serialize a report and write it to a file.

        Args:
            report: Report data to write.
            path: Destination file path.
        """
        path.write_text(self.serialize(report), encoding="utf-8")


class JsonSerializer(ReportSerializer):
    """
    Serializes reports to JSON format.
    """

    def serialize(self, report: dict) -> str:
        """
        Convert a report dictionary to formatted JSON.

        Args:
            report: Report data.

        Returns:
            JSON-formatted string.
        """
        return json.dumps(report, ensure_ascii=False, indent=2)

    def extension(self) -> str:
        """
        Return the JSON file extension.

        Returns:
            'json'
        """
        return "json"


class XmlSerializer(ReportSerializer):
    """
    Serializes reports to XML format.
    """

    def serialize(self, report: dict) -> str:
        """
        Convert a report dictionary to formatted XML.

        Args:
            report: Report data.

        Returns:
            Pretty-printed XML string.
        """
        root = ET.Element("report")
        self._dict_to_xml(root, report)

        rough = ET.tostring(root, encoding="unicode")
        pretty = minidom.parseString(rough).toprettyxml(indent="  ")

        return pretty

    def extension(self) -> str:
        """
        Return the XML file extension.

        Returns:
            'xml'
        """
        return "xml"

    @classmethod
    def _dict_to_xml(cls, parent: ET.Element, data: dict | list | object) -> None:
        """
        Recursively convert Python objects into XML elements.

        Args:
            parent: Parent XML element.
            data: Data structure to convert.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    container = ET.SubElement(parent, key)

                    singular = key.rstrip("s")

                    for item in value:
                        child = ET.SubElement(container, singular)
                        cls._dict_to_xml(child, item)

                elif isinstance(value, dict):
                    child = ET.SubElement(parent, key)
                    cls._dict_to_xml(child, value)

                else:
                    ET.SubElement(parent, key).text = str(value)

        else:
            parent.text = str(data)


class SerializerFactory:
    """
    Factory for creating serializer instances.

    Provides a central registry of supported report formats.
    """

    _registry: dict[str, type[ReportSerializer]] = {
        "json": JsonSerializer,
        "xml": XmlSerializer,
    }

    @classmethod
    def create(cls, fmt: str) -> ReportSerializer:
        """
        Create a serializer for the specified format.

        Args:
            fmt: Requested serialization format.

        Returns:
            Serializer instance.

        Raises:
            ValueError: If the format is not supported.
        """
        fmt = fmt.lower()

        if fmt not in cls._registry:
            raise ValueError(
                f"Unknown format '{fmt}'. Supported: {list(cls._registry)}"
            )

        return cls._registry[fmt]()

    @classmethod
    def supported_formats(cls) -> list[str]:
        """
        Return all supported serialization formats.

        Returns:
            List of supported format names.
        """
        return list(cls._registry)
