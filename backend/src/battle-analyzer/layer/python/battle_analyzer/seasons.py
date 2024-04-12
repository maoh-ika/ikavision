seasons = {
    'splatoon3': [
        { 'name': '2022_drizzle_season', 'start_timestamp': 1662688800, 'end_timestamp': 1669860000 },
        { 'name': '2022_chill_season', 'start_timestamp': 1669860000, 'end_timestamp': 1677636000 },
        { 'name': '2023_fresh_season', 'start_timestamp': 1677636000, 'end_timestamp': 1685584800 },
        { 'name': '2023_sizzle_season', 'start_timestamp': 1685584800, 'end_timestamp': 1693533600 },
        { 'name': '2023_drizzle_season', 'start_timestamp': 1693533600, 'end_timestamp': 1701396000 },
        { 'name': '2023_chill_season', 'start_timestamp': 1701396000, 'end_timestamp': 1709258400 },
        { 'name': '2024_fresh_season', 'start_timestamp': 1709258400, 'end_timestamp': 1717207200 },
    ]
}

def find_season_info_by_date(title: str, date: int) -> dict:
    if title not in seasons:
        return None
    
    season = list(filter(lambda s: s['start_timestamp'] <= date and date < s['end_timestamp'], seasons[title]))
    if len(season) != 1:
        return None

    return season[0]

def find_season_info_by_name(title: str, season_name: int) -> dict:
    if title not in seasons:
        return None
    
    season = list(filter(lambda s: s['name'] == season_name, seasons[title]))
    if len(season) != 1:
        return None

    return season[0]