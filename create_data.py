import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict
import urllib.parse
import re

def clean_rank_text(rank_text: str) -> str:
    """
    Remove ranking suffixes (st, nd, rd, th) from a rank number
    
    Args:
        rank_text (str): The rank text to clean
        
    Returns:
        str: The cleaned rank number
    """
    # Remove any ordinal suffix using regex
    return re.sub(r'(?<=\d)(st|nd|rd|th)', '', rank_text.strip())

def get_team_stats(team_link: str, year: int) -> Dict:
    """
    Get team statistics and roster from their season page
    
    Args:
        team_link (str): The href link to the team's page
        year (int): The year to get stats for
        
    Returns:
        Dict: Dictionary containing team statistics and roster information
    """
    # Extract school name from the link
    school = team_link.split('/')[-3]
    
    # Construct the full URL for the team's season page
    url = f"https://www.sports-reference.com/cbb/schools/{school}/men/{year}.html"
    
    # Add a small delay to be respectful to the server
    time.sleep(3)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        team_stats = {}
        
        # Get roster information
        roster_table = soup.find('table', {'id': 'roster'})
        if roster_table:
            roster_data = []
            # Get all rows from roster tbody
            for row in roster_table.find('tbody').find_all('tr'):
                player_data = {}
                # Extract player information
                player_cell = row.find('td', {'data-stat': 'player'})
                if not player_cell:  # Check if it's in th instead of td
                    player_cell = row.find('th', {'data-stat': 'player'})
                
                # Get player name, handling both link and direct text cases
                if player_cell:
                    player_link = player_cell.find('a')
                    if player_link:
                        player_data['player'] = player_link.text.strip()
                        player_data['player_link'] = player_link.get('href', '')
                    else:
                        player_data['player'] = player_cell.text.strip()
                        player_data['player_link'] = ''

                # Extract other player information, handling potential missing data
                for stat in ['number', 'class', 'pos', 'height', 'weight', 'hometown', 'high_school']:
                    cell = row.find('td', {'data-stat': stat})
                    player_data[stat] = cell.text.strip() if cell else ''
                
                # Handle RSCI ranking (might be empty with 'iz' class)
                rsci_cell = row.find('td', {'data-stat': 'rsci'})
                player_data['rsci_rank'] = rsci_cell.text.strip() if (rsci_cell and not 'iz' in rsci_cell.get('class', [])) else ''
                
                # Add stats summary
                summary_cell = row.find('td', {'data-stat': 'summary'})
                player_data['stats_summary'] = summary_cell.text.strip() if summary_cell else ''
                
                roster_data.append(player_data)
            
            team_stats['roster'] = roster_data
        
        # Find the Per Game stats table with correct ID
        stats_table = soup.find('table', {'id': 'season-total_per_game'})
        if not stats_table:
            print(f"Could not find stats table for {school} in {year}")
            return team_stats
            
        # Get all rows from tbody
        tbody = stats_table.find('tbody')
        if not tbody or len(tbody.find_all('tr')) < 4:  # We need exactly 4 rows
            print(f"Not enough rows in stats table for {school} in {year}")
            return team_stats
            
        rows = tbody.find_all('tr')
            
        # Define the base stats we want to capture rankings for
        base_stats = {
            'fg_per_g': 'FG Rank',
            'fga_per_g': 'FGA Rank',
            'fg_pct': 'FG% Rank',
            'fg2_per_g': '2P Rank',
            'fg2a_per_g': '2PA Rank',
            'fg2_pct': '2P% Rank',
            'fg3_per_g': '3P Rank',
            'fg3a_per_g': '3PA Rank',
            'fg3_pct': '3P% Rank',
            'ft_per_g': 'FT Rank',
            'fta_per_g': 'FTA Rank',
            'ft_pct': 'FT% Rank',
            'orb_per_g': 'ORB Rank',
            'drb_per_g': 'DRB Rank',
            'trb_per_g': 'TRB Rank',
            'ast_per_g': 'AST Rank',
            'stl_per_g': 'STL Rank',
            'blk_per_g': 'BLK Rank',
            'tov_per_g': 'TOV Rank',
            'pf_per_g': 'PF Rank',
            'pts_per_g': 'PTS Rank'
        }
        
        # Process team rankings (row index 1 - second row)
        team_rank_row = rows[1]  # Row with class="note"
        for cell in team_rank_row.find_all(['th', 'td']):
            stat_name = cell.get('data-stat', '')
            if stat_name in base_stats:
                rank_text = cell.text.strip()
                team_stats[base_stats[stat_name]] = clean_rank_text(rank_text)
        
        # Process opponent rankings (row index 3 - fourth row)
        opp_rank_row = rows[3]  # Row with class="note"
        for cell in opp_rank_row.find_all(['th', 'td']):
            stat_name = cell.get('data-stat', '')
            # Remove 'opp_' prefix to match with base_stats
            base_stat_name = stat_name.replace('opp_', '')
            if base_stat_name in base_stats:
                rank_text = cell.text.strip()
                team_stats[f"Opponent {base_stats[base_stat_name]}"] = clean_rank_text(rank_text)
                
        return team_stats
        
    except requests.RequestException as e:
        print(f"Error fetching stats for {school} in {year}: {e}")
        return {}

def get_final_four_teams(year: int) -> List[Dict[str, str]]:
    """
    Scrape Final Four teams for a given year from sports-reference.com
    
    Args:
        year (int): The year to scrape data for
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing team information
    """
    url = f"https://www.sports-reference.com/cbb/seasons/men/{year}.html"
    
    # Add a small delay to be respectful to the server
    time.sleep(1)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the paragraph containing "Final Four"
        final_four_section = soup.find('strong', string='Final Four')
        if not final_four_section:
            print(f"Could not find Final Four section for year {year}")
            return []
            
        # Get the parent paragraph that contains all the team links
        teams_paragraph = final_four_section.find_parent('p')
        if not teams_paragraph:
            print(f"Could not find teams paragraph for year {year}")
            return []
            
        # Extract team names and stats from the links
        teams = []
        team_links = teams_paragraph.find_all('a')
        
        for team_link in team_links:
            team_name = team_link.text.strip()
            team_href = team_link.get('href', '')
            
            # Get team stats
            team_data = {
                'year': year,
                'team': team_name,
            }
            
            # Get additional stats from team page
            if team_href:
                team_stats = get_team_stats(team_href, year)
                team_data.update(team_stats)
            
            teams.append(team_data)
            
        return teams
        
    except requests.RequestException as e:
        print(f"Error fetching data for year {year}: {e}")
        return []

def get_recent_final_four_teams() -> pd.DataFrame:
    """
    Get Final Four teams for the last 3 years
    
    Returns:
        pd.DataFrame: DataFrame containing Final Four teams and their results
    """
    current_year = 2025
    all_teams = []
    
    for year in range(current_year - 15, current_year):
        print(f"Scraping data for year {year}...")
        teams = get_final_four_teams(year)
        all_teams.extend(teams)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_teams)
    
    # Reorder columns to put year and team first
    cols = ['year', 'team'] + [col for col in df.columns if col not in ['year', 'team']]
    df = df[cols]
    
    # Save to CSV
    df.to_csv('final_four_teams.csv', index=False)
    print(f"Found teams with stats:\n{df}")
    return df

if __name__ == "__main__":
    print("Starting to scrape Final Four teams from the last 3 years...")
    df = get_recent_final_four_teams()
    print(f"Successfully scraped {len(df)} teams")
    print("Data saved to final_four_teams.csv")
