# decision-modeling-optimization
This repository contains self-directed projects from NYU Stern’s Decision Models &amp; Analytics course, completed as part of my MBA. These projects apply optimization and simulation techniques to real-world business problems using Python.


#optimization

## Optimization Case 1— Production Mix (Case: Two-P)

**Objective:** Maximize weekly profit by choosing production quantities for two products that share capacity across three plants.

**Model type:** Linear Programming (LP) / Mixed-Integer Programming (MIP)

**Decision variables**
- `D` = units of Product D (doors) per week
- `W` = units of Product W (windows) per week

**Parameters**
- Profits: `profit_D = 300`, `profit_W = 500`
- Capacity (hours): `cap_p1 = 40`, `cap_p2 = 120`, `cap_p3 = 180`
- Processing times (hours/unit):
  - Plant 1: `1*D`
  - Plant 2: `2*W`
  - Plant 3: `3*D + 2*W`

**Constraints**
- Plant 1: `1*D ≤ 40`
- Plant 2: `2*W ≤ 120`
- Plant 3: `3*D + 2*W ≤ 180`
- `D, W ≥ 0` (optionally `Integer`)

**Objective**
- Maximize `300*D + 500*W`

**How to run**
```bash
pip install pulp
python production_mix_pulp.py
