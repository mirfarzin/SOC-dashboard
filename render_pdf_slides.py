"""
Renders each slide of PS02_Offline_Security_Incident_Triage_Assistant_FINAL.pdf
to PNG for visual quality, layout, alignment, and legibility review.
"""

from pathlib import Path
import fitz  # PyMuPDF

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "PS02_Offline_Security_Incident_Triage_Assistant_FINAL.pdf"
PREVIEW_DIR = BASE_DIR / "outputs" / "presentation_preview"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

doc = fitz.open(PDF_PATH)
print(f"Total pages in presentation: {len(doc)}")

for page_idx in range(len(doc)):
    page = doc[page_idx]
    pix = page.get_pixmap(dpi=150)
    out_file = PREVIEW_DIR / f"slide_{page_idx}.png"
    pix.save(str(out_file))
    print(f"  ✓ Rendered slide {page_idx} -> {out_file.name} ({out_file.stat().st_size // 1024} KB)")

print("All preview slides rendered successfully!")
