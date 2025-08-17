from __future__ import annotations
import math
import os
import platform
from random import randint
import subprocess
import argparse
import glob
from datetime import date, datetime
from typing import Tuple
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    raise SystemExit("This script requires Pillow. Install with: pip install pillow")

DEFAULT_BACKGROUND = (0, 0, 0)
DEFAULT_FILLED_COLOR = (255, 255, 255)
DEFAULT_HOLLOW_COLOR = (255, 255, 255)
DEFAULT_PERCENTAGE_COLOR = (255, 255, 255) 
HOLLOW_WIDTH = 3   
MARGIN_RATIO = 0.06
MAX_COLUMNS = 64 

OUTPUT_PATH = os.path.expanduser(os.getenv("TIME_VIS_OUT", f"~/count_{randint(1000,10000)}.png"))
CANVAS_SIZE: Tuple[int, int] | None = None
DEFAULT_DOB_STR = os.getenv("TIME_VIS_DOB", "2010-12-22")
DEFAULT_LIFE_EXPECTANCY_YEARS = int(os.getenv("TIME_VIS_EXPECTANCY", "90"))

BACKGROUND = DEFAULT_BACKGROUND
FILLED_COLOR = DEFAULT_FILLED_COLOR
HOLLOW_COLOR = DEFAULT_HOLLOW_COLOR
PERCENTAGE_COLOR = DEFAULT_PERCENTAGE_COLOR
DOB_STR = DEFAULT_DOB_STR
LIFE_EXPECTANCY_YEARS = DEFAULT_LIFE_EXPECTANCY_YEARS

def parse_color(color_str: str) -> Tuple[int, int, int]:
    color_str = color_str.strip().lower()
    
    named_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (165, 42, 42),
        'navy': (0, 0, 128),
        'olive': (128, 128, 0),
        'lime': (0, 255, 0),
        'aqua': (0, 255, 255),
        'teal': (0, 128, 128),
        'silver': (192, 192, 192),
        'maroon': (128, 0, 0),
        'fuchsia': (255, 0, 255),
    }
    
    if color_str in named_colors:
        return named_colors[color_str]
    
    if color_str.startswith('#'):
        hex_color = color_str[1:]
        if len(hex_color) == 3: 
            hex_color = ''.join([c*2 for c in hex_color]) 
        if len(hex_color) == 6:  
            try:
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except ValueError:
                pass
    
    if color_str.startswith('rgb(') and color_str.endswith(')'):
        color_str = color_str[4:-1]
    
    try:
        parts = [int(x.strip()) for x in color_str.split(',')]
        if len(parts) == 3 and all(0 <= x <= 255 for x in parts):
            return tuple(parts)
    except ValueError:
        pass
    
    raise ValueError(f"Invalid color format: '{color_str}'. Use hex (#RRGGBB or #RGB), rgb(r,g,b), r,g,b, or named colors.")

def cleanup_old_wallpapers() -> None:
    home_dir = os.path.expanduser("~")
    
    pattern = "count_*.png"
    
    deleted_count = 0
    full_pattern = os.path.join(home_dir, pattern)
    for file_path in glob.glob(full_pattern):
        try:
            os.remove(file_path)
            deleted_count += 1
            print(f"Deleted old wallpaper: {file_path}")
        except Exception as e:
            print(f"Warning: Could not delete {file_path}: {e}")
    
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old wallpaper(s)")
    else:
        print("No old wallpapers found to clean up")

def detect_screen_size() -> Tuple[int, int]:
    try:
        sysname = platform.system()
        if sysname == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        elif sysname == "Darwin": 
            try:
                from AppKit import NSScreen  # type: ignore
                frame = NSScreen.mainScreen().frame()
                return int(frame.size.width), int(frame.size.height)
            except Exception:
                out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"]).decode()
                for line in out.splitlines():
                    if "Resolution" in line and "Retina" not in line:
                        parts = [p for p in line.split() if p.isdigit()]
                        if len(parts) >= 2:
                            return int(parts[0]), int(parts[1])
        elif sysname == "Linux":
            try:
                out = subprocess.check_output(["xrandr"]).decode()
                for line in out.splitlines():
                    if "*" in line:
                        res = line.split()[0]
                        w, h = map(int, res.split("x"))
                        return w, h
            except Exception:
                pass
    except Exception:
        pass
    return (1920, 1080)

