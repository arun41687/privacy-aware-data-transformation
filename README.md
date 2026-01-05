# Privacy-Aware Data Transformation

An open-source research framework for **automated sensitive data classification** and **adaptive privacy-preserving data transformations** in modern data pipelines.

This project focuses on identifying sensitive data using metadata-driven machine learning techniques and dynamically applying privacy-preserving transformations based on data sensitivity, consumer identity, and usage context.

---

## 📌 Motivation

Organizations increasingly share data across internal teams, external partners, and reporting systems. However:

- Manual identification of sensitive data (PII, PHI, etc.) is error-prone and non-scalable
- Static data masking rules reduce data utility or fail privacy requirements
- Different consumers require different privacy guarantees for the same dataset

This repository addresses these challenges by providing a **privacy-aware, automated, and adaptive data transformation framework**.

---

## 🎯 Key Objectives

- Automatically classify data fields into sensitivity categories (PII, PHI, Sensitive, Non-Sensitive)
- Leverage **column names, column descriptions, and table metadata** for classification
- Apply **dynamic privacy-preserving transformations** based on:
  - Data sensitivity
  - Consumer identity (internal analyst, external partner, reporting)
  - Purpose of data usage
- Enable reproducible research through open-source implementation

---

## 🧠 Core Features

### 1. Automated Sensitive Data Classification
- Metadata-driven machine learning models
- NLP-based feature extraction from schema metadata
- Multi-class classification:
  - PII (Personally Identifiable Information)
  - PHI (Protected Health Information)
  - Sensitive
  - Non-Sensitive

### 2. Privacy-Aware Transformation Engine
- Consumer-aware transformation policies
- Dynamic generation of transformations such as:
  - Tokenization (internal analytics)
  - Masking or hashing (reporting)
  - Aggregation (external data sharing)

### 3. Privacy–Utility Tradeoff
- Minimizes privacy risk while preserving analytical utility
- Supports configurable privacy policies

---

## 🏗️ High-Level Architecture
```
Metadata Ingestion (YAML files)
↓
Sensitive Data Classification (Rule-based + Optional ML)
↓
Privacy Policy & Consumer Context Engine
↓
Dynamic Transformation Generator
↓
Privacy-Preserving Data Output (CSV)
```

---

## 📂 Repository Structure
```
privacy-aware-data-transformation/
│
├── src/privacy_aware_transform/
│   ├── __init__.py                # Package exports
│   ├── metadata.py                # Metadata ingestion and synthetic generation
│   ├── classifier.py              # Sensitivity classification (rules + ML)
│   ├── policy.py                  # Consumer policies and transformation rules
│   ├── transforms.py              # Transformation implementations (mask, hash, tokenize, aggregate)
│   ├── utils.py                   # Utility functions
│   └── cli.py                     # Command-line interface
│
├── table_structure/metadata/      # YAML metadata files for tables
│   ├── customers.yaml             # Customer data table metadata
│   ├── patient_records.yaml       # Patient data table metadata
│   └── sales_transactions.yaml    # Sales transaction table metadata
│
├── data/
│   └── synthetic/                 # Synthetic sample data (CSV files and transformed outputs)
│       ├── customers.csv
│       ├── patient_records.csv
│       ├── sales_transactions.csv
│       └── <consumer_type>/       # Transformed data by consumer type
│
├── examples/
│   └── example.py                 # Example script demonstrating the full pipeline
│
├── README.md
├── LICENSE
├── requirements.txt               # Python dependencies
└── .gitignore
```

---

## 🧪 Experimental Design

### Datasets
- Synthetic schemas with labeled sensitivity classes
- Publicly available metadata schemas (healthcare, finance, retail)
- No real personal or confidential data is used

### Baselines
- Rule-based sensitive data detection
- Static masking and transformation approaches

### Evaluation Metrics
- Precision, Recall, F1-score for sensitivity classification
- Transformation effectiveness
- Privacy risk reduction
- Data utility preservation

