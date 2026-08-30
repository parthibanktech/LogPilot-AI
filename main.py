"""
Root Main Entrypoint for SysOps Copilot Enterprise RAG Application
"""

import sys
import os

# Add project root to python path
sys.path.insert(0, os.path.dirname(__file__))

from production_rag.main import main

if __name__ == "__main__":
    main()
