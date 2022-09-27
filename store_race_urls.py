import json
import os


dict_race_urls = {
  2019: 'https://www.athlinks.com/event/33913/results/Event/711340/Results',
  2021: 'https://www.athlinks.com/event/33913/results/Event/977377/Results',
  2022: 'https://www.athlinks.com/event/33913/results/Event/1018673/Course/2248652'
}

dir_out = './data'
if not os.path.exists(dir_out):
  os.makedirs(dir_out)

with open(os.path.join(dir_out, 'race_urls.json'), 'w') as f:
  json.dump(dict_race_urls, f)