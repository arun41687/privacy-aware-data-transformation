"""
Sensitivity Classification Module

Classifies data columns into sensitivity categories using rule-based heuristics
and optional machine learning models trained on metadata.
"""

from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from .metadata import ColumnMetadata


@dataclass
class ClassificationResult:
    """Result of column sensitivity classification."""
    column_name: str
    sensitivity_class: str  # PII, PHI, Sensitive, Non-Sensitive
    confidence: float
    reasoning: str
    method: str = "rule-based"  # or "ml" or "blended"


class SensitivityClassifier:
    """
    Classifies data columns into sensitivity categories.
    
    Uses rule-based heuristics combined with optional ML model.
    Classes:
    - PII: Personally Identifiable Information (names, emails, SSN, etc.)
    - PHI: Protected Health Information (medical diagnoses, medications, etc.)
    - Sensitive: Financial, location, or other sensitive data
    - Non-Sensitive: Public or low-sensitivity data
    """

    # Rule-based patterns for each sensitivity class
    PII_PATTERNS = {
        r'(first_?name|last_?name|name|full_?name)': 'name patterns',
        r'(email|email_?address|e_?mail)': 'email patterns',
        r'(phone|tel|mobile|contact)': 'phone patterns',
        r'(ssn|social_?security|social_security_?number)': 'SSN patterns',
        r'(passport|driver_?license|drivers_?license)': 'ID document patterns',
        r'(address|street|residence)': 'address patterns',
        r'(dob|date_?of_?birth|birth_?date)': 'date of birth patterns',
        r'(credit_?card|cc_?number|card_?number)': 'credit card patterns',
        r'(account_?number|acct_?number)': 'account number patterns',
    }

    PHI_PATTERNS = {
        r'(diagnosis|diagnoses|medical_?condition)': 'diagnosis patterns',
        r'(medication|medicine|drug|prescription)': 'medication patterns',
        r'(medical_?record|patient_?record|health_?record)': 'medical record patterns',
        r'(patient|health|medical|clinical)': 'health domain keywords',
        r'(laboratory|lab_?result|lab_?test)': 'lab result patterns',
        r'(procedure|surgery|treatment)': 'treatment patterns',
    }

    SENSITIVE_PATTERNS = {
        r'(salary|income|wage|payment|amount|price|cost|revenue)': 'financial amount patterns',
        r'(bank|account|balance|transaction|financial)': 'financial keywords',
        r'(zip_?code|postal_?code|location|latitude|longitude)': 'location patterns',
        r'(ip_?address|device_?id|mac_?address|imei)': 'device identifier patterns',
        r'(password|secret|token|key|credential)': 'security credential patterns',
        r'(religion|ethnicity|race|gender|sexual_?orientation)': 'demographic sensitive patterns',
    }

    def __init__(self, use_ml: bool = False, ml_model_path: Optional[str] = None):
        """
        Initialize the classifier.

        Args:
            use_ml: Whether to use ML model
            ml_model_path: Path to pre-trained ML model (pickle file).
                          If not provided and use_ml=True, looks for models/sensitivity_classifier.pkl
        """
        self.use_ml = use_ml
        self.ml_pipeline = None
        self.ml_classes = ['PII', 'PHI', 'Sensitive', 'Non-Sensitive']

        if use_ml:
            # Try to load pre-trained model
            if ml_model_path is None:
                # Look for default model location
                ml_model_path = str(Path(__file__).parent.parent.parent / 'models' / 'sensitivity_classifier.pkl')
            
            if Path(ml_model_path).exists():
                self._load_ml_model(ml_model_path)
            else:
                print(f"Warning: ML model not found at {ml_model_path}")
                print("  To train a model, run: python train_ml_classifier.py")
                print("  Falling back to rule-based classification.")
                self.use_ml = False

    def _load_ml_model(self, model_path: str) -> None:
        """Load pre-trained ML model from pickle file."""
        import pickle
        try:
            with open(model_path, 'rb') as f:
                self.ml_pipeline = pickle.load(f)
            print(f"✓ Loaded ML model from {model_path}")
        except Exception as e:
            print(f"Warning: Could not load ML model from {model_path}: {e}")
            self.use_ml = False

    def classify_column(self, column: ColumnMetadata) -> ClassificationResult:
        """
        Classify a single column based on metadata.
        
        Uses rule-based classification first. If confidence < 0.8 and ML model available,
        blends ML prediction with rule-based result using weighted averaging.

        Args:
            column: ColumnMetadata object

        Returns:
            ClassificationResult with sensitivity class and confidence
        """
        # First try rule-based classification
        rule_result = self._classify_by_rules(column)

        # If using ML model and rules are uncertain, blend with ML
        if self.use_ml and self.ml_pipeline and rule_result.confidence < 0.8:
            ml_result = self._classify_by_ml(column)
            
            # If ML has higher confidence, prefer it
            if ml_result.confidence > rule_result.confidence:
                ml_result.method = "ml"
                return ml_result
            
            # Otherwise blend both methods
            if ml_result.sensitivity_class == rule_result.sensitivity_class:
                # Both agree: use average confidence
                blended_confidence = (rule_result.confidence + ml_result.confidence) / 2
                return ClassificationResult(
                    column_name=column.name,
                    sensitivity_class=rule_result.sensitivity_class,
                    confidence=blended_confidence,
                    reasoning=f"Blended (rule + ML): {rule_result.reasoning} | ML: {ml_result.reasoning}",
                    method="blended"
                )

        rule_result.method = "rule-based"
        return rule_result

    def _classify_by_rules(self, column: ColumnMetadata) -> ClassificationResult:
        """Classify using rule-based patterns."""
        combined_text = f"{column.name} {column.description}".lower()

        # Check PII patterns
        for pattern, reason in self.PII_PATTERNS.items():
            if re.search(pattern, combined_text):
                return ClassificationResult(
                    column_name=column.name,
                    sensitivity_class='PII',
                    confidence=0.9,
                    reasoning=f"Matched PII pattern: {reason}"
                )

        # Check PHI patterns
        for pattern, reason in self.PHI_PATTERNS.items():
            if re.search(pattern, combined_text):
                return ClassificationResult(
                    column_name=column.name,
                    sensitivity_class='PHI',
                    confidence=0.9,
                    reasoning=f"Matched PHI pattern: {reason}"
                )

        # Check Sensitive patterns
        for pattern, reason in self.SENSITIVE_PATTERNS.items():
            if re.search(pattern, combined_text):
                return ClassificationResult(
                    column_name=column.name,
                    sensitivity_class='Sensitive',
                    confidence=0.85,
                    reasoning=f"Matched sensitive pattern: {reason}"
                )

        # Default to Non-Sensitive
        return ClassificationResult(
            column_name=column.name,
            sensitivity_class='Non-Sensitive',
            confidence=0.7,
            reasoning="No sensitivity patterns matched; column is non-sensitive"
        )

    def _classify_by_ml(self, column: ColumnMetadata) -> ClassificationResult:
        """
        Classify using ML model.
        
        Extracts features from column metadata and uses trained model for prediction.

        Args:
            column: ColumnMetadata object

        Returns:
            ClassificationResult with ML prediction
        """
        if not self.ml_pipeline:
            return ClassificationResult(
                column_name=column.name,
                sensitivity_class='Non-Sensitive',
                confidence=0.0,
                reasoning="ML model not available",
                method="ml"
            )

        # Combine metadata as features
        combined_text = f"{column.name} {column.description} {column.data_type}".lower()
        
        try:
            prediction = self.ml_pipeline.predict([combined_text])[0]
            probabilities = self.ml_pipeline.predict_proba([combined_text])[0]
            confidence = float(max(probabilities))

            return ClassificationResult(
                column_name=column.name,
                sensitivity_class=prediction,
                confidence=confidence,
                reasoning=f"ML model prediction (confidence {confidence:.2f})",
                method="ml"
            )
        except Exception as e:
            print(f"Warning: ML prediction failed for {column.name}: {e}")
            return ClassificationResult(
                column_name=column.name,
                sensitivity_class='Non-Sensitive',
                confidence=0.0,
                reasoning="ML prediction error",
                method="ml"
            )

    def classify_table(self, table_columns: List[ColumnMetadata]) -> Dict[str, ClassificationResult]:
        """
        Classify all columns in a table.

        Args:
            table_columns: List of ColumnMetadata objects

        Returns:
            Dictionary mapping column names to ClassificationResult
        """
        results = {}
        for column in table_columns:
            result = self.classify_column(column)
            results[column.name] = result
        return results

    def train_ml_model(self, training_data: List[Tuple[str, str]]) -> None:
        """
        Train an ML model on labeled metadata.

        Args:
            training_data: List of (text, label) tuples where text is 
                          "column_name description" and label is sensitivity class
        """
        if not training_data:
            print("Warning: No training data provided")
            return

        texts = [text for text, _ in training_data]
        labels = [label for _, label in training_data]

        self.ml_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=100, lowercase=True)),
            ('classifier', LogisticRegression(max_iter=200, random_state=42))
        ])

        self.ml_pipeline.fit(texts, labels)
        self.use_ml = True
        print(f"ML model trained on {len(training_data)} samples")

    def get_classification_summary(self, results: Dict[str, ClassificationResult]) -> Dict[str, int]:
        """
        Get summary of classifications by sensitivity class.

        Args:
            results: Dictionary of classification results

        Returns:
            Dictionary with counts per sensitivity class
        """
        summary = {'PII': 0, 'PHI': 0, 'Sensitive': 0, 'Non-Sensitive': 0}
        for result in results.values():
            summary[result.sensitivity_class] += 1
        return summary
