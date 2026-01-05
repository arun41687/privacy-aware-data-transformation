"""
Policy Engine Module

Defines consumer policies and applies transformation rules based on
data sensitivity, consumer identity, and usage context.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum


class ConsumerType(Enum):
    """Types of data consumers."""
    INTERNAL_ANALYST = "internal_analyst"
    EXTERNAL_PARTNER = "external_partner"
    REPORTING = "reporting"
    PUBLIC = "public"


class SensitivityLevel(Enum):
    """Data sensitivity levels."""
    PII = "PII"
    PHI = "PHI"
    SENSITIVE = "Sensitive"
    NON_SENSITIVE = "Non-Sensitive"


@dataclass
class TransformationRule:
    """Defines how to transform data based on sensitivity and consumer."""
    sensitivity: SensitivityLevel
    consumer_type: ConsumerType
    transformation_type: str  # mask, hash, tokenize, aggregate, keep
    parameters: Dict[str, any] = field(default_factory=dict)

    def __hash__(self):
        return hash((self.sensitivity, self.consumer_type, self.transformation_type))

    def __eq__(self, other):
        return (self.sensitivity == other.sensitivity and
                self.consumer_type == other.consumer_type and
                self.transformation_type == other.transformation_type)


@dataclass
class ConsumerPolicy:
    """
    Defines privacy transformation policies for different consumer types.
    
    Maps (sensitivity_class, consumer_type) -> transformation rules
    """
    name: str
    consumer_type: ConsumerType
    rules: Dict[SensitivityLevel, TransformationRule] = field(default_factory=dict)

    def get_rule(self, sensitivity: SensitivityLevel) -> Optional[TransformationRule]:
        """Get transformation rule for given sensitivity level."""
        return self.rules.get(sensitivity)


class PolicyEngine:
    """
    Manages and applies privacy policies.
    
    Provides default policies and allows custom policy definition.
    """

    def __init__(self):
        """Initialize with default policies for each consumer type."""
        self.policies: Dict[str, ConsumerPolicy] = {}
        self._init_default_policies()

    def _init_default_policies(self) -> None:
        """Initialize default privacy policies."""

        # Policy for Internal Analysts - more data utility, less privacy
        internal_policy = ConsumerPolicy(
            name="Internal Analytics",
            consumer_type=ConsumerType.INTERNAL_ANALYST,
            rules={
                SensitivityLevel.PII: TransformationRule(
                    sensitivity=SensitivityLevel.PII,
                    consumer_type=ConsumerType.INTERNAL_ANALYST,
                    transformation_type="tokenize",
                    parameters={"token_length": 16}
                ),
                SensitivityLevel.PHI: TransformationRule(
                    sensitivity=SensitivityLevel.PHI,
                    consumer_type=ConsumerType.INTERNAL_ANALYST,
                    transformation_type="tokenize",
                    parameters={"token_length": 16}
                ),
                SensitivityLevel.SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.SENSITIVE,
                    consumer_type=ConsumerType.INTERNAL_ANALYST,
                    transformation_type="mask",
                    parameters={"keep_positions": [0, -1], "mask_char": "*"}
                ),
                SensitivityLevel.NON_SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.NON_SENSITIVE,
                    consumer_type=ConsumerType.INTERNAL_ANALYST,
                    transformation_type="keep",
                    parameters={}
                ),
            }
        )

        # Policy for External Partners - strict privacy, limited utility
        external_policy = ConsumerPolicy(
            name="External Partnership",
            consumer_type=ConsumerType.EXTERNAL_PARTNER,
            rules={
                SensitivityLevel.PII: TransformationRule(
                    sensitivity=SensitivityLevel.PII,
                    consumer_type=ConsumerType.EXTERNAL_PARTNER,
                    transformation_type="hash",
                    parameters={"algorithm": "sha256"}
                ),
                SensitivityLevel.PHI: TransformationRule(
                    sensitivity=SensitivityLevel.PHI,
                    consumer_type=ConsumerType.EXTERNAL_PARTNER,
                    transformation_type="hash",
                    parameters={"algorithm": "sha256"}
                ),
                SensitivityLevel.SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.SENSITIVE,
                    consumer_type=ConsumerType.EXTERNAL_PARTNER,
                    transformation_type="mask",
                    parameters={"keep_positions": [], "mask_char": "*"}
                ),
                SensitivityLevel.NON_SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.NON_SENSITIVE,
                    consumer_type=ConsumerType.EXTERNAL_PARTNER,
                    transformation_type="keep",
                    parameters={}
                ),
            }
        )

        # Policy for Reporting - aggregation and masking
        reporting_policy = ConsumerPolicy(
            name="Reporting",
            consumer_type=ConsumerType.REPORTING,
            rules={
                SensitivityLevel.PII: TransformationRule(
                    sensitivity=SensitivityLevel.PII,
                    consumer_type=ConsumerType.REPORTING,
                    transformation_type="mask",
                    parameters={"keep_positions": [], "mask_char": "*"}
                ),
                SensitivityLevel.PHI: TransformationRule(
                    sensitivity=SensitivityLevel.PHI,
                    consumer_type=ConsumerType.REPORTING,
                    transformation_type="mask",
                    parameters={"keep_positions": [], "mask_char": "*"}
                ),
                SensitivityLevel.SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.SENSITIVE,
                    consumer_type=ConsumerType.REPORTING,
                    transformation_type="aggregate",
                    parameters={"aggregate_type": "count"}
                ),
                SensitivityLevel.NON_SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.NON_SENSITIVE,
                    consumer_type=ConsumerType.REPORTING,
                    transformation_type="keep",
                    parameters={}
                ),
            }
        )

        # Policy for Public - maximum privacy, minimal data
        public_policy = ConsumerPolicy(
            name="Public",
            consumer_type=ConsumerType.PUBLIC,
            rules={
                SensitivityLevel.PII: TransformationRule(
                    sensitivity=SensitivityLevel.PII,
                    consumer_type=ConsumerType.PUBLIC,
                    transformation_type="hash",
                    parameters={"algorithm": "sha256"}
                ),
                SensitivityLevel.PHI: TransformationRule(
                    sensitivity=SensitivityLevel.PHI,
                    consumer_type=ConsumerType.PUBLIC,
                    transformation_type="hash",
                    parameters={"algorithm": "sha256"}
                ),
                SensitivityLevel.SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.SENSITIVE,
                    consumer_type=ConsumerType.PUBLIC,
                    transformation_type="aggregate",
                    parameters={"aggregate_type": "count"}
                ),
                SensitivityLevel.NON_SENSITIVE: TransformationRule(
                    sensitivity=SensitivityLevel.NON_SENSITIVE,
                    consumer_type=ConsumerType.PUBLIC,
                    transformation_type="keep",
                    parameters={}
                ),
            }
        )

        self.policies["internal_analyst"] = internal_policy
        self.policies["external_partner"] = external_policy
        self.policies["reporting"] = reporting_policy
        self.policies["public"] = public_policy

    def get_policy(self, consumer_type: str) -> Optional[ConsumerPolicy]:
        """
        Get policy for a consumer type.

        Args:
            consumer_type: Consumer type identifier

        Returns:
            ConsumerPolicy object or None
        """
        return self.policies.get(consumer_type)

    def add_custom_policy(self, policy: ConsumerPolicy) -> None:
        """
        Add or override a custom policy.

        Args:
            policy: ConsumerPolicy object
        """
        self.policies[policy.consumer_type.value] = policy

    def get_transformation_rule(self, consumer_type: str, sensitivity: str) -> Optional[TransformationRule]:
        """
        Get transformation rule for (consumer_type, sensitivity) pair.

        Args:
            consumer_type: Consumer type identifier
            sensitivity: Sensitivity class name (PII, PHI, Sensitive, Non-Sensitive)

        Returns:
            TransformationRule or None
        """
        policy = self.get_policy(consumer_type)
        if not policy:
            return None

        # Convert sensitivity string to enum
        try:
            sens_enum = SensitivityLevel[sensitivity.upper().replace('-', '_')]
            return policy.get_rule(sens_enum)
        except KeyError:
            return None

    def list_policies(self) -> List[str]:
        """List all available policy names."""
        return list(self.policies.keys())
