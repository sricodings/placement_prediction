import os
from random import randint, sample
from datetime import datetime, timedelta

# Define the year
year = 2023

# Get all days in 2023
start_date = datetime(year, 6, 6)
end_date = datetime(year, 12, 12)
days_in_year = (end_date - start_date).days + 1

# Select 87 random days in 2023
selected_days = sample(range(0, days_in_year), 15)

# Iterate through the selected days
for day_offset in selected_days:
    # Calculate the date
    commit_date = start_date + timedelta(days=day_offset)
    # Generate a random number of commits (1 to 4) for the day
    num_commits = randint(1, 4)
    for _ in range(num_commits):
        # Format the commit date
        formatted_date = commit_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Simulate a file change
        with open("file.txt", "a") as file:
            file.write(f"Commit made on {formatted_date}\n")
        
        # Add changes to Git and commit with the specific date
        os.system('git add .')
        os.system(f'GIT_COMMITTER_DATE="{formatted_date}" git commit --date="{formatted_date}" -m "Random commit for 2023"')

# Push the changes to the repository
os.system('git push -u origin main')
