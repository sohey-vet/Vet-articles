import json
import datetime
import os

with open('sns_schedule.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

today = datetime.date.today()
tomorrow = (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
day_after = (today + datetime.timedelta(days=2)).strftime('%Y-%m-%d')

posts = [x for x in d if x.get('platform') == 'Threads' and x.get('date') in [tomorrow, day_after]]

with open('debug_threads_posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"Found {len(posts)} posts for {tomorrow} and {day_after}.")
