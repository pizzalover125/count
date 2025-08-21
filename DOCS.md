# Count Documentation

### `--mode`

**Usage:** `--mode [MODE]`  
**Options:** `day`, `day-5min`, `month-day`, `month-hours`, `year-months`, `year-days`, `lifetime-years`, `lifetime-months`  
**Default:** `day`  
**Description:** Selects the time visualization mode

```bash
python script.py --mode day
python script.py --mode lifetime-years
python script.py --mode year-days
```

### `--show-percentage`

**Usage:** `--show-percentage`  
**Description:** Displays completion percentage as overlay text on the image

```bash
python script.py --mode day --show-percentage
```

### `--preview`

**Usage:** `--preview`  
**Description:** Generates the image without automatically setting it as wallpaper

```bash
python script.py --mode day --preview
```

### `--no-cleanup`

**Usage:** `--no-cleanup`  
**Description:** Skips automatic cleanup of old wallpaper files

```bash
python script.py --mode day --no-cleanup
```

## Color Customization Flags

### `--bg-color` / `--background-color`

**Usage:** `--bg-color [COLOR]`  
**Default:** Black  
**Description:** Sets the background color

```bash
python script.py --bg-color "#1a1a1a"
python script.py --background-color red
python script.py --bg-color "rgb(25,25,25)"
```

### `--filled-color`

**Usage:** `--filled-color [COLOR]`  
**Default:** White  
**Description:** Sets the color for filled (completed) circles

```bash
python script.py --filled-color green
python script.py --filled-color "#00ff00"
python script.py --filled-color "0,255,0"
```

### `--hollow-color`

**Usage:** `--hollow-color [COLOR]`  
**Default:** White  
**Description:** Sets the color for hollow (remaining) circle outlines

```bash
python script.py --hollow-color orange
python script.py --hollow-color "#ff6600"
```

### `--percentage-color`

**Usage:** `--percentage-color [COLOR]`  
**Default:** White  
**Description:** Sets the color for percentage text (when `--show-percentage` is used)

```bash
python script.py --show-percentage --percentage-color yellow
python script.py --show-percentage --percentage-color "#ffff00"
```

## Lifetime Tracking Flags

### `--dob` / `--date-of-birth`

**Usage:** `--dob YYYY-MM-DD`  
**Default:** `2010-12-22`  
**Description:** Sets your date of birth for lifetime visualizations

```bash
python script.py --mode lifetime-years --dob 1990-05-15
python script.py --mode lifetime-months --date-of-birth 1985-12-03
```

### `--life-expectancy`

**Usage:** `--life-expectancy [YEARS]`  
**Default:** `90`  
**Description:** Sets life expectancy in years for lifetime visualizations

```bash
python script.py --mode lifetime-years --life-expectancy 85
python script.py --mode lifetime-months --life-expectancy 95
```

## Color Format Examples

All color flags accept these formats:

**Named colors:**

```bash
--bg-color black
--filled-color white
--hollow-color red
```

**Hex colors:**

```bash
--bg-color "#1a1a1a"
--filled-color "#00ff00"
--hollow-color "#f00"
```

**RGB values:**

```bash
--bg-color "rgb(26,26,26)"
--filled-color "0,255,0"
--hollow-color "255,0,0"
```

## Complete Examples

**Daily progress with custom colors:**

```bash
python script.py --mode day --show-percentage --bg-color "#1a1a1a" --filled-color green --percentage-color yellow
```

**Lifetime progress:**

```bash
python script.py --mode lifetime-years --dob 1990-05-15 --life-expectancy 85 --show-percentage --filled-color blue
```

**Preview mode with custom styling:**

```bash
python script.py --mode month-day --preview --bg-color black --filled-color cyan --hollow-color white --show-percentage
```
