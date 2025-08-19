# decision-modeling-optimization
This repository contains self-directed projects from NYU Stern’s Decision Models &amp; Analytics course, completed as part of my MBA. These projects apply optimization and simulation techniques to real-world business problems using Python.


#optimization

Case 1 — Production Mix

Objective
Maximize weekly profit by choosing production quantities for two products that share capacity across three plants.

Model type
Linear Programming (LP) / Mixed-Integer Programming (MIP)

Decision variables

D = units of Product D (doors) per week

W = units of Product W (windows) per week

Parameters

Profits: profit_D = 300, profit_W = 500

Capacity (hours): cap_p1 = 40, cap_p2 = 120, cap_p3 = 180

Processing times (hours/unit):

Plant 1: 1*D

Plant 2: 2*W

Plant 3: 3*D + 2*W

Constraints

Plant 1: 1*D ≤ 40

Plant 2: 2*W ≤ 120

Plant 3: 3*D + 2*W ≤ 180

D, W ≥ 0 (optionally integer)

Objective function

Maximize: 300*D + 500*W


How to run

pip install pulp
python production_mix_pulp.py

Case 2 — Multi-Period Capital Allocation (Co-Investment Shares)

Objective
Choose fractional participation in three projects to maximize net present value (NPV), subject to annual capital budgets.

Model type
Linear Programming (LP)

Decision variables

x_O, x_H, x_S ∈ [0,1]: fraction invested in Office, Hotel, Shopping

Parameters (in $M)

Per-period budgets: B = [25, 20, 20, 15]

Investment needs per 100% stake:

Year   Office   Hotel   Shopping
0        40      80        90
1        60      80        50
2        90      80        20
3        10      70        60


NPV per 100% stake:

Office = 45
Hotel  = 70
Shopping = 50


Constraints

For each year t:

Investment(t, Office)*x_O + Investment(t, Hotel)*x_H + Investment(t, Shopping)*x_S <= Budget(t)


Bounds:

0 <= x_O, x_H, x_S <= 1


Objective function

Maximize: 45*x_O + 70*x_H + 50*x_S


Notes

Funds are use-it-or-lose-it each period (no carryover).

Continuous decision variables are appropriate because fractional project shares can be purchased.

