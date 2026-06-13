from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from pathlib import Path
from xml.dom import minidom

# App
# ---------------------------------------------------------------------------

class ReportSerializer(ABC):

    @abstractmethod
    def serialize(self, report: dict) -> str:
        """Convert the report dict to a formatted string."""

    @abstractmethod
    def extension(self) -> str:
        """File extension for this format."""

    def write(self, report: dict, path: Path) -> None:
        path.write_text(self.serialize(report), encoding="utf-8")


# ---------------------------------------------------------------------------

class JsonSerializer(ReportSerializer):

    def serialize(self, report: dict) -> str:
        return json.dumps(report, ensure_ascii=False, indent=2)

    def extension(self) -> str:
        return "json"

# ---------------------------------------------------------------------------
class XmlSerializer(ReportSerializer):

    def serialize(self, report: dict) -> str:
        root = ET.Element("report")
        self._dict_to_xml(root, report)
        rough = ET.tostring(root, encoding="unicode")
        pretty = minidom.parseString(rough).toprettyxml(indent="  ")
        return pretty

    def extension(self) -> str:
        return "xml"

# ---------------------------------------------------------------------------
    @classmethod
    def _dict_to_xml(cls, parent: ET.Element, data: dict | list | object) -> None:
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

# ---------------------------------------------------------------------------
class SerializerFactory:

    _registry: dict[str, type[ReportSerializer]] = {
        "json": JsonSerializer,
        "xml": XmlSerializer,
    }

    @classmethod
    def create(cls, fmt: str) -> ReportSerializer:
        fmt = fmt.lower()
        if fmt not in cls._registry:
            raise ValueError(
                f"Unknown format '{fmt}'. Supported: {list(cls._registry)}"
            )
        return cls._registry[fmt]()

    @classmethod
    def supported_formats(cls) -> list[str]:
        return list(cls._registry)
    
# ---------------------------------------------------------------------------
