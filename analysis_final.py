# %% [markdown]
# # UIDAI Aadhaar Enrolment Analysis  
# ## Governance-First Analytics Framework
# 
# **Purpose:**  
# This analysis demonstrates how aggregate Aadhaar enrolment trends can appear positive while masking underlying demographic concentration risks.  
# The goal is to discourage blind trust in headline numbers and introduce confidence-aware decision support.
# 

# %% [markdown]
# ## Data Ingestion
# 
# This section loads and merges raw UIDAI Aadhaar enrolment CSV files into a single dataset for analysis.
# 

# %%
import pandas as pd
import os

# Path to raw UIDAI data
DATA_PATH = "../data_raw"

# Load all CSV files
files = sorted([f for f in os.listdir(DATA_PATH) if f.endswith(".csv")])

dfs = []
for file in files:
    df = pd.read_csv(os.path.join(DATA_PATH, file))
    dfs.append(df)

merged_df = pd.concat(dfs, ignore_index=True)

merged_df.shape


# %% [markdown]
# ## Step 2: Data Cleaning & State Filtering
# 
# This step standardizes state names and filters the dataset to include
# only the 28 Indian states used for governance analysis.
# 
# This ensures:
# - Consistent naming (no casing / spacing issues)
# - Removal of UTs, duplicates, and noisy entries
# - A stable foundation for state-level confidence analysis
# 

# %%

