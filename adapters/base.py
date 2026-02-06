from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TestResult:
    testcase_id: str
    status: str                 # "passed" | "failed" | "skipped" | "error"
    details: str = ""
    artifacts: Optional[Dict[str, Any]] = None


class SUTAdapter(ABC):
    """
    Base interface that every SUT (System Under Test) adapter must implement.
    Core pipeline talks ONLY to this interface.
    """

    def __init__(self, sut_config: Dict[str, Any]):
        self.sut_config = sut_config

    @property
    @abstractmethod
    def type_name(self) -> str:
        """Must match sut.yaml 'type' field (e.g., 'redmine')."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Human-readable name."""
        return self.type_name

    @abstractmethod
    def healthcheck(self) -> bool:
        """Return True if SUT seems reachable/ready."""
        raise NotImplementedError

    def get_context_bundle(self) -> Dict[str, Any]:
        """
        Provide app-specific context that the generator can use.
        Keep it JSON-serializable.
        """
        return {}

    @abstractmethod
    def execute_testcase(self, testcase: Dict[str, Any]) -> TestResult:
        """
        Execute one normalized test case (core schema).
        For now, can be a stub. Later, implement UI/API.
        """
        raise NotImplementedError
