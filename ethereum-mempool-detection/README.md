# Ethereum Mempool Attack Detection - Q1 Journal Submission
## Real-time Pre-mining Attack Detection using Machine Learning

---

## 📁 Project Structure

```
ethereum-mempool-detection/
├── README.md                              # This file
├── utils.py                               # Shared utility functions
├── dataset_part7.csv                      # Your collected dataset
│
├── 01_EDA_Preprocessing.ipynb             # Exploratory Data Analysis
├── 02_Classical_ML.ipynb                  # XGBoost, RF, SVM models
├── 03_Deep_Learning.ipynb                 # MLP, CNN, LSTM, Transformer
├── 04_Final_Comparison.ipynb              # Unified comparison & XAI
│
├── data/                                  # Preprocessed data
│   ├── X_scaled.npy
│   ├── y.npy
│   └── X_raw.npy
│
├── models/                                # Trained models
│   ├── xgboost_proposed.pkl
│   ├── random_forest.pkl
│   ├── svm_linear.pkl
│   ├── svm_rbf.pkl
│   ├── deep_mlp.h5
│   ├── 1d_cnn.h5
│   ├── bilstm.h5
│   ├── transformer.h5
│   └── scaler.pkl
│
└── results/                               # All figures and tables
    ├── 01_class_distribution.png
    ├── 02_feature_correlation.png
    ├── ... (27 artifacts total)
    └── 27_performance_complexity_tradeoff.png
```

---

## 🚀 Quick Start

### **Step 1: Environment Setup**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install numpy pandas matplotlib seaborn scikit-learn xgboost
pip install tensorflow keras shap lime scikit-optimize statsmodels
pip install scipy joblib
```

### **Step 2: Run the Notebooks in Order**

```bash
# 1. Exploratory Data Analysis (15 minutes)
jupyter notebook 01_EDA_Preprocessing.ipynb

# 2. Classical ML Models (20 minutes)
jupyter notebook 02_Classical_ML.ipynb

# 3. Deep Learning Models (30-45 minutes depending on GPU)
jupyter notebook 03_Deep_Learning.ipynb

