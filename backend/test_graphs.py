import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.subagents.executor import build_graph as build_ex
from app.agents.subagents.writer import build_graph as build_wr
from app.agents.subagents.analyst import build_graph as build_an
from app.agents.subagents.researcher import build_graph as build_res
from app.agents.superviser import build_graph as build_sup
import traceback

try:
    print("Building Executor...")
    ex = build_ex()
    print("✓ Executor built successfully!")
    
    print("Building Writer...")
    wr = build_wr()
    print("✓ Writer built successfully!")
    
    print("Building Analyst...")
    an = build_an()
    print("✓ Analyst built successfully!")
    
    print("Building Researcher...")
    res = build_res()
    print("✓ Researcher built successfully!")
    
    print("Building Supervisor...")
    sup = build_sup()
    print("✓ Supervisor built successfully!")
    
    print("\n✅ All graphs built successfully!")
except Exception as e:
    print("❌ Error:", str(e))
    traceback.print_exc()

