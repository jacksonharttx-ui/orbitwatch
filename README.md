#  OrbitWatch — Real-Time Satellite Tracker (broken)

A self-contained, single-file satellite tracker with a 3D interactive globe.


## Features
- 150–400 real satellites across 7 groups
- SGP4 orbital mechanics — positions update every 2 seconds
- Full orbit paths for every satellite
- Rich info card: NORAD ID, international designator, orbital elements, live position
- Drag / zoom / click globe
- Automatic weekly TLE refresh via GitHub Actions
  
## Data Sources
- TLE data: [Celestrak](https://celestrak.org) (Dr. T.S. Kelso)
- Propagation: [satellite.js](https://github.com/shashwatak/satellite-js) (SGP4/SDP4)
- 3D rendering: [Three.js](https://threejs.org)
