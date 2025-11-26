This repository contains self-directed projects from NYU Stern's Decision Models & Analytics course, completed as part of my MBA.
Each case applies optimization and simulation techniques to solve real-world business problems using Python.

⚙️ Dependencies
pip install pulp numpy pandas

💰 Case 4 — Cash Matching Optimization (Web Application)

**Objective:**
Determine the minimum-cost portfolio of bonds that will meet all project cash flow requirements exactly.

**Model Type:**
Linear Programming (LP)

**Features:**
- Interactive web interface built with Streamlit
- Input cash requirements (dates and amounts)
- Input bond data (maturity, coupon rate, price)
- Automatic optimization using linear programming
- Cash flow analysis with reinvestment of excess cash
- Downloadable results

**How to Run:**

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Launch the web application:
```bash
streamlit run app.py
```

3. The application will open in your default web browser. Use the tabs to:
   - **Cash Requirements**: Enter dates and cash amounts needed
   - **Bonds**: Enter available bonds with maturity, coupon rate, and price
   - **Results**: Click "Run Optimization" to solve and view results

**Key Parameters:**
- Bonds can be purchased fractionally
- Excess cash can be reinvested at a configurable rate (default: 4% annual, 2% semiannual)
- The optimization minimizes the upfront cost while meeting all cash flow requirements

🧱 Case 1 — Production Mix Optimization

Objective:
Maximize weekly profit by choosing production quantities for two products that share capacity across three plants.

Model Type:
Linear Programming (LP) / Mixed-Integer Programming (MIP)

Decision Variables

D: units of Product D (doors) per week

W: units of Product W (windows) per week

Parameters
Parameter	Description	Value
profit_D	Profit per unit (Doors)	300
profit_W	Profit per unit (Windows)	500
cap_p1	Capacity of Plant 1 (hours)	40
cap_p2	Capacity of Plant 2 (hours)	120
cap_p3	Capacity of Plant 3 (hours)	180

Processing Times (hours/unit)

Plant 1: 1 * D

Plant 2: 2 * W

Plant 3: 3 * D + 2 * W

Constraints
1*D ≤ 40         (Plant 1 capacity)
2*W ≤ 120        (Plant 2 capacity)
3*D + 2*W ≤ 180  (Plant 3 capacity)
D, W ≥ 0         (optionally integer)

Objective Function
Maximize: 300*D + 500*W


How to Run

python production_mix_pulp.py

💰 Case 2 — Multi-Period Capital Allocation (Co-Investment Shares)

Objective:
Choose fractional participation in three projects to maximize total NPV, subject to annual capital budgets.

Model Type:
Linear Programming (LP)

Decision Variables

x_O, x_H, x_S ∈ [0, 1]: fraction invested in Office, Hotel, and Shopping projects

Parameters (in $M)

Per-period Budgets

Year	Budget
0	25
1	20
2	20
3	15

Investment Needs (for 100% stake)

Year	Office	Hotel	Shopping
0	40	80	90
1	60	80	50
2	90	80	20
3	10	70	60

NPV (for 100% stake)

Office = 45

Hotel = 70

Shopping = 50

Constraints

For each year t:

Investment(t, Office)*x_O + Investment(t, Hotel)*x_H + Investment(t, Shopping)*x_S ≤ Budget(t)

Bounds
0 ≤ x_O, x_H, x_S ≤ 1

Objective Function
Maximize: 45*x_O + 70*x_H + 50*x_S


Notes:
Funds are use-it-or-lose-it each period (no carryover).
Continuous decision variables are appropriate because fractional project shares can be purchased.

Case 3 — Phone Survey Optimization

Objective:
Minimize the total cost of phone calls (landline and cell) while ensuring target demographic quotas are met.

Model Type:
Linear Programming (LP)

Decision Variables
Variable	Description
L	Total number of landline calls made
C	Total number of cell phone calls made
Parameters
Parameter	Description	Value
cost_L	Cost per landline call	$0.20
cost_C	Cost per cell phone call	$0.50

Demographic response rates (as percentages of calls answered):

Person Responding	% of Landline Calls	% of Cell Calls	Required Respondents
Young Women	8%	20%	≥ 1500
Young Men	8%	18%	≥ 1400
Older Women	20%	20%	≥ 1100
Older Men	20%	18%	≥ 1000
No Answer	44%	24%	—

Constraints

Each group’s required respondents must be met:

0.08
𝐿
+
0.20
𝐶
	
≥
1500
	
	
(Young Women)


0.08
𝐿
+
0.18
𝐶
	
≥
1400
	
	
(Young Men)


0.20
𝐿
+
0.20
𝐶
	
≥
1100
	
	
(Older Women)


0.20
𝐿
+
0.18
𝐶
	
≥
1000
	
	
(Older Men)


𝐶
	
≤
0.5
(
𝐿
+
𝐶
)
	
	
(At most half of all calls are cell)


𝐿
,
𝐶
	
≥
0
0.08L+0.20C
0.08L+0.18C
0.20L+0.20C
0.20L+0.18C
C
L,C
	​

≥1500
≥1400
≥1100
≥1000
≤0.5(L+C)
≥0 (Young Women)
(Young Men)
(Older Women)
(Older Men)
(At most half of all calls are cell)
	​

	​

Objective Function
Minimize: 
0.20
𝐿
+
0.50
𝐶
Minimize: 0.20L+0.50C
🧠 Business Interpretation

We want to find the least-cost combination of landline and cell phone calls that ensures the marketing firm reaches its target number of respondents in each demographic while respecting labor capacity (only half of total calls can be to cell phones).  

