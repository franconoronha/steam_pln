import requests
import json
import pandas as pd
import time
from tinydb import TinyDB

INTERVAL = 15
VERBOSE = True
LANGUAGES = ['brazilian', 'portuguese']

# https://partner.steamgames.com/doc/store/getreviews
BASE_PARAMS = {
    'json': 1,
    'filter': 'recent',
    'num_per_page': 100
}

# review_type
#   all - default
#   positive
#   negative

# purchase_type
#   all - default
#   non_steam
#   steam

# filter_offtopic_activity
#   0

PARSE_COLUMNS = [
  'timestamp_updated',
  'language',
  'review',
  'votes_up',
  'votes_funny',
  'voted_up',
  'weighted_vote_score',
  'written_during_early_access',
  'steam_purchase',
  'received_for_free'
]
COLUMNS = [
  'game',
  'author',
  'playtime_at_review',
] + PARSE_COLUMNS

def get_reviews(game_id, cursor='*', lang=0):
  url = f'https://store.steampowered.com/appreviews/{game_id}'
  params = dict(BASE_PARAMS)
  params['cursor'] = cursor
  params['language'] = LANGUAGES[lang]

  response = requests.get(url, params=params)
  data = response.json()

  success = data['success']
  if success == 1:
    summary = data['query_summary']
    log(f'Got {summary["num_reviews"]} reviews of game {game_id} at {cursor}')
    return {
        'success': success,
        'reviews': data['reviews'],
        'cursor': data['cursor']
    }
  else:
    log(f'Failed to get {game_id} at cursor {cursor}')
    return {
        'success': success,
        'reviews': [],
        'cursor': ''
    }


def relevant_info(review, game_id):
  info = {
    'game': game_id,
    'author': review['author']['steamid'],
    'playtime_at_review': review['author']['playtime_at_review']
  }
  for key in PARSE_COLUMNS:
    if key in review:
      info[key] = review[key]
    else:
      info[key] = None
  if 'review' in info:
    info['review'] = process_review(info['review'])

  return info


def process_review(text):
  return text.replace(';', '').replace('\r\n', '').replace('\r', '').replace('\n', '')


def log(message):
  if VERBOSE:
    print(message)


def save_checkpoints(checkpoints):
  with open('./data/checkpoints.json', 'w') as f:
      json.dump(checkpoints, f, indent=4)


def main():
  try:
    with open('./data/checkpoints.json', 'r') as f:
      checkpoints = json.load(f)
  except:
      checkpoints = {
          'games': 0,
          'reviews': 0,
          'cursor': '*'
      }

  try:
    pd.read_csv('./data/reviews.csv', sep=';')
  except:
    print('Creating reviews.csv')
    pd.DataFrame(columns=COLUMNS).to_csv('./data/reviews.csv', index=False, sep=';')
    checkpoints['reviews'] = 0
    checkpoints['cursor'] = '*'

  db = TinyDB('./data/games.json')
  ids = [game['steam_appid'] for game in iter(db)]

  for i in range(checkpoints['reviews'], len(ids)):
    game_id = ids[i]
    log(f'Getting reviews of game {i+1}/{len(ids)}')
    success = True
    running = True
    cursor = checkpoints['cursor']

    while running:
      result = get_reviews(game_id, cursor)
      success = result['success']

      if success:
        if len(result['reviews']) == 0:
          log(f'No more reviews of game {game_id}')
          checkpoints['cursor'] = '*'
          break
        cursor = result['cursor']
        checkpoints['cursor'] = result['cursor']

        reviews = [relevant_info(review, game_id) for review in result['reviews']]
        df = pd.DataFrame(reviews)
        df.to_csv('./data/reviews.csv', mode='a', header=False, sep=';', index=False)
        save_checkpoints(checkpoints)
      else:
        log(f'Failed to get reviews of game {game_id}')

      time.sleep(INTERVAL)

    checkpoints['reviews'] = i + 1
    save_checkpoints(checkpoints)




if __name__ == '__main__':
  main()