# 4. Final Comparison & Explainability (15 minutes)
jupyter notebook 04_Final_Comparison.ipynb
```

---

## 📊 Dataset Information

**Source**: Ganache simulation with Polymorphic Botnet  
**Size**: ~100,000 transactions  
**Features**: 13 engineered features  
**Classes**: 5 (0=Normal, 1=Double Spend, 2=Race, 3=Volume, 4=Hybrid)

### **Features (13 total)**
1. `gas_price` - Transaction gas price
2. `value` - ETH value transferred
3. `gas_limit` - Gas limit set
4. `data_size` - Size of transaction data
5. `nonce_conflict` - Binary indicator of nonce reuse
6. `nonce_gap` - Gap between nonce and on-chain nonce
7. `gas_differential` - Gas price difference with conflicting tx
8. `gas_volatility` - Ratio of gas prices
9. `submission_frequency` - Transactions per 10s window
10. `arrival_interval` - Time between conflicting txs
11. `balance_adequacy` - Sufficient balance indicator
12. `recipient_similarity` - Same recipient as conflicting tx
13. `is_rbf` - Legitimate Replace-By-Fee indicator

---

## 🤖 Models Implemented (7 Total)

### **Classical Machine Learning (4 models)**
1. **XGBoost** (Proposed) - Gradient boosting with Bayesian optimization
2. **Random Forest** - Ensemble of decision trees
3. **SVM (Linear)** - Linear kernel support vector machine
4. **SVM (RBF)** - Radial basis function kernel

### **Deep Learning (4 models)**
5. **Deep MLP** - 4-layer perceptron (128→64→32→5)
6. **1D-CNN** - Convolutional neural network
7. **BiLSTM** - Bidirectional long short-term memory
8. **Transformer** - Multi-head attention mechanism

---

## 📈 Expected Results

Based on similar mempool detection research:

| Model | Accuracy | F1-Score | Inference (ms) |
|-------|----------|----------|----------------|
| XGBoost (Proposed) | 0.97-0.99 | 0.97-0.99 | 0.5-2.0 |
| Random Forest | 0.95-0.97 | 0.95-0.97 | 1.0-3.0 |
| SVM (RBF) | 0.85-0.90 | 0.85-0.90 | 5.0-10.0 |
| Deep MLP | 0.94-0.96 | 0.94-0.96 | 2.0-4.0 |
| BiLSTM | 0.93-0.95 | 0.93-0.95 | 5.0-8.0 |
| Transformer | 0.94-0.96 | 0.94-0.96 | 8.0-12.0 |

**Real-time Threshold**: < 10ms for production deployment

---

## 📑 Generated Artifacts (27 Total)

### **Notebook 1: EDA (6 figures + 2 CSV)**
- `01_class_distribution.png` - Class balance analysis
- `02_feature_correlation.png` - Correlation heatmap
- `03_vif_analysis.png` - Multicollinearity check
- `04_feature_distributions.png` - Feature histograms by class
- `05_anova_feature_importance.png` - Univariate importance
- `06_boxplots_top_features.png` - Box plots for top features
- `01_summary_statistics.csv` - Descriptive stats table
- `03_vif_scores.csv` - VIF values

### **Notebook 2: Classical ML (7 figures + 2 CSV)**
- `07_xgboost_optimization.csv` - Bayesian optimization log
- `08_cv_results_classical.csv` - Cross-validation results
- `09_learning_curves.png` - Data efficiency analysis
- `10_confusion_matrices_classical.png` - 4 confusion matrices
- `11_calibration_curves.png` - Probability calibration
- `12_feature_importance_classical.png` - XGB & RF importance
- `13_classical_model_comparison.csv` - Metrics table
- `14_classical_performance_comparison.png` - Bar charts

### **Notebook 3: Deep Learning (4 figures + 1 CSV)**
- `15_dl_training_curves.png` - Loss & accuracy over epochs
- `16_confusion_matrices_dl.png` - 4 confusion matrices
- `17_dl_model_comparison.csv` - DL metrics table
- `18_dl_performance_comparison.png` - Performance bars

### **Notebook 4: Final Comparison (9 figures + 2 CSV)**
- `19_final_model_comparison.csv` - All 7 models compared
- `20_unified_confusion_matrices.png` - 8 confusion matrices
- `21_roc_auc_all_models.png` - ROC curves (one-vs-rest)
- `22_precision_recall_curves.png` - PR curves
- `23_mcnemar_test_results.csv` - Statistical significance
- `24_shap_beeswarm.png` - SHAP feature importance
- `25_shap_bar.png` - SHAP mean absolute values
- `26_lime_explanations.png` - LIME local explanations
- `27_performance_complexity_tradeoff.png` - Accuracy vs complexity

---

## 🎓 For Q1 Journal Submission

### **Section-by-Section Usage**

**Introduction**
- Use `01_class_distribution.png` to show dataset balance
- Cite feature engineering process (13 features)

**Methodology**
- Reference system architecture (Ganache → Detector → ML)
- Include pseudocode from detector script
- Mention Sim2Real noise injection

**Experiments**
- **Table 1**: Use `01_summary_statistics.csv`
- **Table 2**: Use `19_final_model_comparison.csv`
- **Figure 1**: `05_anova_feature_importance.png`
- **Figure 2**: `20_unified_confusion_matrices.png`
- **Figure 3**: `21_roc_auc_all_models.png`
- **Figure 4**: `24_shap_beeswarm.png`

**Results**
- Lead with XGBoost superiority + McNemar's test (`23_mcnemar_test_results.csv`)
- Show learning curves (`09_learning_curves.png`) to prove data efficiency
- Discuss inference time for real-time capability (`27_performance_complexity_tradeoff.png`)

**Discussion**
- Explain SHAP findings: which features matter most
- Address why SVM fails (non-linear patterns)
- Discuss DL vs classical ML trade-offs

---

## 🔧 Customization

### **Change Dataset Path**
Edit line 66 in `01_EDA_Preprocessing.ipynb`:
```python
df = pd.read_csv('your_dataset.csv')
```

### **Adjust Hyperparameters**
- XGBoost: `02_Classical_ML.ipynb` → Section 3 (Bayesian search space)
- Deep Learning: `03_Deep_Learning.ipynb` → Section 3 (model architectures)

### **Add More Models**
Follow the pattern in existing notebooks:
1. Define model in Section 3
2. Add to `models` dictionary
3. Rest of pipeline auto-handles it

---

## 📊 LaTeX Table Generation

Use the utility function to generate LaTeX code:

```python
from utils import generate_latex_table
import pandas as pd

