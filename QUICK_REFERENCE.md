# Quick Reference Card

## 🚀 Start Here (30 seconds)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run example
python examples/example.py

# 3. Check output
ls data/synthetic/
```

---

## 📚 Documentation Quick Links

| Need | Document | Section |
|------|----------|---------|
| Overview | README.md | Key Objectives |
| Installation | README.md | Installation |
| ML guide | ML_TRAINING_GUIDE.md | Quick Start |
| Code details | IMPLEMENTATION_SUMMARY.md | Architecture |
| Navigation | DOCUMENTATION_INDEX.md | Use Case 1-6 |
| Complete info | COMPLETION_SUMMARY.md | Full details |

---

## 🤖 ML Classifier in 3 Commands

```bash
# 1. Train (2-5 seconds)
python train_ml_classifier.py

# 2. Test (instantly)
python test_ml_classifier.py

# 3. Use
# In your Python code:
from privacy_aware_transform.classifier import SensitivityClassifier
classifier = SensitivityClassifier(use_ml=True)
```

---

## 📋 Common Tasks

### Task 1: Understand the System
```
1. Read: README.md (10 min)
2. Run:  python examples/example.py (2 min)
3. Done!
```

### Task 2: Train ML Model
```
1. Run: python train_ml_classifier.py
2. Read: ML_TRAINING_GUIDE.md (10 min)
3. Done!
```

### Task 3: Use in Code
```python
from privacy_aware_transform.classifier import SensitivityClassifier
from privacy_aware_transform.transforms import TransformationEngine

classifier = SensitivityClassifier(use_ml=True)
engine = TransformationEngine()

# Classify
result = classifier.classify_column(column_metadata)
print(result.class)          # "PII", "PHI", "Sensitive", "Non-Sensitive"
print(result.confidence)     # 0.0-1.0
print(result.method)         # "rule-based", "ml", "blended"

# Transform
transformer = engine.get_transformer(sensitivity="PII", consumer="external_partner")
transformed = transformer.transform("john@example.com")
```

### Task 4: Add Your Data
```
1. Create: table_structure/metadata/my_table.yaml
2. Run:    python train_ml_classifier.py
3. Use:    SensitivityClassifier(use_ml=True)
```

### Task 5: Extend Framework
```
1. Read: IMPLEMENTATION_SUMMARY.md
2. Pick: Extension point (Transformer, Policy, etc.)
3. Code: Custom class
4. Test: Use existing test infrastructure
```

---

## 🔧 CLI Commands

```bash
# List available policies
python -m privacy_aware_transform.cli list-policies

# Classify columns
python -m privacy_aware_transform.cli classify --metadata-dir table_structure/metadata

# Transform data
python -m privacy_aware_transform.cli transform \
  --metadata-file table_structure/metadata/customers.yaml \
  --data-file data/synthetic/customers.csv \
  --consumer-type internal_analyst \
  --output output.csv

# Get help
python -m privacy_aware_transform.cli help
```

---

## 🎯 Key Classes

### SensitivityClassifier
```python
from privacy_aware_transform.classifier import SensitivityClassifier

# Create (auto-loads trained model if use_ml=True)
classifier = SensitivityClassifier(use_ml=True)

# Classify single column
result = classifier.classify_column(column_metadata)
# → ClassificationResult(class, confidence, reasoning, method)

# Classify all columns in table
classifications = classifier.classify_table(table_metadata.columns)
# → List[ClassificationResult]
```

### TransformationEngine
```python
from privacy_aware_transform.transforms import TransformationEngine

engine = TransformationEngine()

# Get transformer
transformer = engine.get_transformer(
    sensitivity="PII",
    consumer_type="external_partner",
    data_type="string"
)

# Transform value
result = transformer.transform("john@example.com")
# → "j***@***.com" (mask), "a3f2b1c..." (hash), etc.
```

### PolicyEngine
```python
from privacy_aware_transform.policy import PolicyEngine

engine = PolicyEngine()

# Get transformation rule
rule = engine.get_transformation_rule(
    sensitivity="PII",
    consumer_type="reporting"
)
# → TransformationRule(transformation_type, parameters)
```

### MetadataLoader
```python
from privacy_aware_transform.metadata import MetadataLoader