def auto_grid(n: int, max_cols: int = MAX_COLUMNS) -> Tuple[int, int]:
    if n <= 0:
        return (1, 1)
    cols = min(max_cols, math.ceil(math.sqrt(n)))
    rows = math.ceil(n / cols)
    best = (cols, rows)
    best_ratio = abs((cols / rows) - 1)
    for c in range(1, min(max_cols, n) + 1):
        r = math.ceil(n / c)
        ratio = abs((c / r) - 1)
        if ratio < best_ratio:
            best, best_ratio = (c, r), ratio
    return best

def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/System/Library/Fonts/Helvetica.ttc", 
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def draw_circles_only(count: int, filled: int, size: Tuple[int, int], show_percentage: bool = False) -> Image.Image:
    w, h = size
    scale = 16
    W, H = w * scale, h * scale

    img = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(img)
    cols, rows = auto_grid(count)
    margin = int(min(W, H) * MARGIN_RATIO) 
    grid_w = W - 2 * margin
    grid_h = H - 2 * margin
    cell_w = grid_w / cols
    cell_h = grid_h / rows
    diameter = int(min(cell_w, cell_h) * 0.8)
    radius = diameter // 2
    x0 = (W - cols * cell_w) / 2
    y0 = (H - rows * cell_h) / 2

    for i in range(count):
        r_idx = i // cols
        c_idx = i % cols
        cx = int(x0 + c_idx * cell_w + cell_w / 2)
        cy = int(y0 + r_idx * cell_h + cell_h / 2)
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        if i < filled:
            draw.ellipse(bbox, fill=FILLED_COLOR)
        else:
            draw.ellipse(bbox, outline=HOLLOW_COLOR, width=HOLLOW_WIDTH * scale)

    if show_percentage and count > 0:
        percentage = (filled / count) * 100
        percentage_text = f"{percentage:.1f}%"

        center_x = W // 2
        center_y = H // 2
        
        base_font_size = min(W, H) // 20
        font = get_font(base_font_size)
        
        bbox = draw.textbbox((0, 0), percentage_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2
        
        padding = int(base_font_size * 0.3)
        bg_bbox = [
            text_x - padding,
            text_y - padding,
            text_x + text_width + padding,
            text_y + text_height + padding
        ]
        
        bg_color = tuple(int(c * 0.8) if c > 128 else int(c + 50) for c in BACKGROUND)
        draw.rounded_rectangle(bg_bbox, radius=padding, fill=bg_color)
        
        draw.text((text_x, text_y), percentage_text, fill=PERCENTAGE_COLOR, font=font)

    img = img.resize((w, h), Image.LANCZOS)
    return img


def view_day() -> Tuple[int, int]:
    now = datetime.now()
    count = 24
    filled = now.hour
    return count, filled

def view_month_day() -> Tuple[int, int]:
    today = date.today()
    first_next_month = date(today.year + (today.month // 12), ((today.month % 12) + 1), 1)
    days_in_month = (first_next_month - date(today.year, today.month, 1)).days
    filled = today.day - 1 
    return days_in_month, filled

def view_month_hours() -> Tuple[int, int]:
    today = date.today()
    now = datetime.now()
    
    first_next_month = date(today.year + (today.month // 12), ((today.month % 12) + 1), 1)
    days_in_month = (first_next_month - date(today.year, today.month, 1)).days
    total_hours = days_in_month * 24
    
    days_completed = today.day - 1  
    hours_completed = days_completed * 24 + now.hour
    
    return total_hours, hours_completed

def view_year_months() -> Tuple[int, int]:
    now = date.today()
    filled = now.month - 1
    return 12, filled

def view_year_days() -> Tuple[int, int]:
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    day_of_year = (today - start_of_year).days
    start_next_year = date(today.year + 1, 1, 1)
    days_in_year = (start_next_year - start_of_year).days
    return days_in_year, day_of_year

def parse_dob(dob_str: str) -> date:
    try:
        y, m, d = map(int, dob_str.split("-"))
        return date(y, m, d)
    except Exception as e:
        raise ValueError("DOB must be YYYY-MM-DD format, e.g., '2008-01-01'")

def view_lifetime_years() -> Tuple[int, int]:
    today = date.today()
    dob = parse_dob(DOB_STR)
    total = LIFE_EXPECTANCY_YEARS
    lived = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    lived = max(0, min(lived, total))
    return total, lived

def view_lifetime_months() -> Tuple[int, int]:
    today = date.today()
    dob = parse_dob(DOB_STR)
    total = LIFE_EXPECTANCY_YEARS * 12
    lived = (today.year - dob.year) * 12 + (today.month - dob.month)
    if today.day < dob.day:
        lived -= 1
    lived = max(0, min(lived, total))
    return total, lived

VIEW_MAP = {
    "day": view_day,
    "month-day": view_month_day,
    "month-hours": view_month_hours,
    "year-months": view_year_months,
    "year-days": view_year_days,
    "lifetime-years": view_lifetime_years,
    "lifetime-months": view_lifetime_months,
}

def set_wallpaper(path: str) -> None:
    sysname = platform.system()
    if sysname == "Windows":
        _set_wallpaper_windows(path)
    elif sysname == "Darwin":
        _set_wallpaper_macos(path)
    elif sysname == "Linux":
        try:
            _set_wallpaper_gnome(path)
        except Exception:
            print("Wallpaper set not supported automatically for this Linux DE. Set manually.")
    else:
        print("Unsupported OS for auto-set. Save path:", path)

def _set_wallpaper_windows(path: str) -> None:
    import ctypes
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDWININICHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE)

def _set_wallpaper_macos(path: str) -> None:
    script = f'''osascript -e 'tell application "System Events" to tell every desktop to set picture to "{path}"' '''
    subprocess.call(script, shell=True)

def _set_wallpaper_gnome(path: str) -> None:
    uri = f"file://{path}"
    subprocess.check_call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri])
    try:
        subprocess.check_call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri])
    except Exception:
        pass