df = pd.read_csv('results/19_final_model_comparison.csv')
latex_code = generate_latex_table(df, 
    caption="Comprehensive Model Comparison", 
    label="tab:final_comparison")
print(latex_code)
```

Copy-paste into your paper!

---

## 🐛 Troubleshooting

### **Issue: "Module not found"**
```bash
pip install <missing_module>
```

### **Issue: TensorFlow GPU not detected**
```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
# If empty, TensorFlow will use CPU (slower but works)
```

### **Issue: SHAP takes too long**
Reduce sample size in `04_Final_Comparison.ipynb`:
```python
sample_size = 500  # Instead of 1000
```

### **Issue: Memory error with deep learning**
Reduce batch size in `03_Deep_Learning.ipynb`:
```python
batch_size=64  # Instead of 128
```

---

## 📚 Citations for Paper

**Machine Learning Frameworks**
- Scikit-learn: Pedregosa et al. (2011)
- XGBoost: Chen & Guestrin (2016)
- TensorFlow: Abadi et al. (2016)

**Explainability**
- SHAP: Lundberg & Lee (2017)
- LIME: Ribeiro et al. (2016)

**Blockchain Security**
- Ethereum Yellow Paper: Wood (2014)
- Front-running attacks: Daian et al. (2020)

---

## 🎯 Performance Benchmarks

**Hardware Used**
- CPU: [Your CPU]
- RAM: [Your RAM]
- GPU: [Your GPU or None]

**Training Times** (approximate)
- XGBoost: 30-60 seconds
- Random Forest: 45-90 seconds
- SVM: 5-10 minutes
- Deep MLP: 5-10 minutes
- BiLSTM: 10-15 minutes
- Transformer: 10-20 minutes

---

## 📧 Contact

For questions about this implementation:
- Check code comments in each notebook
- Review error messages carefully
- Ensure all dependencies are installed

---

## ✅ Pre-Submission Checklist

Before submitting to journal:

- [ ] All 4 notebooks run without errors
- [ ] 27 artifacts generated in `results/` folder
- [ ] Models saved in `models/` folder
- [ ] Cross-validation results show consistent performance
- [ ] Statistical significance tests pass (p < 0.05)
- [ ] Real-time inference requirement met (< 10ms)
- [ ] SHAP analysis shows interpretable features
- [ ] Confusion matrices show balanced performance across classes
- [ ] LaTeX tables generated and formatted
- [ ] Paper draft references all figures/tables correctly

---

## 🚀 Advanced Usage

### **Cross-Dataset Validation**
Run detector on a new Ganache instance, collect fresh data, then:
```python
# In 04_Final_Comparison.ipynb
X_new = np.load('data/X_new_scaled.npy')
y_new = np.load('data/y_new.npy')

# Test XGBoost on new data
xgb_model = joblib.load('models/xgboost_proposed.pkl')
y_pred_new = xgb_model.predict(X_new)
print(f"Cross-dataset accuracy: {accuracy_score(y_new, y_pred_new):.4f}")
```

### **Adversarial Robustness Test**
```python
# Add to 04_Final_Comparison.ipynb
from sklearn.preprocessing import StandardScaler

# Add Gaussian noise
epsilon = 0.1
X_adversarial = X_test + epsilon * np.random.randn(*X_test.shape)

# Test robustness
y_pred_adv = xgb_model.predict(X_adversarial)
print(f"Adversarial accuracy: {accuracy_score(y_test, y_pred_adv):.4f}")
```

---

## 📖 Additional Resources

- **Ethereum Documentation**: https://ethereum.org/en/developers/docs/
- **XGBoost Tuning Guide**: https://xgboost.readthedocs.io/
- **SHAP Documentation**: https://shap.readthedocs.io/
- **Scikit-learn User Guide**: https://scikit-learn.org/stable/user_guide.html

---

**Good luck with your Q1 journal submission! 🎓**
