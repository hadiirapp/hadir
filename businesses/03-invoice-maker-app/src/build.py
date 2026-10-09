"""Build the free web edition (site/index.html) and the paid Pro file (product/Fatoora-Pro.html).

Usage: python3 src/build.py [checkout_url]
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = (root / "src/app.html").read_text()
buy = sys.argv[1] if len(sys.argv) > 1 else "YOUR_CHECKOUT_LINK"
(root / "site/index.html").write_text(src.replace("__PRO__", "false").replace("__BUY_URL__", buy))
(root / "product/Fatoora-Pro.html").write_text(src.replace("__PRO__", "true").replace("__BUY_URL__", buy))
print("built")
