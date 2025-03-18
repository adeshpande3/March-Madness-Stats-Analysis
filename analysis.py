from typing import Dict, List
import pandas as pd
import re
import ast

def parse_roster(roster_str: str) -> List[Dict]:
    """Parse roster string into list of dictionaries"""
    try:
        if isinstance(roster_str, str):
            return ast.literal_eval(roster_str)
        return roster_str
    except (ValueError, SyntaxError):
        return []

def is_good_scoring_team(row: pd.Series) -> bool:
    """Check if team is good at scoring (top 50 in points per game)"""
    try:
        rank = int(row['PTS Rank'])
        return rank <= 50
    except (ValueError, KeyError):
        return False

def forces_turnovers(row: pd.Series) -> bool:
    """Check if team is good at forcing turnovers (top 50 in opponent turnovers)"""
    try:
        rank = int(row['Opponent TOV Rank'])
        return rank <= 50
    except (ValueError, KeyError):
        return False

def protects_basketball(row: pd.Series) -> bool:
    """Check if team is good at protecting the ball (top 50 in avoiding turnovers)"""
    try:
        rank = int(row['TOV Rank'])
        # Note: For turnovers, a higher rank is better (means fewer turnovers)
        return rank >= 300  # Being in the bottom 50 in turnovers is good
    except (ValueError, KeyError):
        return False

def high_volume_three_point_team(row: pd.Series) -> bool:
    """Check if team makes a lot of 3s (top 50 in 3PT made per game)"""
    try:
        rank = int(row['3P Rank'])
        return rank <= 50
    except (ValueError, KeyError):
        return False

def elite_offensive_rebounding(row: pd.Series) -> bool:
    """Check if team is elite at offensive rebounding (top 50)"""
    try:
        rank = int(row['ORB Rank'])
        return rank <= 50
    except (ValueError, KeyError):
        return False

def has_experienced_core(row: pd.Series) -> bool:
    """Check if team has more upperclassmen than lowerclassmen in top 5 scorers"""
    try:
        roster = parse_roster(row['roster'])
        if not roster or len(roster) < 5:
            return False
        
        # Take first 5 players (already sorted by scoring)
        top_5 = roster[:5]
        
        # Count upperclassmen (JR/SR) vs lowerclassmen (FR/SO)
        upperclassmen = sum(1 for player in top_5 if player.get('class', '') in ['JR', 'SR'])
        lowerclassmen = sum(1 for player in top_5 if player.get('class', '') in ['FR', 'SO'])
        
        return upperclassmen > lowerclassmen
    except (KeyError, AttributeError):
        return False

def has_top_recruits(row: pd.Series) -> bool:
    """Check if team has 2 or more top 100 recruits in first 5 players"""
    try:
        roster = parse_roster(row['roster'])
        if not roster or len(roster) < 5:
            return False
        
        # Take first 5 players
        top_5 = roster[:5]
        
        # Count players with RSCI rank <= 100
        top_recruits = 0
        for player in top_5:
            rsci = player.get('rsci_rank', '')
            # Extract number from RSCI rank (handles formats like "37 (2021)")
            match = re.match(r'(\d+)', rsci)
            if match and int(match.group(1)) <= 100:
                top_recruits += 1
        
        return top_recruits >= 2
    except (KeyError, AttributeError):
        return False

def has_scoring_guard(row: pd.Series) -> bool:
    """Check if team has a guard in first 5 players scoring > 15 ppg"""
    try:
        roster = parse_roster(row['roster'])
        if not roster or len(roster) < 5:
            return False
        
        # Take first 5 players
        top_5 = roster[:5]
        
        for player in top_5:
            # Check if player is a guard
            if player.get('pos', '') in ['G', 'PG', 'SG']:
                # Extract points from summary (format: "17.5 Pts, 4.2 Reb, 4.0 Ast")
                summary = player.get('stats_summary', '')
                if summary:
                    pts_match = re.match(r'(\d+\.?\d*)\s*Pts', summary)
                    if pts_match and float(pts_match.group(1)) > 15:
                        return True
        return False
    except (KeyError, AttributeError):
        return False

def has_size(row: pd.Series) -> bool:
    """Check if team has 3 or more players 6-8 or taller in first 5 players"""
    try:
        roster = parse_roster(row['roster'])
        if not roster or len(roster) < 5:
            return False
        
        # Take first 5 players
        top_5 = roster[:5]
        
        # Count players 6-8 or taller
        tall_players = 0
        for player in top_5:
            height = player.get('height', '')
            if height:
                # Convert height (e.g., "6-8") to inches
                try:
                    feet, inches = map(int, height.split('-'))
                    total_inches = feet * 12 + inches
                    if total_inches >= 78:  # 6-6 = 78 inches
                        tall_players += 1
                except ValueError:
                    continue
        
        return tall_players >= 3
    except (KeyError, AttributeError):
        return False

def good_defense(row: pd.Series) -> bool:
    """Check if team is good at defense (top 50 in opponent points per game)"""
    try:
        rank = int(row['Opponent PTS Rank'])
        return rank <= 50
    except (ValueError, KeyError):
        return False

def defends_three_point(row: pd.Series) -> bool:
    """Check if team defends the three well (top 50 in opponent 3P percentage)"""
    try:
        rank = int(row['Opponent 3P% Rank'])
        return rank <= 50
    except (ValueError, KeyError):
        return False

def good_free_throw_team(row: pd.Series) -> bool:
    """Check if team shoots free throws well (top 50 in FT percentage)"""
    try:
        rank = int(row['FT% Rank'])
        return rank <= 50
    except (ValueError, KeyError):
        return False

# Dictionary mapping analysis functions to their column names
ANALYSIS_FUNCTIONS = {
    'Can Score': is_good_scoring_team,
    'Forces Turnovers': forces_turnovers,
    'Protects the Ball': protects_basketball,
    'High Volume 3PT Team': high_volume_three_point_team,
    'Elite Offensive Rebounding': elite_offensive_rebounding,
    'Good Defense': good_defense,
    'Defends Three Point': defends_three_point,
    'Good Free Throw Team': good_free_throw_team,
    'Experienced Core': has_experienced_core,
    'Multiple Top Recruits': has_top_recruits,
    'Has Scoring Guard': has_scoring_guard,
    'Has Size': has_size,
}

def analyze_teams(stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze team statistics and create a new DataFrame with yes/no answers to various questions
    
    Args:
        stats_df: DataFrame containing team statistics and rankings
        
    Returns:
        DataFrame with analysis results
    """
    # Create a new DataFrame with just year and team
    analysis_df = stats_df[['year', 'team']].copy()
    
    # Apply each analysis function
    for col_name, func in ANALYSIS_FUNCTIONS.items():
        analysis_df[col_name] = stats_df.apply(func, axis=1)
        
    # Convert boolean results to Yes/No
    for col in ANALYSIS_FUNCTIONS.keys():
        analysis_df[col] = analysis_df[col].map({True: 'Yes', False: 'No'})
    
    return analysis_df

if __name__ == "__main__":
    # Read the original stats CSV
    stats_df = pd.read_csv('final_four_teams.csv')
    
    # Perform analysis
    analysis_df = analyze_teams(stats_df)
    
    # Save results
    analysis_df.to_csv('team_analysis.csv', index=False)
    print("Analysis complete. Results saved to team_analysis.csv")
    print("\nAnalysis Results:")
    print(analysis_df) 