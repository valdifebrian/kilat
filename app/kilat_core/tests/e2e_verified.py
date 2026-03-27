import os
import sys
from pathlib import Path

# Add project root and app to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
APP_ROOT = (PROJECT_ROOT / "app").resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from kilat_core.tools.read_many import read_many_files
from kilat_core.tools.edit_many import edit_many_files
from kilat_core.tools.semantic_search import semantic_search
from kilat_core.planner import Planner

def test_batch_ops():
    print("🧪 Testing Batch Ops...")
    # Test read
    current_file = __file__
    res = read_many_files([current_file])
    assert "FILE:" in res
    print("  ✅ Batch Read: PASS")
    
    # Test edit (atomic)
    test_file = PROJECT_ROOT / "tmp_test_batch.txt"
    test_file.write_text("Original", encoding="utf-8")
    
    edits = [{"path": str(test_file), "content": "Updated"}]
    res = edit_many_files(edits)
    assert "successful" in res.lower()
    assert test_file.read_text(encoding="utf-8") == "Updated"
    
    # Cleanup
    os.remove(test_file)
    print("  ✅ Batch Edit: PASS")

def test_semantic_search():
    print("🧪 Testing Semantic Search (Tree-sitter)...")
    # Test on a file with definitions
    res = semantic_search(str(PROJECT_ROOT / "app" / "kilat.py"))
    assert "🏛️" in res or "𝑓" in res
    print("  ✅ Semantic Search: PASS")

def test_planner():
    print("🧪 Testing Planner...")
    p = Planner(str(PROJECT_ROOT))
    res = p.create_plan("E2E Test", ["Step 1", "Step 2"])
    assert "PLAN.md" in res
    
    res = p.update_step(1, "x")
    assert "[x] Step 1" in p.get_summary()
    
    # Cleanup
    if os.path.exists(PROJECT_ROOT / "PLAN.md"):
        os.remove(PROJECT_ROOT / "PLAN.md")
    print("  ✅ Planner: PASS")

if __name__ == "__main__":
    print("🚀 KILAT END-TO-END VERIFICATION\n")
    try:
        test_batch_ops()
        test_semantic_search()
        test_planner()
        print("\n🏆 ALL TESTS PASSED! KILAT IS STABLE.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
