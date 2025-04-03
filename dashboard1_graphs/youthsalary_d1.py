import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV data into a DataFrame.
df = pd.read_csv(r"data\Youth_Salary_vs_Rent_Prices.csv")

# If needed, ensure the columns match:
# df.columns = ["Year", "Average_Youth_Salary", "Average_Monthly_Rent"]

# Create positions for each year on the x-axis.
years = df['Year']
x = np.arange(len(years))
bar_width = 0.35  # width for the bars

# Create the figure and axis.
fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars for each series with updated colors.
bars_salary = ax.bar(x - bar_width/2, df['Average_Youth_Salary'],
                     bar_width, label='Average Youth Salary', color='lightgray', alpha=0.8)
bars_rent = ax.bar(x + bar_width/2, df['Average_Monthly_Rent'],
                   bar_width, label='Average Monthly Rent', color='#dcef6e', alpha=0.8)

# Overlay line plots for each series using the same positions (with markers) and updated colors.
ax.plot(x - bar_width/2, df['Average_Youth_Salary'], color='lightgray', marker='o', linewidth=2)
ax.plot(x + bar_width/2, df['Average_Monthly_Rent'], color='#dcef6e', marker='o', linewidth=2)

# Customize the plot.
ax.set_xlabel("Year")
ax.set_ylabel("Amount in $")
ax.set_title("Average Youth Salary vs Average Monthly Rent Prices")
ax.set_xticks(x)
ax.set_xticklabels(years, rotation=45)
ax.set_ylim(600, 1200)
ax.legend()
ax.grid(True)


plt.tight_layout()
plt.show()
