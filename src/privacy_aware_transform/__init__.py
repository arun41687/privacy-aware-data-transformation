"""
Privacy-Aware Data Transformation Framework

A framework for automated sensitive data classification and privacy-preserving
data transformations based on metadata-driven machine learning and policy engines.
"""

__version__ = "0.1.0"
__author__ = "Privacy Research Team"

from .metadata import MetadataLoader, SyntheticMetadataGenerator
from .classifier import SensitivityClassifier
from .policy import ConsumerPolicy, PolicyEngine
from .transforms import TransformationEngine, Transformer

__all__ = [
    "MetadataLoader",
    "SyntheticMetadataGenerator",
    "SensitivityClassifier",
    "ConsumerPolicy",
    "PolicyEngine",
    "TransformationEngine",
    "Transformer",
]