merged_df["state"] = (
    merged_df["state"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ---------------------------------------
# Define official 28 Indian states
# ---------------------------------------

INDIA_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
]

# ---------------------------------------
# Filter to 28 states only
# ---------------------------------------

state_df = merged_df[merged_df["state"].isin(INDIA_STATES)].copy()

state_df["state"].nunique(), state_df.shape


# %% [markdown]
# ## Step 3: National Aggregate Trend (Misleading by Design)
# 
# This section intentionally aggregates Aadhaar enrolments across all states
# and age groups to produce a single national trend.
# 
# While this view appears strong and reassuring,
# it conceals underlying demographic concentration.
# 
# This mirrors how high-level dashboards are often interpreted
# without sufficient context.
# 

# %%
# ---------------------------------------
# Step 3: National aggregate (MISLEADING VIEW)
# ---------------------------------------

# Convert date column
state_df["date"] = pd.to_datetime(state_df["date"], dayfirst=True)

# Total enrolments per row
state_df["total_enrolments"] = (
    state_df["age_0_5"]
    + state_df["age_5_17"]
    + state_df["age_18_greater"]
)

# Aggregate nationally by date
national_trend = (
    state_df
    .groupby("date")["total_enrolments"]
    .sum()
    .reset_index()
    .sort_values("date")
)

national_trend.head()


# %% [markdown]
# ## Step 4: Decomposing the National Trend by Age Group
# 
# The national aggregate trend conceals how enrolments are distributed
# across different age groups.
# 
# This section breaks down the same data by age category
# to examine whether growth is uniform or concentrated.
# 
# This helps identify whether the apparent national improvement
# reflects broad participation or dominance by a single demographic.
# 

# %%

age_trend = (
    state_df
    .groupby("date")[["age_0_5", "age_5_17", "age_18_greater"]]
    .sum()
    .reset_index()
    .sort_values("date")
)

age_trend.head()


# %% [markdown]
# ## Step 5: Measuring Demographic Dominance (Confidence Score)
# 
# To assess whether the national trend reflects balanced participation,
# we measure how much of total enrolment is driven by a single age group.
# 
# If one demographic dominates the total,
# the aggregate trend becomes less representative.
# 
# We define a confidence score as:
# 
# Confidence Score = 1 − (Share of Dominant Age Group)
# 
# Lower confidence scores indicate higher risk of misleading interpretation.
# 

# %%


# Total enrolments per day
age_trend["total_enrolments"] = (
    age_trend["age_0_5"]
    + age_trend["age_5_17"]
    + age_trend["age_18_greater"]
)

# Share of dominant age group
age_trend["max_share"] = (
    age_trend[["age_0_5", "age_5_17", "age_18_greater"]]
    .max(axis=1) / age_trend["total_enrolments"]
)

# Confidence score (governance-safe metric)
age_trend["confidence_score"] = 1 - age_trend["max_share"]

age_trend[["date", "confidence_score"]].head()


# %% [markdown]
# ## Step 6: Visualizing the Demographic Imbalance
# 
# The following visualization shows how the national enrolment trend
# is composed across different age groups over time.
# 
# Although total enrolments increase steadily,
# the growth is disproportionately driven by a single demographic segment.
# 
# This visual evidence supports the confidence warning
# shown in the dashboard.
# 

# %%
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

plt.stackplot(
    age_trend["date"],
    age_trend["age_0_5"],
    age_trend["age_5_17"],
    age_trend["age_18_greater"],
    labels=["Age 0–5", "Age 5–17", "Age 18+"]
)

plt.legend(loc="upper left")
plt.title("National Aadhaar Enrolment Trend by Age Group")
plt.xlabel("Date")
plt.ylabel("Number of Enrolments")

plt.tight_layout()

# save for dashboard
plt.savefig("../plots/age_group_trend.png", dpi=300)

# show in notebook
plt.show()

# then close to avoid overlap
plt.close()


# %% [markdown]
# ## Step 7: State-Level Decomposition (Governance View)
# 
# To support informed decision-making, the national trend is decomposed
# at the state level.
# 
# This allows comparison between:
# - total enrolment volume
# - demographic balance behind that volume
# 
# The goal is not to rank performance alone,
# but to identify regions where aggregate numbers may be misleading.
# 

# %%

state_summary = (
    state_df
    .groupby("state")[["age_0_5", "age_5_17", "age_18_greater"]]
    .sum()
    .reset_index()
)

state_summary["total_enrolments"] = (
    state_summary["age_0_5"]
    + state_summary["age_5_17"]
    + state_summary["age_18_greater"]
)

state_summary.head()


# %% [markdown]
# ## Step 8: State-Level Confidence Score
# 
# Using the same demographic dominance logic applied at the national level,
# we compute a confidence score for each state.
# 
# This score reflects how balanced enrolments are across age groups.
# Lower confidence indicates higher risk of misleading aggregate interpretation.
# 

# %%

# Share of dominant age group per state
state_summary["max_share"] = (
    state_summary[["age_0_5", "age_5_17", "age_18_greater"]]
    .max(axis=1) / state_summary["total_enrolments"]
)

# Confidence score (governance-safe metric)
state_summary["confidence_score"] = 1 - state_summary["max_share"]

state_summary[[
    "state",
    "total_enrolments",
    "confidence_score"
]].head()


# %% [markdown]
# ## Step 9: Bias Risk Classification
# 
# To make confidence scores actionable for non-technical users,
# each state is assigned a bias risk category.
# 
# These categories indicate how safely aggregate enrolment numbers
# can be interpreted for decision-making.
# 

# %%


def bias_flag(score):
    if score < 0.4:
        return "High bias risk"
    elif score < 0.6:
        return "Moderate bias risk"
    else:
        return "Low bias risk"

state_summary["bias_flag"] = state_summary["confidence_score"].apply(bias_flag)

state_summary[[
    "state",
    "total_enrolments",
    "confidence_score",
    "bias_flag"
]].head()


# %% [markdown]
# ## Step 10: Saving Final Outputs for Dashboard
# 
# This step saves the final, governed state-level dataset
# used by the single-page dashboard.
# 
# From this point onward, all visualizations and interactions
# are driven from these frozen outputs.
# 

# %%


# Sort for dashboard readability
state_summary = state_summary.sort_values(
    "total_enrolments",
    ascending=False
)

# Save CSV for Streamlit dashboard
state_summary.to_csv(
    "../plots/state_confidence_table.csv",


# %%
    index=False
)

# Sanity check
state_summary.shape, state_summary["state"].nunique()


# %% [markdown]
# ### How the Aggregate Number Is Composed
# 
# While the national enrolment trend appears strong,
# this aggregate number is driven unevenly across age groups.
# 
# The following breakdown shows the total contribution of each age segment,
# highlighting demographic concentration behind the overall growth.
# 

# %%
import matplotlib.pyplot as plt

# ---------------------------------------
# Aggregate enrolments by age group
# ---------------------------------------

age_totals = state_df[
    ["age_0_5", "age_5_17", "age_18_greater"]
].sum()

plt.figure(figsize=(7, 5))

plt.bar(
    age_totals.index,
    age_totals.values
)

plt.title("Aggregate Aadhaar Enrolments by Age Group")
plt.xlabel("Age Group")
plt.ylabel("Total Enrolments")

plt.tight_layout()

# Save for dashboard
plt.savefig("../plots/aggregate_enrolments.png", dpi=300)

plt.show()
plt.close()


# %% [markdown]
# ## Total Enrolments vs Confidence Score (State-wise)
# 
# This visualization compares enrolment volume with confidence score
# to highlight regions where high aggregate numbers may still be unreliable.
# 
# States with high enrolments but low confidence
# require cautious interpretation before action.
# 

# %%
plt.figure(figsize=(10, 6))

colors = state_summary["bias_flag"].map({
    "High bias risk": "#D62728",
    "Moderate bias risk": "#FF7F0E",
    "Low bias risk": "#2CA02C"
})

plt.scatter(
    state_summary["total_enrolments"],
    state_summary["confidence_score"],
    c=colors,
    alpha=0.8,
    s=80
)

# Threshold lines
plt.axhline(0.4, linestyle="--", linewidth=1)
plt.axhline(0.6, linestyle="--", linewidth=1)

x_pos = state_summary["total_enrolments"].max() * 0.55

# Correct label placement
plt.text(x_pos, 0.25, "High bias risk", fontsize=9)
plt.text(x_pos, 0.50, "Moderate bias risk", fontsize=9)
plt.text(x_pos, 0.75, "Low bias risk", fontsize=9)

plt.title("State-wise Enrolments vs Confidence Score")
plt.xlabel("Total Enrolments")
plt.ylabel("Confidence Score")

plt.tight_layout()
plt.savefig("../plots/enrolments_vs_confidence.png", dpi=300)
plt.show()
plt.close()