### Reproducibility
- Fixed random seeds
- Configurable experiments
- Fully local execution (no AWS required)

---

## 📖 Research & Publications

This repository supports scholarly publications focusing on:

- Metadata-driven sensitive data classification
- Privacy-aware dynamic data transformations
- Privacy–utility tradeoff analysis
- Open-source reproducibility in data privacy research

The implementation aligns closely with the methodologies and experiments described in the associated journal articles.

---

## 📎 Citation

If you use this framework in your research, please cite:
```
@software{privacy_aware_data_transformation,
title = {Privacy-Aware Data Transformation},
author = {Thimmareddy, Avinash},
year = {2025},
url = {https://github.com/<your-username>/privacy-aware-data-transformation}
}
```

---

## ⚖️ License

This project is licensed under the **Apache License 2.0**.

---

## 🛡️ Ethical Considerations

- No real personal data is used
- All datasets are synthetic or publicly available
- Intended for research and educational purposes
- Users are responsible for compliance with applicable data protection laws

---

## 🚀 Getting Started

### Installation

```bash
git clone https://github.com/<your-username>/privacy-aware-data-transformation.git
cd privacy-aware-data-transformation
pip install -r requirements.txt
```

### Quick Start

#### 1. Run the Example Script (Recommended)

```bash
python examples/example.py
```

This script:
- Generates sample metadata YAML files (customers, patient records, sales transactions)
- Creates synthetic test data (CSV files)
- Classifies sensitive columns using metadata-driven rules
- Applies privacy-preserving transformations for different consumer types
- Saves transformed outputs

**Output:** Check `data/synthetic/` for original and transformed data organized by consumer type.

#### 2. Use the CLI

##### Generate sample metadata:
```bash
python -m privacy_aware_transform.cli generate-samples --output-dir table_structure/metadata
```

##### Classify columns in metadata:
```bash
python -m privacy_aware_transform.cli classify --metadata-dir table_structure/metadata --output classification_report.txt
```

##### Transform data based on policy:
```bash
python -m privacy_aware_transform.cli transform \
  --metadata-file table_structure/metadata/customers.yaml \
  --data-file data/synthetic/customers.csv \
  --consumer-type internal_analyst \
  --output data/synthetic/customers_transformed.csv
```

##### List available consumer policies:
```bash
python -m privacy_aware_transform.cli list-policies
```

#### 3. Programmatic Usage

```python
from privacy_aware_transform.metadata import MetadataLoader
from privacy_aware_transform.classifier import SensitivityClassifier
from privacy_aware_transform.policy import PolicyEngine
from privacy_aware_transform.transforms import TransformationEngine
from privacy_aware_transform.utils import load_csv_data, apply_transformations_to_dataframe, save_csv_data

# Load metadata from YAML
loader = MetadataLoader('table_structure/metadata')
table_meta = loader.load_table_metadata('customers.yaml')

# Classify sensitive columns
classifier = SensitivityClassifier(use_ml=False)
classifications = classifier.classify_table(table_meta.columns)

# Load data and apply transformations
df = load_csv_data('data/synthetic/customers.csv')
policy_engine = PolicyEngine()
transformation_engine = TransformationEngine()

# Transform for internal analyst
transformed_df = apply_transformations_to_dataframe(
    df, table_meta, classifications,
    consumer_type='internal_analyst',
    transformation_engine=transformation_engine,
    policy_engine=policy_engine
)

save_csv_data(transformed_df, 'output.csv')
```

---

## 🤖 Machine Learning Classifier

The framework includes an **optional ML-based classifier** that trains on your metadata to improve sensitivity classification accuracy.

### Quick Start with ML

#### 1. Train the ML Model (First Time)

```bash
python train_ml_classifier.py
```

