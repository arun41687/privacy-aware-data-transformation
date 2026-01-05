"""
Metadata Ingestion Module

Handles loading and managing table/column metadata from YAML files.
Provides synthetic metadata generation for testing and experimentation.
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from faker import Faker

# Set seed for reproducibility
Faker.seed(42)


@dataclass
class ColumnMetadata:
    """Represents metadata for a single column."""
    name: str
    data_type: str
    description: str = ""
    nullable: bool = True
    is_key: bool = False
    examples: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TableMetadata:
    """Represents metadata for a table."""
    table_name: str
    database: str = "default"
    columns: List[ColumnMetadata] = None
    description: str = ""
    owner: str = ""

    def __post_init__(self):
        if self.columns is None:
            self.columns = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "database": self.database,
            "description": self.description,
            "owner": self.owner,
            "columns": [col.to_dict() for col in self.columns]
        }


class MetadataLoader:
    """Loads table metadata from YAML files."""

    def __init__(self, metadata_dir: str):
        """
        Initialize the metadata loader.

        Args:
            metadata_dir: Directory containing YAML metadata files.
        """
        self.metadata_dir = Path(metadata_dir)
        if not self.metadata_dir.exists():
            raise FileNotFoundError(f"Metadata directory not found: {metadata_dir}")

    def load_table_metadata(self, table_file: str) -> TableMetadata:
        """
        Load metadata for a single table from a YAML file.

        Args:
            table_file: Name of the YAML file (e.g., 'customers.yaml')

        Returns:
            TableMetadata object
        """
        file_path = self.metadata_dir / table_file
        if not file_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {file_path}")

        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        # Parse columns
        columns = []
        if 'columns' in data:
            for col_data in data['columns']:
                col = ColumnMetadata(
                    name=col_data['name'],
                    data_type=col_data.get('data_type', 'string'),
                    description=col_data.get('description', ''),
                    nullable=col_data.get('nullable', True),
                    is_key=col_data.get('is_key', False),
                    examples=col_data.get('examples', None)
                )
                columns.append(col)

        # Create table metadata
        table_meta = TableMetadata(
            table_name=data.get('table_name', ''),
            database=data.get('database', 'default'),
            description=data.get('description', ''),
            owner=data.get('owner', ''),
            columns=columns
        )

        return table_meta

    def load_all_tables(self) -> Dict[str, TableMetadata]:
        """
        Load metadata for all YAML files in the directory.

        Returns:
            Dictionary mapping table names to TableMetadata objects
        """
        tables = {}
        for yaml_file in self.metadata_dir.glob('*.yaml'):
            try:
                table_meta = self.load_table_metadata(yaml_file.name)
                tables[table_meta.table_name] = table_meta
            except Exception as e:
                print(f"Error loading {yaml_file.name}: {e}")
        return tables


class SyntheticMetadataGenerator:
    """Generates synthetic table metadata for testing and demonstration."""

    def __init__(self, seed: int = 42):
        """
        Initialize the synthetic metadata generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.fake = Faker()
        Faker.seed(seed)

    def generate_customer_metadata(self) -> TableMetadata:
        """Generate synthetic customer table metadata."""
        columns = [
            ColumnMetadata(
                name="customer_id",
                data_type="int",
                description="Unique customer identifier (primary key)",
                is_key=True,
                examples=["1", "2", "3"]
            ),
            ColumnMetadata(
                name="first_name",
                data_type="string",
                description="Customer first name (PII)",
                examples=["John", "Jane", "Bob"]
            ),
            ColumnMetadata(
                name="last_name",
                data_type="string",
                description="Customer last name (PII)",
                examples=["Doe", "Smith", "Johnson"]
            ),
            ColumnMetadata(
                name="email",
                data_type="string",
                description="Customer email address (PII)",
                examples=["john@example.com", "jane@example.com"]
            ),
            ColumnMetadata(
                name="phone",
                data_type="string",
                description="Customer phone number (PII)",
                examples=["555-0101", "555-0102"]
            ),
            ColumnMetadata(
                name="ssn",
                data_type="string",
                description="Social Security Number (Sensitive PII)",
                examples=["123-45-6789", "987-65-4321"]
            ),
            ColumnMetadata(
                name="dob",
                data_type="date",
                description="Date of birth (PII)",
                examples=["1990-01-15", "1985-06-20"]
            ),
            ColumnMetadata(
                name="address",
                data_type="string",
                description="Customer street address (PII)",
                examples=["123 Main St", "456 Oak Ave"]
            ),
            ColumnMetadata(
                name="city",
                data_type="string",
                description="Customer city (Sensitive)",
                examples=["New York", "Los Angeles"]
            ),
            ColumnMetadata(
                name="state",
                data_type="string",
                description="Customer state",
                examples=["NY", "CA"]
            ),
            ColumnMetadata(
                name="zip_code",
                data_type="string",
                description="Customer zip code (Sensitive)",
                examples=["10001", "90001"]
            ),
            ColumnMetadata(
                name="registration_date",
                data_type="date",
                description="Account registration date (Non-Sensitive)",
                examples=["2020-01-01", "2021-06-15"]
            ),
            ColumnMetadata(
                name="status",
                data_type="string",
                description="Customer account status (Non-Sensitive)",
                examples=["active", "inactive"]
            ),
        ]

        return TableMetadata(
            table_name="customers",
            database="main_db",
            description="Customer personal information and contact details",
            owner="data_governance_team",
            columns=columns
        )

    def generate_health_metadata(self) -> TableMetadata:
        """Generate synthetic health/medical table metadata (PHI)."""
        columns = [
            ColumnMetadata(
                name="patient_id",
                data_type="int",
                description="Unique patient identifier (primary key)",
                is_key=True,
                examples=["1", "2", "3"]
            ),
            ColumnMetadata(
                name="patient_name",
                data_type="string",
                description="Patient full name (PHI)",
                examples=["John Doe", "Jane Smith"]
            ),
            ColumnMetadata(
                name="medical_record_number",
                data_type="string",
                description="Medical record number (PHI)",
                examples=["MRN123456", "MRN789012"]
            ),
            ColumnMetadata(
                name="diagnosis",
                data_type="string",
                description="Patient diagnosis (PHI/Sensitive)",
                examples=["Diabetes Type 2", "Hypertension"]
            ),
            ColumnMetadata(
                name="medication",
                data_type="string",
                description="Prescribed medication (PHI)",
                examples=["Metformin", "Lisinopril"]
            ),
            ColumnMetadata(
                name="dob",
                data_type="date",
                description="Date of birth (PHI)",
                examples=["1965-03-20", "1970-11-10"]
            ),
            ColumnMetadata(
                name="visit_date",
                data_type="date",
                description="Last visit date (Non-Sensitive)",
                examples=["2024-12-15", "2024-11-20"]
            ),
            ColumnMetadata(
                name="provider_name",
                data_type="string",
                description="Healthcare provider name (Non-Sensitive)",
                examples=["Dr. Smith", "Nurse Johnson"]
            ),
        ]

        return TableMetadata(
            table_name="patient_records",
            database="health_db",
            description="Patient medical and health information",
            owner="healthcare_admin",
            columns=columns
        )

    def generate_sales_metadata(self) -> TableMetadata:
        """Generate synthetic sales transaction metadata."""
        columns = [
            ColumnMetadata(
                name="transaction_id",
                data_type="int",
                description="Unique transaction identifier (primary key)",
                is_key=True,
                examples=["1", "2", "3"]
            ),
            ColumnMetadata(
                name="customer_id",
                data_type="int",
                description="Customer identifier (foreign key)",
                examples=["101", "102", "103"]
            ),
            ColumnMetadata(
                name="product_name",
                data_type="string",
                description="Product name (Non-Sensitive)",
                examples=["Laptop", "Mouse", "Monitor"]
            ),
            ColumnMetadata(
                name="quantity",
                data_type="int",
                description="Purchase quantity (Non-Sensitive)",
                examples=["1", "2", "5"]
            ),
            ColumnMetadata(
                name="amount",
                data_type="float",
                description="Transaction amount (Sensitive)",
                examples=["1299.99", "2500.00"]
            ),
            ColumnMetadata(
                name="payment_method",
                data_type="string",
                description="Payment method (Sensitive)",
                examples=["credit_card", "debit_card"]
            ),
            ColumnMetadata(
                name="transaction_date",
                data_type="date",
                description="Transaction date (Non-Sensitive)",
                examples=["2024-12-01", "2024-12-15"]
            ),
        ]

        return TableMetadata(
            table_name="sales_transactions",
            database="commerce_db",
            description="Customer sales transactions",
            owner="sales_team",
            columns=columns
        )

    def save_metadata_yaml(self, table_meta: TableMetadata, output_dir: str) -> str:
        """
        Save table metadata to a YAML file.

        Args:
            table_meta: TableMetadata object to save
            output_dir: Directory to save the YAML file

        Returns:
            Path to saved YAML file
        """
        output_path = Path(output_dir) / f"{table_meta.table_name}.yaml"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        yaml_data = {
            "table_name": table_meta.table_name,
            "database": table_meta.database,
            "description": table_meta.description,
            "owner": table_meta.owner,
            "columns": [
                {
                    "name": col.name,
                    "data_type": col.data_type,
                    "description": col.description,
                    "nullable": col.nullable,
                    "is_key": col.is_key,
                    "examples": col.examples
                }
                for col in table_meta.columns
            ]
        }

        with open(output_path, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

        return str(output_path)
