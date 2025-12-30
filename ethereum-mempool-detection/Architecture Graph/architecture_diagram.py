from graphviz import Digraph

def create_system_architecture():
    """
    Creates a comprehensive system architecture diagram for 
    Ethereum mempool attack detection - Q1 journal quality
    """
    
    # Create directed graph with professional styling
    dot = Digraph(comment='System Architecture', 
                  format='pdf',  # Change to 'svg' or 'png' if needed
                  engine='dot')
    
    # Global graph attributes for professional appearance
    dot.attr(rankdir='TB',  # Top to Bottom layout
             splines='ortho',  # Orthogonal edges
             nodesep='0.8',
             ranksep='1.2',
             bgcolor='white',
             fontname='Arial',
             fontsize='12',
             dpi= '300')
    
    # Node styling
    node_style = {
        'shape': 'box',
        'style': 'rounded,filled',
        'fontname': 'Arial',
        'fontsize': '11',
        'height': '0.6',
        'width': '2.5'
    }
    
    # ==========================================
    # LAYER 1: DATA COLLECTION
    # ==========================================
    with dot.subgraph(name='cluster_0') as c:
        c.attr(label='1. Data Collection Module',
               style='rounded',
               color='#2C3E50',
               fontsize='13',
               fontname='Arial Bold',
               labelloc='t')
        
        c.node('ganache', 'Ganache v7.4.0\nBlockchain Testnet\n(103,734 transactions)',
               fillcolor='#3498DB', fontcolor='white', **node_style)
        c.node('mempool', 'Mempool Monitor\n(15 tx/s simulation)',
               fillcolor='#5DADE2', fontcolor='white', **node_style)
        c.node('stream', 'Transaction Stream\n(5 attack categories)',
               fillcolor='#85C1E9', fontcolor='black', **node_style)
    
    # ==========================================
    # LAYER 2: FEATURE ENGINEERING
    # ==========================================
    with dot.subgraph(name='cluster_1') as c:
        c.attr(label='2. Feature Engineering Module',
               style='rounded',
               color='#16A085',
               fontsize='13',
               fontname='Arial Bold',
               labelloc='t')
        
        c.node('extract', 'Feature Extractor\n(12 features)',
               fillcolor='#1ABC9C', fontcolor='white', **node_style)
        
        # Sub-features in a nested cluster
        with c.subgraph(name='cluster_features') as s:
            s.attr(style='dashed', color='#7DCEA0')
            s.node('nonce', 'Nonce Features\n(conflict, gap)',
                   fillcolor='#A9DFBF', fontcolor='black', 
                   shape='box', style='filled', fontsize='10')
            s.node('gas', 'Gas Features\n(price, differential, volatility)',
                   fillcolor='#A9DFBF', fontcolor='black',
                   shape='box', style='filled', fontsize='10')
            s.node('timing', 'Timing Features\n(frequency, interval)',
                   fillcolor='#A9DFBF', fontcolor='black',
                   shape='box', style='filled', fontsize='10')
            s.node('txn', 'Transaction Features\n(value, data_size)',
                   fillcolor='#A9DFBF', fontcolor='black',
                   shape='box', style='filled', fontsize='10')
        
        c.node('standardize', 'Z-Score Standardization\n(μ=0, σ=1)',
               fillcolor='#48C9B0', fontcolor='white', **node_style)
    
    # ==========================================
    # LAYER 3: MODEL TRAINING (PARALLEL)
    # ==========================================
    with dot.subgraph(name='cluster_2') as c:
        c.attr(label='3. Model Training Framework (Parallel Evaluation)',
               style='rounded',
               color='#8E44AD',
               fontsize='13',
               fontname='Arial Bold',
               labelloc='t')
        
        # Classical ML Branch
        with c.subgraph(name='cluster_classical') as s:
            s.attr(label='Classical ML', style='dashed', color='#AF7AC5')
            s.node('xgb', 'XGBoost\n(269 trees, Bayesian opt)\n96.48% acc',
                   fillcolor='#9B59B6', fontcolor='white', **node_style)
            s.node('rf', 'Random Forest\n(200 trees)\n96.48% acc',
                   fillcolor='#BB8FCE', fontcolor='black', **node_style)
            s.node('svm', 'SVM (Linear+RBF)\n(GridSearchCV)\n61-82% acc',
                   fillcolor='#D7BDE2', fontcolor='black', **node_style)
        
        # Deep Learning Branch
        with c.subgraph(name='cluster_dl') as s:
            s.attr(label='Deep Learning', style='dashed', color='#AF7AC5')
            s.node('mlp', 'MLP (12K params)\n96.49% acc',
                   fillcolor='#9B59B6', fontcolor='white', **node_style)
            s.node('cnn', '1D-CNN (9K params)\n96.46% acc',
                   fillcolor='#BB8FCE', fontcolor='black', **node_style)
            s.node('lstm', 'BiLSTM (79K params)\n96.49% acc',
                   fillcolor='#D7BDE2', fontcolor='black', **node_style)
            s.node('transformer', 'Transformer (80K params)\n96.49% acc',
                   fillcolor='#E8DAEF', fontcolor='black', **node_style)
    
    # ==========================================
    # LAYER 4: MODEL SELECTION & VALIDATION
    # ==========================================
    with dot.subgraph(name='cluster_3') as c:
        c.attr(label='4. Model Selection & Statistical Validation',
               style='rounded',
               color='#E67E22',
               fontsize='13',
               fontname='Arial Bold',
               labelloc='t')
        
        c.node('cv', '5-Fold Cross-Validation\n(F1-weighted scoring)',
               fillcolor='#F39C12', fontcolor='white', **node_style)
        c.node('mcnemar', "McNemar's Test\n(p<0.001 vs SVM)",
               fillcolor='#F8B739', fontcolor='black', **node_style)
        c.node('ablation', 'Feature Ablation\n(12 experiments)',
               fillcolor='#FAD7A0', fontcolor='black', **node_style)
        c.node('select', 'XGBoost Selected\n(96.48% acc, 0.0035ms)',
               fillcolor='#D68910', fontcolor='white', 
               shape='box', style='rounded,filled,bold', 
               fontsize='12', width='3.0')
    
    # ==========================================
    # LAYER 5: DEPLOYMENT & EXPLAINABILITY
    # ==========================================
    with dot.subgraph(name='cluster_4') as c:
        c.attr(label='5. Production Deployment System',
               style='rounded',
               color='#C0392B',
               fontsize='13',
               fontname='Arial Bold',
               labelloc='t')
        
        c.node('deploy', 'Real-Time Detector\n(1,280 tx/s throughput)',
               fillcolor='#E74C3C', fontcolor='white', **node_style)
        
        with c.subgraph(name='cluster_explain') as s:
            s.attr(style='dashed', color='#EC7063')
            s.node('shap', 'SHAP Analysis\n(global importance)',
                   fillcolor='#F1948A', fontcolor='black',
                   shape='box', style='filled', fontsize='10')
            s.node('lime', 'LIME Explanations\n(instance-level)',
                   fillcolor='#F1948A', fontcolor='black',
                   shape='box', style='filled', fontsize='10')
        
        c.node('alert', 'Alert System\n(5 attack categories)',
               fillcolor='#C0392B', fontcolor='white', **node_style)
    
    # ==========================================
    # EDGES (Data Flow)
    # ==========================================
    
    # Layer 1 → 2
    dot.edge('ganache', 'mempool', label='Block generation\n12s intervals', 
             fontsize='9', fontcolor='#566573')
    dot.edge('mempool', 'stream', label='Transaction\nbroadcast',
             fontsize='9', fontcolor='#566573')
    dot.edge('stream', 'extract', label='Raw transactions',
             fontsize='9', fontcolor='#566573', style='bold')
    
    # Layer 2 internal
    dot.edge('extract', 'nonce', style='dashed', color='#7DCEA0')
    dot.edge('extract', 'gas', style='dashed', color='#7DCEA0')
    dot.edge('extract', 'timing', style='dashed', color='#7DCEA0')
    dot.edge('extract', 'txn', style='dashed', color='#7DCEA0')
    
    dot.edge('nonce', 'standardize', style='dashed', color='#7DCEA0')
    dot.edge('gas', 'standardize', style='dashed', color='#7DCEA0')
    dot.edge('timing', 'standardize', style='dashed', color='#7DCEA0')
    dot.edge('txn', 'standardize', style='dashed', color='#7DCEA0')
    
    # Layer 2 → 3 (parallel training)
    dot.edge('standardize', 'xgb', label='80/20 split\n82,987 train',
             fontsize='9', fontcolor='#566573', style='bold')
    dot.edge('standardize', 'rf', style='bold', color='#7F8C8D')
    dot.edge('standardize', 'svm', style='bold', color='#7F8C8D')
    dot.edge('standardize', 'mlp', style='bold', color='#7F8C8D')
    dot.edge('standardize', 'cnn', style='bold', color='#7F8C8D')
    dot.edge('standardize', 'lstm', style='bold', color='#7F8C8D')
    dot.edge('standardize', 'transformer', style='bold', color='#7F8C8D')
    
    # Layer 3 → 4 (validation)
    dot.edge('xgb', 'cv', style='bold', color='#8E44AD')
    dot.edge('rf', 'cv', color='#7F8C8D')
    dot.edge('svm', 'cv', color='#7F8C8D')
    dot.edge('mlp', 'cv', color='#7F8C8D')
    dot.edge('cnn', 'cv', color='#7F8C8D')
    dot.edge('lstm', 'cv', color='#7F8C8D')
    dot.edge('transformer', 'cv', color='#7F8C8D')
    
    dot.edge('cv', 'mcnemar', label='Statistical\nsignificance',
             fontsize='9', fontcolor='#566573')
    dot.edge('cv', 'ablation', fontsize='9', fontcolor='#566573')
    dot.edge('mcnemar', 'select', style='bold', color='#E67E22')
    dot.edge('ablation', 'select', style='bold', color='#E67E22')
    
    # Layer 4 → 5
    dot.edge('select', 'deploy', label='Production\ndeployment',
             fontsize='9', fontcolor='#566573', style='bold', color='#C0392B')
    
    dot.edge('deploy', 'shap', style='dashed', color='#EC7063')
    dot.edge('deploy', 'lime', style='dashed', color='#EC7063')
    
    dot.edge('shap', 'alert', label='Explainable\nclassifications',
             fontsize='9', fontcolor='#566573', color='#C0392B')
    dot.edge('lime', 'alert', color='#C0392B')
    
    # Add legend
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(label='Legend', style='dashed', color='#95A5A6',
               fontsize='11', labelloc='b')
        c.node('leg1', 'Bold edges = Primary data flow',
               shape='plaintext', fontsize='10')
        c.node('leg2', 'Dashed edges = Internal module connections',
               shape='plaintext', fontsize='10')
    
    return dot

# Generate the diagram
diagram = create_system_architecture()

# Save as PDF (high quality for journals)
diagram.render('system_architecture', format='pdf', cleanup=True)

# Also save as PNG (300 DPI for Word documents)
diagram.render('system_architecture', format='png', cleanup=True)

# Save as SVG (vector, infinitely scalable)
diagram.render('system_architecture', format='svg', cleanup=True)

print("✅ System architecture diagrams generated:")
print("   - system_architecture.pdf (for LaTeX submissions)")
print("   - system_architecture.png (for Word documents, 300 DPI)")
print("   - system_architecture.svg (vector format)")