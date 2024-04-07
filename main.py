from flask import Flask, request, jsonify
from fuzzywuzzy import fuzz
import re
import json
import urllib.parse

app = Flask(__name__)

# Updated data without 'id' field
data = [
    {"name": "1234567890"},
]

def contains_special_characters(keyword):
    # Define a regular expression pattern to match special characters
    pattern = r'[~@#$%^&*()]'
    return bool(re.search(pattern, keyword))

def generate_patterns(data):
    # Generate patterns from the data
    patterns = [r'[{}{}]'.format(word[0].upper(), word[0].lower()) + word[1:] for item in data for word in item['name'].split()]
    return patterns

def load_flagged_words():
    # Load filtered/flagged words from a .json file
    with open('flagged_words.json', 'r') as file:
        flagged_words = json.load(file)
    return flagged_words

patterns = generate_patterns(data)
flagged_words = load_flagged_words()

@app.route('/filter', methods=['GET'])
def filter_keyword():
    # Get the keyword from the query parameters
    keyword = request.args.get('keyword')

    # Decode the keyword to handle %20 encoding
    keyword = urllib.parse.unquote(keyword)

    # Split the keyword into separate words if it contains spaces
    keywords = keyword.split()

    # Check if any keyword contains special characters
    if any(contains_special_characters(k) for k in keywords):
        response = {"filtered": True}
    else:
        # Check if any keyword resembles a flagged word
        if any(k.lower() in flagged_words for k in keywords):
            response = {"filtered": True}
        else:
            # Threshold for similarity (adjust as needed)
            threshold = 70

            # Find words from data close to the keyword
            filtered_data = [item for item in data if any(fuzz.partial_ratio(k.lower(), item['name'].lower()) >= threshold for k in keywords)]

            # Check if filtered data is empty
            if filtered_data:
                response = {"filtered": True}
            else:
                response = {"filtered": False}

    # Return the response
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