loader = MetadataLoader('table_structure/metadata')
table_meta = loader.load_table_metadata('customers.yaml')
# → TableMetadata(table_name, columns, description, etc.)
```

---

## 📊 File Locations

```
Code:
  src/privacy_aware_transform/
    ├── classifier.py        (Sensitivity classification)
    ├── ml_classifier.py     (ML model training)
    ├── transforms.py        (Transformation implementations)
    ├── policy.py            (Consumer policies)
    ├── metadata.py          (Metadata loading)
    └── cli.py               (Command-line interface)

Data:
  table_structure/metadata/   (Your metadata YAML files)
  data/synthetic/             (Generated sample data)
  models/                     (Trained ML models)

Scripts:
  train_ml_classifier.py      (Train ML model)
  test_ml_classifier.py       (Test classifier)
  examples/example.py         (Full pipeline demo)
```

---

## 🔍 Sensitivity Classes

| Class | Description | Examples |
|-------|-------------|----------|
| **PII** | Personally Identifiable Info | name, email, phone, ssn, address, DOB |
| **PHI** | Protected Health Info | diagnosis, medication, medical_record, patient |
| **Sensitive** | Financial/Location | salary, credit_card, zip_code, city |
| **Non-Sensitive** | Public data | registration_date, status, product_name |

---

## 🛡️ Transformations

| Type | Input | Output | Use |
|------|-------|--------|-----|
| **Keep** | `john@example.com` | `john@example.com` | Non-sensitive data |
| **Mask** | `john@example.com` | `j***@***.com` | Keep partial data |
| **Hash** | `john@example.com` | `a3f2b1c...` | Irreversible |
| **Tokenize** | `john@example.com` | `USR_12345` | Consistent replacement |

---

## 👥 Consumer Types

| Consumer | Privacy Level | Use Case |
|----------|--------------|----------|
| **internal_analyst** | Low | Trusted internal teams |
| **external_partner** | Medium | External companies |
| **reporting** | High | Aggregate reporting |
| **public** | Highest | Public data sharing |

---

## ⚙️ Configuration

### Use ML Classification
```python
classifier = SensitivityClassifier(use_ml=True)
```

### Use Only Rules
```python
classifier = SensitivityClassifier(use_ml=False)
```

### Custom Model Path
```python
classifier = SensitivityClassifier(
    use_ml=True,
    ml_model_path='/path/to/model.pkl'
)
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Model not found | Run `python train_ml_classifier.py` |
| Import errors | Run `pip install -r requirements.txt` |
| Low accuracy | Add more metadata files (YAML), retrain |
| Rule/ML disagree | Expected with small datasets, add more data |

---

## 📖 Documentation Map

```
START: README.md (10 min)
  ↓
CHOOSE YOUR PATH:
  → ML User? → ML_TRAINING_GUIDE.md (15 min)
  → Developer? → IMPLEMENTATION_SUMMARY.md (30 min)
  → New? → DOCUMENTATION_INDEX.md
  → Quick? → COMPLETION_SUMMARY.md (5 min)
```

---

## ✅ Verification

Run to verify installation:
```bash
python test_quick.py              # Quick test (2 sec)
python test_ml_classifier.py      # ML test (3 sec)
python examples/example.py        # Full demo (5 sec)
```

All should complete without errors. ✓

---

## 🎯 Quick Start (5 minutes)

```bash
# 1. Install (1 min)
pip install -r requirements.txt

# 2. Run example (1 min)
python examples/example.py

# 3. Train ML (1 min)
python train_ml_classifier.py

# 4. Test (1 min)
python test_ml_classifier.py

# 5. Done! (1 min to read first docs)
```

---

## 📞 Find Answers

| Question | Look Here |
|----------|-----------|
| How do I install? | README.md → Installation |
| How do I run example? | README.md → Quick Start |
| How do I train ML? | ML_TRAINING_GUIDE.md → Quick Start |
| How do I use in code? | README.md → Programmatic Usage |
| How do I add data? | ML_TRAINING_GUIDE.md → Adding More Data |
| How does it work? | README.md → Architecture |
| What are the limitations? | README.md → Limitations |
| How do I extend? | IMPLEMENTATION_SUMMARY.md → Extension Points |
| Where do I navigate? | DOCUMENTATION_INDEX.md |

---

## 🚀 Next Steps

1. ✓ Read this card
2. → Run: `python examples/example.py`
3. → Read: [README.md](README.md)
4. → Run: `python train_ml_classifier.py`
5. → Read: [ML_TRAINING_GUIDE.md](ML_TRAINING_GUIDE.md)
6. → Use in your code!

---

**Version**: 1.0.0  
**Status**: ✅ Ready to Use  
**Last Updated**: January 4, 2025
