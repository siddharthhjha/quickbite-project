"""
Fix all page imports at once
Run: python fix_pages.py
"""

import os
import re

pages_dir = 'pages'

# Import statements to add
imports_to_add = {
    '05_Customer_Segments.py': 'from utils.sample_data import create_sample_*',
    '07_Experiments.py': 'from utils.sample_data import create_sample_experiments',
    '08_Churn_Predictor.py': 'from utils.sample_data import create_sample_churn_data',
    '10_LTV_Dashboard.py': 'from utils.sample_data import create_sample_ltv_data',
    '11_Anomaly_Detector.py': 'from utils.sample_data import create_sample_daily_metrics',
}

for filename, import_line in imports_to_add.items():
    filepath = os.path.join(pages_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if import already exists
        if import_line not in content:
            # Find where to add import (after other imports)
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
            lines.insert(insert_pos, import_line)
            content = '\n'.join(lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Added import to {filename}")
        else:
            print(f"⏭️ Import already exists in {filename}")

print("✅ All pages fixed!")