"""
Command-line interface for the privacy-aware data transformation framework.

Provides CLI commands for:
- Classifying sensitive data columns
- Applying privacy-preserving transformations
- Generating sample data and metadata
"""

import click
import sys
from pathlib import Path
import pandas as pd

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from privacy_aware_transform.metadata import MetadataLoader, SyntheticMetadataGenerator
from privacy_aware_transform.classifier import SensitivityClassifier
from privacy_aware_transform.policy import PolicyEngine, ConsumerType
from privacy_aware_transform.transforms import TransformationEngine
from privacy_aware_transform.utils import (
    load_csv_data, save_csv_data,
    apply_transformations_to_dataframe,
    print_classification_report
)


@click.group()
def cli():
    """Privacy-Aware Data Transformation CLI"""
    pass


@cli.command()
@click.option('--metadata-dir', type=click.Path(exists=True), required=True,
              help='Directory containing YAML metadata files')
@click.option('--output', type=click.Path(), default='metadata_report.txt',
              help='Output file for classification report')
def classify(metadata_dir: str, output: str):
    """Classify columns in metadata files."""
    click.echo(f"Loading metadata from: {metadata_dir}")

    try:
        loader = MetadataLoader(metadata_dir)
        tables = loader.load_all_tables()

        if not tables:
            click.echo("No metadata files found.")
            return

        classifier = SensitivityClassifier(use_ml=False)

        with open(output, 'w') as f:
            for table_name, table_meta in tables.items():
                click.echo(f"\nClassifying table: {table_name}")
                classifications = classifier.classify_table(table_meta.columns)
                summary = classifier.get_classification_summary(classifications)

                # Print to console and file
                report_text = f"\n{'='*80}\n"
                report_text += f"Classification Report for Table: {table_name}\n"
                report_text += f"{'='*80}\n"

                for col_name, result in classifications.items():
                    report_text += f"{col_name:30} | {result.sensitivity_class:15} | {result.confidence:.2f}\n"

                report_text += f"\nSummary:\n"
                for sens_class, count in summary.items():
                    report_text += f"  {sens_class}: {count}\n"

                click.echo(report_text)
                f.write(report_text)

        click.echo(f"\nReport saved to: {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--metadata-file', type=click.Path(exists=True), required=True,
              help='YAML metadata file for the table')
@click.option('--data-file', type=click.Path(exists=True), required=True,
              help='CSV file containing the data')
@click.option('--consumer-type', type=click.Choice(['internal_analyst', 'external_partner', 'reporting', 'public']),
              default='internal_analyst', help='Consumer type for policy')
@click.option('--output', type=click.Path(), default='transformed_data.csv',
              help='Output file for transformed data')
def transform(metadata_file: str, data_file: str, consumer_type: str, output: str):
    """Transform sensitive data based on metadata and consumer policy."""
    try:
        click.echo(f"Loading metadata from: {metadata_file}")
        click.echo(f"Loading data from: {data_file}")

        # Load metadata
        metadata_dir = Path(metadata_file).parent
        loader = MetadataLoader(str(metadata_dir))
        table_meta = loader.load_table_metadata(Path(metadata_file).name)

        # Load data
        df = load_csv_data(data_file)

        # Classify columns
        click.echo("Classifying columns...")
        classifier = SensitivityClassifier(use_ml=False)
        classifications = classifier.classify_table(table_meta.columns)

        # Print classification report
        print_classification_report(classifications, table_meta.table_name)

        # Transform data
        click.echo(f"Applying transformations for consumer: {consumer_type}")
        policy_engine = PolicyEngine()
        transformation_engine = TransformationEngine()

        transformed_df = apply_transformations_to_dataframe(
            df, table_meta, classifications,
            consumer_type, transformation_engine, policy_engine
        )

        # Save transformed data
        save_csv_data(transformed_df, output)
        click.echo(f"Transformed data saved to: {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output-dir', type=click.Path(), default='table_structure/metadata',
              help='Directory to save generated metadata files')
def generate_samples(output_dir: str):
    """Generate sample metadata and data files."""
    try:
        click.echo(f"Generating sample metadata files in: {output_dir}")

        generator = SyntheticMetadataGenerator()

        # Generate and save metadata
        for table_meta in [
            generator.generate_customer_metadata(),
            generator.generate_health_metadata(),
            generator.generate_sales_metadata()
        ]:
            filepath = generator.save_metadata_yaml(table_meta, output_dir)
            click.echo(f"  Generated: {filepath}")

        click.echo("\nGenerated sample metadata files:")
        click.echo("  - customers.yaml")
        click.echo("  - patient_records.yaml")
        click.echo("  - sales_transactions.yaml")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def list_policies():
    """List available consumer policies."""
    try:
        policy_engine = PolicyEngine()
        click.echo("\nAvailable Consumer Policies:")
        click.echo("="*50)
        for policy_name in policy_engine.list_policies():
            policy = policy_engine.get_policy(policy_name)
            click.echo(f"\n{policy_name.upper()}: {policy.name}")
            for sensitivity, rule in policy.rules.items():
                click.echo(f"  {sensitivity.value:20} -> {rule.transformation_type}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
