"""
Base Detector interface for PS02 Suspicious Activity Detectors.
"""

from abc import ABC, abstractmethod
from typing import List
from src.schema import NormalizedEvent, DetectionFinding
from src.config import AppConfig


class BaseDetector(ABC):
    """Abstract base class for all security detection rules."""

    def __init__(self, config: AppConfig):
        self.config = config

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique ID for this detector rule."""
        pass

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable title of the rule."""
        pass

    @abstractmethod
    def evaluate(self, events: List[NormalizedEvent]) -> List[DetectionFinding]:
        """
        Evaluate a stream of normalized security events and return all triggered findings.
        """
        pass
