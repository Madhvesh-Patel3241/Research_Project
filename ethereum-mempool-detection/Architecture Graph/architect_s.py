from graphviz import Digraph
import os

# Create the Directed Graph
dot = Digraph('Ethereum_Mempool_Architecture', comment='Q1 Journal Architecture')

# --- 1. Global Settings for Journal Quality ---
dot.attr(rankdir='LR')           # Left-to-Right layout
dot.attr(dpi='300')              # High resolution
dot.attr(fontname='Times-Roman') # Standard Academic Font
dot.attr(splines='ortho')        # Straight, professional lines
dot.attr(nodesep='0.6')
dot.attr(ranksep='0.8')

# --- 2. Define Nodes ---
# Main Pipeline (Light Blue)
dot.attr('node', shape='box', style='filled', fillcolor='#E3F2FD', 
         color='black', penwidth='1.2', fontsize='11', fontname='Helvetica-Bold')

dot.node('ETH', 'Ethereum Node')
dot.node('MON', 'Mempool Monitor')
dot.node('FE', 'Feature Extractor')
dot.node('XGB', 'XGBoost Detector')
dot.node('ALT', 'Alert System')

# Data Outputs (Light Yellow, Note shape)
dot.attr('node', shape='note', style='filled', fillcolor='#FFF9C4', 
         fontsize='9', fontname='Courier')
dot.node('STREAM', 'Transaction Stream\n(15 tx/s nominal)')
dot.node('RESULT', 'Detection Results\n(Attack Classifications)')

# --- 3. Define Edges ---
dot.edge('ETH', 'MON')
dot.edge('MON', 'FE')
dot.edge('FE', 'XGB')
dot.edge('XGB', 'ALT')

# Data Output Edges (Dashed)
dot.edge('ETH', 'STREAM', style='dashed', arrowhead='vee', color='grey30')
dot.edge('ALT', 'RESULT', style='dashed', arrowhead='vee', color='grey30')

# --- 4. Render in ALL Formats ---
output_name = 'system_architecture_s'

# 1. Save as PDF (Best for LaTeX)
dot.render(output_name, view=False, format='pdf')
print(f"Saved: {output_name}.pdf (Best for LaTeX)")

# 2. Save as SVG (Best for Word/Web)
dot.render(output_name, view=False, format='svg')
print(f"Saved: {output_name}.svg (Best for Word)")

# 3. Save as PNG (Back up for general use)
dot.render(output_name, view=True, format='png')
print(f"Saved: {output_name}.png (Visual Check)")