def main() -> None:
    global BACKGROUND, FILLED_COLOR, HOLLOW_COLOR, PERCENTAGE_COLOR, DOB_STR, LIFE_EXPECTANCY_YEARS
    
    parser = argparse.ArgumentParser(
        description="Customizable circles-only time visualizer with percentage display",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Color formats:
  - Named colors: black, white, red, green, blue, yellow, cyan, magenta, etc.
  - Hex colors: #RRGGBB or #RGB (e.g., #FF0000, #F00)
  - RGB values: rgb(r,g,b) or r,g,b (e.g., rgb(255,0,0) or 255,0,0)

Mode descriptions:
  - day: Shows 24 circles representing hours in the current day
  - month-day: Shows circles for each day in the current month (days completed)
  - month-hours: Shows circles for each hour in the current month (hours completed)
  - year-months: Shows 12 circles representing months in the current year
  - year-days: Shows circles for each day in the current year
  - lifetime-years: Shows circles representing years in your expected lifetime
  - lifetime-months: Shows circles representing months in your expected lifetime

Examples:
  python script.py --mode day --show-percentage
  python script.py --mode month-hours --show-percentage
  python script.py --mode lifetime-years --dob 1990-05-15 --show-percentage --percentage-color yellow
  python script.py --bg-color "#1a1a1a" --filled-color "#00ff00" --hollow-color "#ff6600" --show-percentage 
        """)
    
    parser.add_argument("--mode", type=str, choices=list(VIEW_MAP.keys()), 
                       default=os.getenv("TIME_VIS_MODE", "day"), 
                       help="Select the visualization mode")
    parser.add_argument("--no-cleanup", action="store_true", 
                       help="Skip cleaning up old wallpapers") 
    
    parser.add_argument("--bg-color", "--background-color", type=str,
                       help="Background color (default: black)")
    parser.add_argument("--filled-color", type=str,
                       help="Color for filled circles (default: white)")
    parser.add_argument("--hollow-color", type=str,
                       help="Color for hollow circle outlines (default: white)")
    parser.add_argument("--percentage-color", type=str,
                       help="Color for percentage text (default: white)")
    
    parser.add_argument("--show-percentage", action="store_true",
                       help="Display percentage complete")

    parser.add_argument("--dob", "--date-of-birth", type=str,
                       help="Date of birth in YYYY-MM-DD format")
    parser.add_argument("--life-expectancy", type=int,
                       help="Life expectancy in years")
    
    parser.add_argument("--preview", action="store_true",
                       help="Generate image without setting as wallpaper")
    
    args = parser.parse_args()
    mode = args.mode.lower()

    if mode not in VIEW_MAP:
        raise SystemExit(f"Unknown mode '{mode}'. Choose one of: {', '.join(VIEW_MAP)}")

    if args.bg_color:
        try:
            BACKGROUND = parse_color(args.bg_color)
        except ValueError as e:
            raise SystemExit(f"Invalid background color: {e}")
    
    if args.filled_color:
        try:
            FILLED_COLOR = parse_color(args.filled_color)
        except ValueError as e:
            raise SystemExit(f"Invalid filled color: {e}")
    
    if args.hollow_color:
        try:
            HOLLOW_COLOR = parse_color(args.hollow_color)
        except ValueError as e:
            raise SystemExit(f"Invalid hollow color: {e}")
    
    if args.percentage_color:
        try:
            PERCENTAGE_COLOR = parse_color(args.percentage_color)
        except ValueError as e:
            raise SystemExit(f"Invalid percentage color: {e}")
    
    if args.dob:
        DOB_STR = args.dob
    
    if args.life_expectancy:
        LIFE_EXPECTANCY_YEARS = args.life_expectancy

    if mode.startswith("lifetime"):
        try:
            parse_dob(DOB_STR)
        except ValueError as e:
            raise SystemExit(f"Invalid date of birth: {e}")
        
    if not args.no_cleanup:
        cleanup_old_wallpapers()

    if CANVAS_SIZE is None:
        size = detect_screen_size()
    else:
        size = CANVAS_SIZE 

    count, filled = VIEW_MAP[mode]()
    img = draw_circles_only(count, filled, size, show_percentage=args.show_percentage)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    img.save(OUTPUT_PATH, format="PNG")
    print(f"Saved: {OUTPUT_PATH} ({count} circles; {filled} filled)")
    print(f"Colors: Background={BACKGROUND}, Filled={FILLED_COLOR}, Hollow={HOLLOW_COLOR}")
    
    if args.show_percentage:
        percentage = (filled / count) * 100 if count > 0 else 0
        print(f"Percentage displayed: {percentage:.1f}% (Color: {PERCENTAGE_COLOR})")
    
    if mode.startswith("lifetime"):
        print(f"Date of birth: {DOB_STR}, Life expectancy: {LIFE_EXPECTANCY_YEARS} years")

    if not args.preview:
        try:
            set_wallpaper(OUTPUT_PATH)
            print("Wallpaper set.")
        except Exception as e:
            print("Could not set wallpaper automatically:", e)
            print("You can set it manually using the saved image.")
    else:
        print("Preview mode: wallpaper not set automatically.") 

if __name__ == "__main__":
    main() 
