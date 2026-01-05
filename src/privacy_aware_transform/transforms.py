"""
Data Transformation Module

Implements privacy-preserving transformations:
- Masking: Replace characters with mask character
- Hashing: Cryptographic hash (one-way, non-reversible)
- Tokenization: Consistent pseudonymization using keyed HMAC
- Aggregation: Group and summarize data
- Keep: No transformation (pass-through)
"""

import hashlib
import hmac
from typing import Any, Optional, Dict, List
from functools import lru_cache
import os


class Transformer:
    """Base class for data transformations."""

    def transform(self, value: Any) -> Any:
        """Transform a single value. To be overridden by subclasses."""
        raise NotImplementedError


class MaskingTransformer(Transformer):
    """Masks data by replacing characters with a mask character."""

    def __init__(self, keep_positions: List[int] = None, mask_char: str = "*"):
        """
        Initialize masking transformer.

        Args:
            keep_positions: List of positions to keep visible (can be negative for end positions)
            mask_char: Character to use for masking (default: '*')
        """
        self.keep_positions = keep_positions if keep_positions else []
        self.mask_char = mask_char

    def transform(self, value: Any) -> str:
        """
        Mask value by replacing characters.

        Args:
            value: Value to mask

        Returns:
            Masked string
        """
        if value is None or value == "":
            return ""

        value_str = str(value)

        if not self.keep_positions:
            # Mask entire value
            return self.mask_char * len(value_str)

        # Keep certain positions
        result = list(self.mask_char * len(value_str))
        for pos in self.keep_positions:
            if pos < 0:
                pos = len(value_str) + pos
            if 0 <= pos < len(value_str):
                result[pos] = value_str[pos]

        return ''.join(result)


class HashingTransformer(Transformer):
    """Applies cryptographic hash to data (one-way, non-reversible)."""

    def __init__(self, algorithm: str = "sha256"):
        """
        Initialize hashing transformer.

        Args:
            algorithm: Hash algorithm (sha256, sha512, md5, etc.)
        """
        self.algorithm = algorithm

    def transform(self, value: Any) -> str:
        """
        Hash value using specified algorithm.

        Args:
            value: Value to hash

        Returns:
            Hexadecimal hash string
        """
        if value is None or value == "":
            return ""

        value_str = str(value).encode('utf-8')
        hash_obj = hashlib.new(self.algorithm)
        hash_obj.update(value_str)
        return hash_obj.hexdigest()


class TokenizationTransformer(Transformer):
    """
    Applies consistent pseudonymization using keyed HMAC.
    
    Same input value always maps to same token (deterministic).
    Different secrets produce different tokens (key-based).
    Non-reversible without the key.
    """

    def __init__(self, secret_key: Optional[str] = None, token_length: int = 16):
        """
        Initialize tokenization transformer.

        Args:
            secret_key: Secret key for HMAC (random if not provided)
            token_length: Length of output token (truncated from hash)
        """
        if secret_key is None:
            # Generate a random secret key (or use environment variable for consistency)
            secret_key = os.environ.get('PRIVACY_SECRET_KEY', os.urandom(32).hex())
        
        self.secret_key = secret_key.encode('utf-8') if isinstance(secret_key, str) else secret_key
        self.token_length = token_length

    @lru_cache(maxsize=10000)
    def transform(self, value: Any) -> str:
        """
        Generate consistent token for value.

        Args:
            value: Value to tokenize

        Returns:
            Consistent token (pseudo-hash based on HMAC)
        """
        if value is None or value == "":
            return ""

        value_str = str(value).encode('utf-8')
        hmac_obj = hmac.new(self.secret_key, value_str, hashlib.sha256)
        token = hmac_obj.hexdigest()[:self.token_length]
        return f"TOKEN_{token}"


class KeepTransformer(Transformer):
    """Pass-through transformer (no transformation)."""

    def transform(self, value: Any) -> Any:
        """
        Return value unchanged.

        Args:
            value: Value to keep

        Returns:
            Same value
        """
        return value


class TransformationEngine:
    """
    Applies transformations to data based on policies.
    
    Coordinates between ClassificationResult and TransformationRules
    to transform entire dataframes.
    """

    def __init__(self):
        """Initialize transformation engine."""
        self.transformers: Dict[str, Transformer] = {}

    def get_transformer(self, transform_type: str, parameters: Dict[str, Any] = None) -> Transformer:
        """
        Get or create a transformer of given type.

        Args:
            transform_type: Type of transformation (mask, hash, tokenize, keep, aggregate)
            parameters: Parameters for the transformer

        Returns:
            Transformer object
        """
        if parameters is None:
            parameters = {}

        # Convert unhashable types to strings for cache key
        cache_params = {}
        for k, v in parameters.items():
            if isinstance(v, list):
                cache_params[k] = tuple(v)
            else:
                cache_params[k] = v
        
        cache_key = (transform_type, tuple(sorted(cache_params.items())))

        if cache_key not in self.transformers:
            if transform_type == "mask":
                transformer = MaskingTransformer(
                    keep_positions=parameters.get("keep_positions", []),
                    mask_char=parameters.get("mask_char", "*")
                )
            elif transform_type == "hash":
                transformer = HashingTransformer(
                    algorithm=parameters.get("algorithm", "sha256")
                )
            elif transform_type == "tokenize":
                transformer = TokenizationTransformer(
                    secret_key=parameters.get("secret_key"),
                    token_length=parameters.get("token_length", 16)
                )
            elif transform_type == "keep":
                transformer = KeepTransformer()
            else:
                # Default to keep
                transformer = KeepTransformer()

            self.transformers[cache_key] = transformer

        return self.transformers[cache_key]

    def apply_transformation(
        self,
        data: List[Any],
        transform_type: str,
        parameters: Dict[str, Any] = None
    ) -> List[Any]:
        """
        Apply transformation to a list of values.

        Args:
            data: List of values to transform
            transform_type: Type of transformation
            parameters: Parameters for the transformer

        Returns:
            List of transformed values
        """
        transformer = self.get_transformer(transform_type, parameters)
        return [transformer.transform(value) for value in data]

    def apply_column_transformation(
        self,
        column_data: List[Any],
        sensitivity_class: str,
        consumer_type: str,
        policy_engine: 'PolicyEngine'
    ) -> List[Any]:
        """
        Apply transformation to a column based on sensitivity and consumer policy.

        Args:
            column_data: List of values in the column
            sensitivity_class: Sensitivity class (PII, PHI, Sensitive, Non-Sensitive)
            consumer_type: Consumer type identifier
            policy_engine: PolicyEngine instance

        Returns:
            List of transformed values
        """
        rule = policy_engine.get_transformation_rule(consumer_type, sensitivity_class)
        if not rule:
            # Default: keep data unchanged
            return column_data

        return self.apply_transformation(
            column_data,
            rule.transformation_type,
            rule.parameters
        )
