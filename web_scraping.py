"""Implement a web scraping script to collect data from the book of answers website.
import requests
from bs4 import BeautifulSoup
import random
import time
import json


user_agents = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'

headers = {
    'User-Agent': user_agents
}

results = {}

for i in range(1, 337):
    target_url = f'https://answersbook.iwhy.dev/page/{i}/'

    response = requests.get(target_url, headers=headers)

    if response.status_code == 200:
        time.sleep(random.uniform(0.3, 3))

        soup = BeautifulSoup(response.text, 'html.parser')

        answer = soup.find('h2').text
        explanation = soup.find('p').text

        results[i] = {
            "Answer": answer,
            "Explanation": explanation
        }

        print("Page:", i)
        print("Answer:", answer)
        print("Explanation:", explanation)

    else:
        print(f"Failed to retrieve page {i}. Status code: {response.status_code}")

with open('the_book_of_answers.json', 'w', encoding='utf-8') as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)

print("All done!")
