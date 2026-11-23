"""
Generates high-resolution monochrome graphics for PS02 TARS-style presentation:
1. cover_security_node.png - Abstract isometric telemetry converging into an incident node.
2. problem_iceberg.png - Conceptual visible logs vs. hidden correlated attack killchain.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ASSETS_DIR = Path(__file__).resolve().parent / "outputs" / "presentation_assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def create_cover_graphic():
    """Generates striking isometric monochrome security telemetry node."""
    w, h = 1200, 1500
    img = Image.new("RGBA", (w, h), (10, 10, 10, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, h // 2

    # Draw subtle background grid
    grid_color = (25, 25, 25, 255)
    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=grid_color, width=1)
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)

    # Concentric isometric hexagons (air-gap boundary)
    for radius, stroke, col in [
        (480, 2, (40, 40, 40, 255)),
        (380, 3, (70, 70, 70, 255)),
        (280, 4, (120, 120, 120, 255)),
        (180, 6, (200, 200, 200, 255)),
    ]:
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            px = cx + radius * math.cos(angle)
            py = cy + (radius * 0.7) * math.sin(angle)
            points.append((px, py))
        draw.polygon(points, outline=col, width=stroke)

    # Converging telemetry rays
    stream_color = (180, 180, 180, 255)
    origins = [
        (150, 250), (1050, 250),
        (80, 750), (1120, 750),
        (200, 1300), (1000, 1300),
        (cx, 120), (cx, 1380)
    ]
    for ox, oy in origins:
        # Draw node circle
        draw.ellipse([ox - 10, oy - 10, ox + 10, oy + 10], fill=(240, 240, 240, 255), outline=(10, 10, 10, 255), width=3)
        # Draw connecting segmented line
        draw.line([(ox, oy), (cx, cy)], fill=(90, 90, 90, 255), width=2)

    # Inner 3D isometric core structure (Cube / Shield node)
    cube_size = 140
    # Top face
    top_face = [
        (cx, cy - cube_size),
        (cx + cube_size * 1.1, cy - cube_size * 0.4),
        (cx, cy + cube_size * 0.2),
        (cx - cube_size * 1.1, cy - cube_size * 0.4)
    ]
    draw.polygon(top_face, fill=(245, 245, 245, 255), outline=(10, 10, 10, 255), width=4)

    # Left face
    left_face = [
        (cx - cube_size * 1.1, cy - cube_size * 0.4),
        (cx, cy + cube_size * 0.2),
        (cx, cy + cube_size * 1.5),
        (cx - cube_size * 1.1, cy + cube_size * 0.9)
    ]
    draw.polygon(left_face, fill=(160, 160, 160, 255), outline=(10, 10, 10, 255), width=4)

    # Right face
    right_face = [
        (cx, cy + cube_size * 0.2),
        (cx + cube_size * 1.1, cy - cube_size * 0.4),
        (cx + cube_size * 1.1, cy + cube_size * 0.9),
        (cx, cy + cube_size * 1.5)
    ]
    draw.polygon(right_face, fill=(80, 80, 80, 255), outline=(10, 10, 10, 255), width=4)

    # Glowing inner node
    draw.ellipse([cx - 24, cy - 10, cx + 24, cy + 38], fill=(255, 255, 255, 255))

    out_path = ASSETS_DIR / "cover_security_node.png"
    img.save(out_path, "PNG")
    print(f"[+] Saved cover graphic: {out_path}")


def create_problem_iceberg():
    """Generates conceptual iceberg diagram matching TARS page 2."""
    w, h = 1200, 1000
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    cx = w // 2
    waterline = 460

    # Top light background, bottom darker underwater tint
    draw.rectangle([0, waterline, w, h], fill=(245, 245, 248, 255))

    # Waterline divider
    draw.line([(60, waterline), (w - 60, waterline)], fill=(30, 30, 30, 255), width=3)
    draw.text((w - 240, waterline - 28), "WATERLINE • VISIBLE LOGS", fill=(80, 80, 80, 255))
    draw.text((w - 300, waterline + 12), "UNDERWATER • CORRELATED THREAT", fill=(120, 120, 120, 255))

    # Upper iceberg (visible tip)
    upper_tip = [
        (cx, 160),
        (cx + 180, waterline),
        (cx - 180, waterline)
    ]
    draw.polygon(upper_tip, fill=(230, 230, 235, 255), outline=(20, 20, 20, 255), width=3)

    # Lower iceberg (submerged mass - massive)
    lower_mass = [
        (cx - 180, waterline),
        (cx + 180, waterline),
        (cx + 340, 680),
        (cx + 180, 900),
        (cx, 960),
        (cx - 180, 900),
        (cx - 340, 680),
    ]
    draw.polygon(lower_mass, fill=(35, 35, 38, 255), outline=(10, 10, 10, 255), width=3)

    # Internal facet lines on lower mass for 3D geometric effect
    facets = [
        ((cx, 960), (cx, waterline)),
        ((cx - 180, 900), (cx - 80, waterline)),
        ((cx + 180, 900), (cx + 80, waterline)),
        ((cx - 340, 680), (cx, 620)),
        ((cx + 340, 680), (cx, 620)),
        ((cx, 620), (cx, 960))
    ]
    for p1, p2 in facets:
        draw.line([p1, p2], fill=(65, 65, 70, 255), width=2)

    # Annotations on upper part
    draw.text((cx - 75, 280), "RAW LOGS", fill=(20, 20, 20, 255))
    draw.text((cx - 95, 310), "AUTH FAILURES", fill=(60, 60, 60, 255))
    draw.text((cx - 85, 340), "DISPARATE ALERTS", fill=(60, 60, 60, 255))

    # Annotations on submerged mass
    draw.text((cx - 120, 520), "• LATERAL MOVEMENT", fill=(240, 240, 240, 255))
    draw.text((cx - 140, 580), "• DEFENSIVE EVASION (EDR)", fill=(240, 240, 240, 255))
    draw.text((cx - 150, 640), "• UNAPPROVED PRIVILEGE GAIN", fill=(240, 240, 240, 255))
    draw.text((cx - 165, 700), "• MULTI-STAGE ATTACK SYNERGY", fill=(240, 240, 240, 255))
    draw.text((cx - 130, 760), "• ATTACK TIMELINE CONTEXT", fill=(240, 240, 240, 255))

    out_path = ASSETS_DIR / "problem_iceberg.png"
    img.save(out_path, "PNG")
    print(f"[+] Saved problem iceberg graphic: {out_path}")


if __name__ == "__main__":
    create_cover_graphic()
    create_problem_iceberg()
