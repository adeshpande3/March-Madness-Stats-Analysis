# March Madness Analysis

(LOL this same project woulda taken me a week a couple years ago. I used Cursor and did 
this in like 45 minutes. Insane)

The idea behind this is to try to test out different "claims" about what makes a 
basketball team good. Ones like "you need experienced guards to win in March" or "size matters in the tournament".

<img width="1267" alt="image" src="https://github.com/user-attachments/assets/e3694379-5274-46ca-b1aa-66dd4e9e03c1" />

This repo scrapes historical Final Four team data and sees whether certain takes end up being true. 

## Features

- Scrapes Final Four team data from sports-reference.com
- Analyzes team statistics and rankings
- Evaluates roster composition including:
  - Experience level of top scorers
  - Presence of highly recruited players (Top 100 RSCI)
  - Guard scoring prowess
  - Team size and height metrics
- Generates comprehensive CSV reports with analysis results

## Analysis Metrics

Currently the tool evaluates teams based on several criteria:

1. **Team Statistics**
   - Scoring efficiency (top 50 in points per game)
   - Turnover metrics (forcing and preventing)
   - Three-point shooting (volume and efficiency)
   - Offensive rebounding

2. **Roster Analysis**
   - Experience level of top 5 scorers (upperclassmen vs lowerclassmen)
   - Top recruits in the playing rotation
   - Presence of high-scoring guards (>17 PPG)
   - Team height (number of players 6'8" or taller in rotation)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main scraping script:
```bash
python create_data.py
```

This will:
1. Scrape Final Four teams' data
2. Save raw data to `final_four_teams.csv`

Then run the analysis:
```bash
python analysis.py
```

This will:
1. Read the raw data
2. Perform analysis on team composition and statistics
3. Generate `team_analysis.csv` with the results

## Output

The analysis generates two CSV files:

1. `final_four_teams.csv`: Raw data including:
   - Team statistics and rankings
   - Complete roster information
   - Player statistics and background

2. `team_analysis.csv`: Analyzed results with Yes/No answers to key questions about:
   - Team statistical performance
   - Roster composition
   - Player experience and talent level

## If you want to modify for your own usage
If you want to modify this code for your own analysis:

1. Update the statistics thresholds in `analysis.py`:
   - Adjust the ranking thresholds (currently top 50) in functions like `is_good_scoring_team()`
   - Modify the scoring threshold (>15 ppg) in `has_scoring_guard()`
   - Change the height requirement (6'8") in `has_size()`

2. Add or remove analysis metrics:
   - Create new analysis functions in `analysis.py`
   - Add them to the `ANALYSIS_FUNCTIONS` dictionary
   - The function names will become column headers in the output

3. Change the years analyzed:
   - Modify the year range in `get_recent_final_four_teams()` in `create_data.py`
   - Currently set to analyze the last 15 years
   - Be mindful that older years may have different HTML structure

4. Adjust the data sources:
   - Update the URL patterns in `create_data.py` if using different sports reference sites
   - Modify the HTML parsing logic if the page structure changes
   - Add error handling for any new edge cases

5. Customize the output:
   - Change the CSV column names in `analyze_teams()`
   - Modify the output format in `to_csv()` calls
   - Add additional output files as needed

## Dependencies

- requests==2.31.0: For web scraping
- beautifulsoup4==4.12.2: For HTML parsing
- pandas==1.3.5: For data analysis
- urllib3<2.0.0: HTTP client (version restricted for compatibility)

## Notes

- The scraper includes delays between requests to be respectful to sports-reference.com
- Data is focused on Final Four teams from recent years
- All statistics are based on regular season performance
