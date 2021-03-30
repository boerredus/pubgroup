import json

def main():
    json.dump({ 'url': input('Paste your Amazon (shared) wishlist URL here.\n(it should look like \'https://www.amazon.com.**/hz/wishlist/ls/FUYL********\'): ') }, open('config.json', 'w'), ensure_ascii=False)
    print('All done here! Go ahead and run `app.py`.')

main()