This automatically:
- Scans all YAML files in `table_structure/metadata/`
- Extracts labeled training data from column names and descriptions
- Trains a Logistic Regression + TF-IDF model
- Saves to `models/sensitivity_classifier.pkl`
- Reports training accuracy

**Output:**
```
Training complete! Accuracy: 96.4% (27/28 correct)
Model saved to: models/sensitivity_classifier.pkl

Top learned features:
1. transaction (importance: 0.3476)
2. medication (importance: 0.3078)
3. diagnosis (importance: 0.2902)
```

#### 2. Use the ML Classifier

```python
from privacy_aware_transform.classifier import SensitivityClassifier

# Automatically loads trained model
classifier = SensitivityClassifier(use_ml=True)

# Classify columns (now uses both rules + ML for better accuracy)
classifications = classifier.classify_table(table_meta.columns)
```

#### 3. Test and Verify

```bash
python test_ml_classifier.py
```

This shows:
- Comparison between rule-based and ML predictions
- Classification agreement percentage
- Confidence scores for each method

### How ML Classification Works

The ML classifier uses a **two-stage approach**:

1. **Rule-Based (Primary - Fast)**
   - Pattern matching on column names/descriptions
   - Confidence: 0.70-0.90
   - Fast, interpretable, no training required

2. **ML-Based (Secondary - Accurate)**
   - Trained on your metadata files
   - Blends with rules when confidence < 0.8
   - Confidence: 0.38-0.90
   - More accurate on edge cases

### Adding More Training Data

The ML model is incremental-friendly:

```bash
# 1. Add new YAML files to table_structure/metadata/
#    (e.g., employees.yaml, products.yaml, etc.)

# 2. Retrain
python train_ml_classifier.py

# 3. Model now improves with more metadata
```

**Recommended Growth Path:**
- Start: 28 samples (3 tables) → 96% accuracy
- Target: 50-75 samples (5-7 tables) → 97-98% accuracy
- Optimal: 100+ samples (10+ tables) → 98%+ accuracy

### ML Model Specifications

- **Algorithm**: Logistic Regression
- **Features**: TF-IDF on column name + description + data type
- **Training Data**: Automatically labeled from metadata patterns
- **Serialization**: Pickle (models/sensitivity_classifier.pkl)
- **Update Frequency**: Retrain when adding new metadata

### For Detailed ML Guidance

See **[ML_TRAINING_GUIDE.md](ML_TRAINING_GUIDE.md)** for:
- Feature engineering details
- Training data requirements
- Performance optimization
- Troubleshooting
- Best practices

---

## 📋 Metadata YAML Format

Metadata is defined in YAML files located in `table_structure/metadata/`. Each YAML file represents one table.

**Example: `customers.yaml`**
```yaml
table_name: customers
database: main_db
description: "Customer personal information and contact details"
owner: "data_governance_team"

columns:
  - name: customer_id
    data_type: int
    description: "Unique customer identifier (primary key)"
    nullable: false
    is_key: true
    examples: ["1", "2", "3"]

  - name: first_name
    data_type: string
    description: "Customer first name (PII)"
    nullable: false
    is_key: false
    examples: ["John", "Jane"]

  - name: email
    data_type: string
    description: "Customer email address (PII)"
    nullable: true
    is_key: false
    examples: ["john@example.com", "jane@example.com"]

  - name: registration_date
    data_type: date
    description: "Account registration date (Non-Sensitive)"
    nullable: false
    is_key: false
    examples: ["2020-01-01", "2021-06-15"]
```

---

## 🔐 Sensitivity Classification

The framework automatically classifies columns into sensitivity levels based on metadata (column names and descriptions):

| Class | Definition | Examples |
|-------|-----------|----------|
| **PII** | Personally Identifiable Information | first_name, email, phone, ssn, address, dob |
| **PHI** | Protected Health Information | diagnosis, medication, patient_name, medical_record_number |
| **Sensitive** | Financial or location data | salary, amount, zip_code, city, credit_card |
| **Non-Sensitive** | Public or non-sensitive data | registration_date, status, product_name, visit_count |

