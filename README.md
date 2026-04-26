#  OrbitWatch — Real-Time Satellite Tracker

A self-contained, single-file satellite tracker with a 3D interactive globe.
**No backend required.** Hosted as a static site on GitHub Pages / Vercel.


## Features
- 150–400 real satellites across 7 groups
- SGP4 orbital mechanics — positions update every 2 seconds
- Full orbit paths for every satellite
- Rich info card: NORAD ID, international designator, orbital elements, live position
- Drag / zoom / click globe
- Automatic weekly TLE refresh via GitHub Actions

## Project Structure
```
orbitwatch/
├── index.html                    ← The entire app (single file)
├── scripts/
│   └── build.py                  ← Fetches fresh TLEs, rebuilds index.html
└── .github/
    └── workflows/
        └── refresh-tles.yml      ← Runs build.py every Monday at 06:00 UTC
```

## How TLE Refresh Works
Every Monday the GitHub Action:
1. Runs `scripts/build.py`
2. Fetches fresh TLE data from [Celestrak](https://celestrak.org) for all 7 groups
3. Injects the new TLEs into `index.html`
4. Commits and pushes the updated file
5. Vercel/GitHub Pages auto-deploys the new version

Satellite **positions** are always live (SGP4 propagation in the browser).
The **orbital elements** are refreshed weekly so accuracy stays within ~1 km.

## Satellite Groups
| Group | Source | Count |
|---|---|---|
| Space Stations | Celestrak `stations` | ~10 |
| Weather | Celestrak `weather` | ~40 |
| Navigation (GNSS) | Celestrak `gnss` | ~60 |
| Starlink | Celestrak `starlink` | ~120 |
| OneWeb | Celestrak `oneweb` | ~80 |
| Science / EO | Celestrak `science` | ~60 |
| Debris (FY-1C cloud) | Celestrak `1999-025` | ~40 |

## Data Sources
- TLE data: [Celestrak](https://celestrak.org) (Dr. T.S. Kelso)
- Propagation: [satellite.js](https://github.com/shashwatak/satellite-js) (SGP4/SDP4)
- 3D rendering: [Three.js](https://threejs.org)
