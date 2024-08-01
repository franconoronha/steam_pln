# import sqlite3
import json
import requests
from tinydb import TinyDB
import time

URL = 'https://store.steampowered.com/api/appdetails'
INTERVAL = 12

def main():
    with open('./data/game_ids.txt', 'r') as f:
        game_ids = f.read().splitlines()
    
    db = TinyDB('./data/games.json')
    try:
        with open('./data/failed_requests.json', 'r') as f:
            failed_req = json.load(f)['ids']
    except:
        failed_req = []

    try:
        with open('./data/checkpoints.json', 'r') as f:
            checkpoints = json.load(f)
    except:
        checkpoints = {
            'games': 0,
            'reviews': 0,
            'cursor': '*',
            'stop_at': -1
        }

    for i in range(checkpoints['games'], len(game_ids)):
        game_id = game_ids[i]
        print(f'Getting game {i+1}/{len(game_ids)}')
        success = get_game(game_id, db)
        if success:
            time.sleep(INTERVAL)
        else:
            print(f'Failed to get game {game_id}')
            failed_req.append(game_id)	

        checkpoints['games'] = i + 1
        with open('./data/checkpoints.json', 'w') as f:
            json.dump(checkpoints, f, indent=4)
        with open('./data/failed_requests.json', 'w') as f:
            json.dump({ 'ids': failed_req }, f, indent=4)


def get_game(game_id, db):
    req = requests.get(f'{URL}?appids={game_id}')
    if req.status_code != 200:
        return False
    
    res = req.json()
    if res[game_id]['success']:
        data = res[game_id]['data']
        if 'screenshots' in data:
            del data['screenshots']
        if 'movies' in data:
            del data['movies']
        if 'support_info' in data:
            del data['support_info']
        if 'package_grops' in data:
            del data['package_groups']
        db.insert(data)
        return True
    else:
        return False
    

if __name__ == '__main__':
    main()