**Classification Method:**
- Rule-based pattern matching on column names and descriptions (high precision, fast)
- Optional ML-based classification (LogisticRegression + TF-IDF) for training on labeled data

---

## 🛡️ Privacy Transformations

The framework supports four consumer types with different privacy-utility tradeoffs:

### Consumer Types & Default Transformations

| Sensitivity | Internal Analyst | External Partner | Reporting | Public |
|-------------|-----------------|-----------------|-----------|--------|
| **PII** | Tokenize | Hash | Mask | Hash |
| **PHI** | Tokenize | Hash | Mask | Hash |
| **Sensitive** | Mask (keep ends) | Mask (full) | Aggregate | Aggregate |
| **Non-Sensitive** | Keep | Keep | Keep | Keep |

### Transformation Techniques

1. **Keep**: Return data unchanged (pass-through)
2. **Mask**: Replace characters with mask character (e.g., `john@example.com` → `j**@****.com`)
3. **Hash**: Apply SHA256 or other cryptographic hash (irreversible)
4. **Tokenize**: Consistent pseudonymization using keyed HMAC (deterministic but non-reversible without key)
5. **Aggregate**: Count or group data (for reporting purposes)

---

## 🔧 Core Modules API

### 1. `metadata.py`
- **MetadataLoader**: Load table metadata from YAML files
- **SyntheticMetadataGenerator**: Generate sample metadata for testing

### 2. `classifier.py`
- **SensitivityClassifier**: Rule-based + optional ML classification
- **ClassificationResult**: Result object with class, confidence, and reasoning

### 3. `policy.py`
- **PolicyEngine**: Manages consumer policies and transformation rules
- **ConsumerPolicy**: Maps (sensitivity, consumer) → transformation rule

### 4. `transforms.py`
- **TransformationEngine**: Orchestrates transformations
- **MaskingTransformer**, **HashingTransformer**, **TokenizationTransformer**: Individual transformations

### 5. `utils.py`
- Utility functions: CSV I/O, DataFrame transformations, reporting

---

## 📊 Example Output

After running `examples/example.py`, the framework generates transformed datasets:

```
data/synthetic/
├── customers.csv (original)
├── patient_records.csv (original)
├── sales_transactions.csv (original)
├── internal_analyst/
│   ├── customers_transformed.csv
│   ├── patient_records_transformed.csv
│   └── sales_transactions_transformed.csv
└── external_partner/
    ├── customers_transformed.csv
    ├── ...
```

---

## 📚 Limitations & Future Work

### Current Limitations
1. **Aggregate transformations** are framework-ready but not fully implemented
2. **ML-based classification** requires manual training on labeled data
3. **No reversibility** support (transformations are one-way by design)
4. **Limited to local execution** (AWS or cloud integration not included)
5. **No audit logging** of transformations
6. **No differential privacy** support

### Future Enhancements
- [ ] Differential privacy mechanisms (Laplace noise, etc.)
- [ ] Advanced aggregation strategies (grouping, binning, etc.)
- [ ] Pre-trained ML models for classification
- [ ] Integration with data lineage tracking
- [ ] Audit and compliance logging
- [ ] Real-time streaming data support
- [ ] Performance benchmarking on large datasets
- [ ] Privacy budget management and tracking

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## ❓ FAQ

**Q: How do I add my own table metadata?**  
A: Create a new YAML file in `table_structure/metadata/` following the format in `customers.yaml`.

**Q: Can I use transformations reversibly?**  
A: No, transformations are intentionally one-way for privacy preservation.

**Q: How does tokenization work?**  
A: Tokenization uses a secret key (HMAC-SHA256) to create deterministic pseudonyms.

---

## ⚖️ License

Licensed under Apache License 2.0. See LICENSE file for details.

---

**Last Updated:** January 2025
