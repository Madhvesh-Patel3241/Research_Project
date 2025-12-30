"""
UTILITY FUNCTIONS
=================
Shared helper functions for all notebooks
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Feature names
FEATURE_NAMES = [
    'gas_price', 'value', 'gas_limit', 'data_size', 'nonce_conflict',
    'nonce_gap', 'gas_differential', 'gas_volatility', 'submission_frequency',
    'arrival_interval', 'balance_adequacy', 'recipient_similarity'
]

# Class names
CLASS_NAMES = {
    0: 'Normal/Legitimate RBF',
    1: 'Basic Double Spend',
    2: 'Race Attack (Front-running)',
    3: 'Volume Attack (DDoS)',
    4: 'Hybrid Sophisticated'
}

def create_directories():
    """Create necessary directories for outputs"""
    import os
    directories = ['results', 'models', 'data']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✓ Directories created: results/, models/, data/")

def load_dataset(filepath='dataset_part7.csv'):
    """Load and validate dataset"""
    df = pd.read_csv(filepath)
    
    # Validation
    assert all(feat in df.columns for feat in FEATURE_NAMES), "Missing features"
    assert 'attack_type' in df.columns, "Missing target column"
    assert df['attack_type'].nunique() == 5, "Expected 5 classes"
    assert df.isnull().sum().sum() == 0, "Dataset has missing values"
    
    print(f"✓ Dataset loaded: {df.shape}")
    return df

def plot_confusion_matrix_custom(y_true, y_pred, title, save_path=None):
    """Create a custom confusion matrix plot"""
    from sklearn.metrics import confusion_matrix
    
    cm = confusion_matrix(y_true, y_pred)
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm_normalized, annot=True, fmt='.1f', cmap='Blues',
                xticklabels=[CLASS_NAMES[i] for i in range(5)],
                yticklabels=[CLASS_NAMES[i] for i in range(5)],
                ax=ax, cbar_kws={'label': 'Percentage (%)'})
    
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.set_xlabel('Predicted Class', fontweight='bold')
    ax.set_ylabel('True Class', fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()
    
    return cm

def calculate_metrics(y_true, y_pred):
    """Calculate all relevant metrics"""
    return {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
        'Recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
        'F1-Score': f1_score(y_true, y_pred, average='weighted', zero_division=0)
    }

def compare_models(results_dict):
    """Create comparison dataframe from results dictionary"""
    comparison_data = []
    
    for model_name, metrics in results_dict.items():
        row = {'Model': model_name}
        row.update(metrics)
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    df = df.sort_values('F1-Score', ascending=False)
    return df

def plot_metric_comparison(df, metric, title, save_path=None):
    """Plot bar chart for a specific metric"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = ax.bar(range(len(df)), df[metric],
                   color=sns.color_palette("Set2", len(df)),
                   edgecolor='black', linewidth=1.5)
    
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['Model'], rotation=45, ha='right')
    ax.set_ylabel(metric, fontweight='bold', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def generate_latex_table(df, caption="Model Comparison", label="tab:comparison"):
    """Generate LaTeX table code"""
    latex_code = f"""
\\begin{{table}}[htbp]
\\centering
\\caption{{{caption}}}
\\label{{{label}}}
\\begin{{tabular}}{{l|cccc}}
\\hline
\\textbf{{Model}} & \\textbf{{Accuracy}} & \\textbf{{Precision}} & \\textbf{{Recall}} & \\textbf{{F1-Score}} \\\\
\\hline
"""
    
    for _, row in df.iterrows():
        latex_code += f"{row['Model']} & {row['Accuracy']:.4f} & {row['Precision']:.4f} & {row['Recall']:.4f} & {row['F1-Score']:.4f} \\\\\n"
    
    latex_code += """\\hline
\\end{tabular}
\\end{table}
"""
    
    return latex_code

def print_section_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def cohen_d(group1, group2):
    """Calculate Cohen's d effect size"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def bootstrap_confidence_interval(y_true, y_pred, metric_func, n_bootstrap=1000, ci=0.95):
    """Calculate bootstrap confidence interval for a metric"""
    scores = []
    n_samples = len(y_true)
    
    for _ in range(n_bootstrap):
        indices = np.random.choice(n_samples, n_samples, replace=True)
        score = metric_func(y_true[indices], y_pred[indices])
        scores.append(score)
    
    alpha = (1 - ci) / 2
    lower = np.percentile(scores, alpha * 100)
    upper = np.percentile(scores, (1 - alpha) * 100)
    
    return np.mean(scores), lower, upper

if __name__ == "__main__":
    print("Utility functions loaded successfully!")
    print(f"Available features: {len(FEATURE_NAMES)}")
    print(f"Number of classes: {len(CLASS_NAMES)}")
    create_directories()
