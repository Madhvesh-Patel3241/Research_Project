from graphviz import Digraph

def generate_architecture():
    dot = Digraph('Blockchain_Security_Arch', comment='Q1 Journal Architecture')
    dot.attr(rankdir='TB', size='10,10', dpi='300', compound='true', fontname='Times-Roman')
    
    # Defaults for nodes
    dot.attr('node', shape='box', style='filled', fillcolor='white', fontname='Helvetica', fontsize='10')
    dot.attr('edge', fontname='Helvetica', fontsize='8')

    # Cluster 1: Offline Training
    with dot.subgraph(name='cluster_0') as c:
        c.attr(style='dashed', label='Phase I: Offline Model Development', color='grey40')
        c.node('DS', 'Historical Dataset\n(Ganache)', shape='cylinder', fillcolor='#f3e5f5')
        c.node('FE_OFF', 'Feature Engineering\n(12-Feature Set)')
        c.node('TR', 'XGBoost Training\n(Bayesian Optimization)')
        c.node('ART', 'Serialized Model\nArtifact', shape='note', fillcolor='#fff9c4')
        
        c.edge('DS', 'FE_OFF')
        c.edge('FE_OFF', 'TR')
        c.edge('TR', 'ART')

    # Cluster 2: Real-Time Deployment
    with dot.subgraph(name='cluster_1') as c:
        c.attr(style='bold', label='Phase II: Real-Time Detection Pipeline (Mainnet)', color='black')
        
        # Input Layer
        c.node('ETH', 'Ethereum Mempool', shape='cylinder', fillcolor='#e1f5fe')
        c.node('MON', 'Mempool Monitor\n(Async Listener)')
        
        # Processing Layer
        c.node('RT_FE', 'Real-Time\nFeature Extractor')
        c.node('DB', 'Rolling Stats\n(60s Window)', shape='cylinder', fillcolor='#e0f2f1')
        
        # Inference Layer
        c.node('XGB', 'XGBoost Inference\n(Latency: 0.0035ms)', fillcolor='#c8e6c9', style='filled,bold')
        c.node('SHAP', 'SHAP Explainer\n(Interpretation)')
        
        # Output Layer
        c.node('DEC', 'Decision Logic\n(Threshold τ)', shape='diamond')
        c.node('ALT', 'Critical Alert\n(Block Tx)', style='filled', fillcolor='#ffcdd2')
        c.node('LOG', 'Audit Log', shape='folder')

        # Edges in Deployment
        c.edge('ETH', 'MON', label=' JSON-RPC')
        c.edge('MON', 'RT_FE')
        c.edge('DB', 'RT_FE', style='dashed')
        c.edge('RT_FE', 'XGB', label=' Feature Vector x')
        c.edge('XGB', 'SHAP')
        c.edge('XGB', 'DEC', label=' Score ŷ')
        c.edge('DEC', 'ALT', label=' Attack')
        c.edge('DEC', 'LOG', label=' Normal')
        c.edge('SHAP', 'LOG', style='dotted')

    # Link Training to Deployment
    dot.edge('ART', 'XGB', label=' Load Weights', style='dashed', constraint='false')

    dot.render('architecture_diagram', view=True, format='png')
    print("Architecture diagram generated as 'architecture_diagram.png'")

if __name__ == '__main__':
    generate_architecture()