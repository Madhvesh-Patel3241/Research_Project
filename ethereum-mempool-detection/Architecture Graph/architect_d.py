import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_system_architecture_matplotlib():
    """
    Creates system architecture using matplotlib for maximum control
    """
    
    fig, ax = plt.subplots(figsize=(14, 18), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 20)
    ax.axis('off')
    
    # Color scheme (professional journal colors)
    colors = {
        'data': '#3498DB',
        'feature': '#1ABC9C',
        'classical': '#9B59B6',
        'deep': '#8E44AD',
        'validation': '#F39C12',
        'deployment': '#E74C3C',
        'text': '#2C3E50'
    }
    
    # Helper function to create rounded boxes
    def create_box(ax, x, y, width, height, text, color, text_color='white'):
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            facecolor=color, edgecolor='black',
                            linewidth=2, alpha=0.9)
        ax.add_patch(box)
        ax.text(x + width/2, y + height/2, text,
               ha='center', va='center', fontsize=10,
               color=text_color, fontweight='bold',
               wrap=True)
    
    # Helper function for arrows
    def create_arrow(ax, x1, y1, x2, y2, label='', style='solid'):
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=20,
                               linewidth=2, color='#34495E',
                               linestyle=style,
                               alpha=0.7)
        ax.add_patch(arrow)
        if label:
            mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mid_x + 0.3, mid_y, label, fontsize=8,
                   color='#566573', style='italic')
    
    # ==========================================
    # LAYER 1: DATA COLLECTION (Y: 18-20)
    # ==========================================
    ax.text(5, 19.5, '1. DATA COLLECTION MODULE',
           ha='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#ECF0F1', 
                    edgecolor=colors['data'], linewidth=2))
    
    create_box(ax, 1, 17.5, 2.5, 1, 'Ganache v7.4.0\nTestnet\n(103,734 tx)',
              colors['data'])
    create_box(ax, 4, 17.5, 2.5, 1, 'Mempool\nMonitor\n(15 tx/s)',
              colors['data'])
    create_box(ax, 7, 17.5, 2.5, 1, 'Transaction\nStream\n(5 classes)',
              colors['data'])
    
    create_arrow(ax, 2.25, 17.5, 4, 18, 'Block gen')
    create_arrow(ax, 5.25, 17.5, 7, 18, 'Broadcast')
    
    # ==========================================
    # LAYER 2: FEATURE ENGINEERING (Y: 14-17)
    # ==========================================
    ax.text(5, 16.5, '2. FEATURE ENGINEERING MODULE',
           ha='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#ECF0F1',
                    edgecolor=colors['feature'], linewidth=2))
    
    create_box(ax, 3.5, 15, 3, 1, 'Feature Extractor\n(12 features)',
              colors['feature'])
    
    # Sub-features
    create_box(ax, 0.5, 14, 2, 0.6, 'Nonce\n(conflict, gap)',
              colors['feature'], text_color='black')
    create_box(ax, 3, 14, 2, 0.6, 'Gas\n(price, diff)',
              colors['feature'], text_color='black')
    create_box(ax, 5.5, 14, 2, 0.6, 'Timing\n(freq, interval)',
              colors['feature'], text_color='black')
    create_box(ax, 8, 14, 2, 0.6, 'Transaction\n(value, size)',
              colors['feature'], text_color='black')
    
    create_box(ax, 3.5, 13, 3, 0.8, 'Z-Score Standardization',
              colors['feature'])
    
    # Arrows
    create_arrow(ax, 8.25, 17.5, 5, 16, 'Raw tx')
    create_arrow(ax, 5, 15, 1.5, 14.3, style='dashed')
    create_arrow(ax, 5, 15, 4, 14.3, style='dashed')
    create_arrow(ax, 5, 15, 6.5, 14.3, style='dashed')
    create_arrow(ax, 5, 15, 9, 14.3, style='dashed')
    
    create_arrow(ax, 1.5, 14, 4, 13.8, style='dashed')
    create_arrow(ax, 4, 14, 5, 13.8, style='dashed')
    create_arrow(ax, 6.5, 14, 5.5, 13.8, style='dashed')
    create_arrow(ax, 9, 14, 6, 13.8, style='dashed')
    
    # ==========================================
    # LAYER 3: MODEL TRAINING (Y: 8-12.5)
    # ==========================================
    ax.text(5, 12.5, '3. MODEL TRAINING FRAMEWORK',
           ha='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#ECF0F1',
                    edgecolor=colors['classical'], linewidth=2))
    
    # Classical ML
    ax.text(2.5, 11.8, 'Classical ML', ha='center', fontsize=10,
           style='italic', color=colors['classical'])
    create_box(ax, 1, 10.8, 2, 0.8, 'XGBoost\n96.48%',
              colors['classical'])
    create_box(ax, 1, 9.8, 2, 0.8, 'Random Forest\n96.48%',
              colors['classical'])
    create_box(ax, 1, 8.8, 2, 0.8, 'SVM\n61-82%',
              colors['classical'])
    
    # Deep Learning
    ax.text(7.5, 11.8, 'Deep Learning', ha='center', fontsize=10,
           style='italic', color=colors['deep'])
    create_box(ax, 6.5, 10.8, 2, 0.8, 'MLP\n96.49%',
              colors['deep'])
    create_box(ax, 6.5, 9.8, 2, 0.8, '1D-CNN\n96.46%',
              colors['deep'])
    create_box(ax, 6.5, 8.8, 2, 0.8, 'BiLSTM\n96.49%',
              colors['deep'])
    create_box(ax, 6.5, 7.8, 2, 0.8, 'Transformer\n96.49%',
              colors['deep'])
    
    # Arrows from feature to models
    create_arrow(ax, 5, 13, 2, 11.6, '80/20 split')
    for y_pos in [10.8, 9.8, 8.8, 7.8]:
        create_arrow(ax, 5, 13, 7.5, y_pos + 0.4, style='dashed')
    
    # ==========================================
    # LAYER 4: VALIDATION (Y: 5-7.5)
    # ==========================================
    ax.text(5, 7.5, '4. MODEL SELECTION & VALIDATION',
           ha='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#ECF0F1',
                    edgecolor=colors['validation'], linewidth=2))
    
    create_box(ax, 1, 6, 2.5, 0.8, '5-Fold CV',
              colors['validation'], text_color='black')
    create_box(ax, 4, 6, 2.5, 0.8, "McNemar's Test",
              colors['validation'], text_color='black')
    create_box(ax, 7, 6, 2.5, 0.8, 'Feature Ablation',
              colors['validation'], text_color='black')
    
    create_box(ax, 2.5, 5, 5, 0.8, 'XGBoost Selected (96.48%, 0.0035ms)',
              colors['validation'], text_color='white')
    
    # Arrows
    for x_pos in [2, 7.5]:
        create_arrow(ax, x_pos, 8.8, 2.25, 6.8)
    
    create_arrow(ax, 2.25, 6, 5, 5.8)
    create_arrow(ax, 5.25, 6, 5, 5.8)
    create_arrow(ax, 8.25, 6, 5, 5.8)
    
    # ==========================================
    # LAYER 5: DEPLOYMENT (Y: 1-4.5)
    # ==========================================
    ax.text(5, 4.5, '5. PRODUCTION DEPLOYMENT',
           ha='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#ECF0F1',
                    edgecolor=colors['deployment'], linewidth=2))
    
    create_box(ax, 3.5, 3.2, 3, 0.8, 'Real-Time Detector\n(1,280 tx/s)',
              colors['deployment'])
    
    create_box(ax, 1.5, 2, 2, 0.6, 'SHAP\nGlobal',
              colors['deployment'], text_color='black')
    create_box(ax, 6.5, 2, 2, 0.6, 'LIME\nLocal',
              colors['deployment'], text_color='black')
    
    create_box(ax, 3.5, 1, 3, 0.8, 'Alert System\n(5 categories)',
              colors['deployment'])
    
    # Arrows
    create_arrow(ax, 5, 5, 5, 4, 'Deploy')
    create_arrow(ax, 4.5, 3.2, 2.5, 2.6, style='dashed')
    create_arrow(ax, 5.5, 3.2, 7.5, 2.6, style='dashed')
    create_arrow(ax, 2.5, 2, 4.5, 1.8, 'Explain')
    create_arrow(ax, 7.5, 2, 5.5, 1.8)
    
    # ==========================================
    # LEGEND
    # ==========================================
    legend_elements = [
        mpatches.Patch(color=colors['data'], label='Data Collection'),
        mpatches.Patch(color=colors['feature'], label='Feature Engineering'),
        mpatches.Patch(color=colors['classical'], label='Classical ML'),
        mpatches.Patch(color=colors['deep'], label='Deep Learning'),
        mpatches.Patch(color=colors['validation'], label='Validation'),
        mpatches.Patch(color=colors['deployment'], label='Deployment')
    ]
    ax.legend(handles=legend_elements, loc='lower center',
             ncol=3, fontsize=9, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('system_architecture_matplotlib.png', dpi=300, 
                bbox_inches='tight', facecolor='white')
    plt.savefig('system_architecture_matplotlib.pdf', dpi=300,
                bbox_inches='tight', facecolor='white')
    print("✅ Matplotlib diagrams saved!")
    
    return fig

# Generate
fig = create_system_architecture_matplotlib()
plt.show()