"""
Utility functions for the privacy-aware data transformation framework.
"""

import pandas as pd
from typing import List, Dict, Any
from .metadata import TableMetadata
from .classifier import ClassificationResult, SensitivityClassifier


def load_csv_data(filepath: str) -> pd.DataFrame:
    """Load CSV data into a DataFrame."""
    return pd.read_csv(filepath)


def save_csv_data(df: pd.DataFrame, filepath: str) -> None:
    """Save DataFrame to CSV."""
    df.to_csv(filepath, index=False)


def apply_transformations_to_dataframe(
    df: pd.DataFrame,
    table_metadata: TableMetadata,
    classifications: Dict[str, ClassificationResult],
    consumer_type: str,
    transformation_engine: 'TransformationEngine',
    policy_engine: 'PolicyEngine'
) -> pd.DataFrame:
    """
    Apply transformations to entire DataFrame based on classifications and policy.

    Args:
        df: Input DataFrame
        table_metadata: Table metadata
        classifications: Dictionary of column classifications
        consumer_type: Consumer type identifier
        transformation_engine: TransformationEngine instance
        policy_engine: PolicyEngine instance

    Returns:
        Transformed DataFrame
    """
    transformed_df = df.copy()

    for column_name in df.columns:
        if column_name not in classifications:
            # Skip columns not in metadata
            continue

        classification = classifications[column_name]
        sensitivity_class = classification.sensitivity_class

        # Apply transformation
        transformed_df[column_name] = transformation_engine.apply_column_transformation(
            df[column_name].tolist(),
            sensitivity_class,
            consumer_type,
            policy_engine
        )

    return transformed_df


def print_classification_report(
    classifications: Dict[str, ClassificationResult],
    table_name: str = "Unknown"
) -> None:
    """
    Print a formatted classification report.

    Args:
        classifications: Dictionary of classification results
        table_name: Name of the table
    """
    print(f"\n{'='*80}")
    print(f"Classification Report for Table: {table_name}")
    print(f"{'='*80}\n")

    # Print by sensitivity class
    from collections import defaultdict
    by_class = defaultdict(list)
    for col_name, result in classifications.items():
        by_class[result.sensitivity_class].append((col_name, result))

    for sensitivity_class in ['PII', 'PHI', 'Sensitive', 'Non-Sensitive']:
        if sensitivity_class in by_class:
            print(f"\n{sensitivity_class}:")
            print(f"{'-'*80}")
            for col_name, result in by_class[sensitivity_class]:
                print(f"  {col_name:30} | Confidence: {result.confidence:.2f} | {result.reasoning}")

    print(f"\n{'='*80}\n")
