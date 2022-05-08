from bs4 import BeautifulSoup
from flask import Flask
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import urllib.parse

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/titles/', methods=['GET'])
def titles():
  URL = "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles"
  page = requests.get(URL)

  # soup is a new instance of the BeautifulSoup library - it receives page.content instead of page.text to avoid issues with character encoding
  soup = BeautifulSoup(page.content, "lxml")
  tags = soup.find_all("a", {"class": not "image", "title": True, "accesskey": False})
  filtered_tags = []
  
  for tag in tags:
    # convert the html tag to a string
    tag = str(tag)

    # replace accented characters with their non-accented equivalent
    tag = urllib.parse.unquote_plus(tag)
    
    try:
      # get the value of the title attribute
      title_start = tag.rindex('title="') + 7
      title_end = tag.index('">')

      # get the value of the href without the /wiki/
      href_start = tag.rindex('/wiki/') + 6
      href_end = tag.index('" title=')
      edited_href = tag[href_start:href_end].replace("_", " ")

      # gets the text between the tags (<a>Text</a>)
      inner_text_start = tag.rindex('">') + 2
      inner_text_end = tag.index("</")

      # the tag's href attribute is sometimes the same as its title and sometimes the same as the inner_text
      if edited_href == tag[title_start:title_end] or edited_href == tag[inner_text_start:inner_text_end]:
        # filter out the unrelated a tags, and avoid any duplicates
        if not "Wikipedia" in tag and not "/wiki/User" in tag and not "Category" in tag and not "Template" in tag and not tag in filtered_tags:
          # add the remainder of the url after /wiki/ to filtered_tags
          filtered_tags.append(tag[href_start:href_end])

    # some tags don't start with /wiki/, for example, so would raise a ValueError
    except ValueError as ve:
      pass

  return jsonify({'data': filtered_tags})

if __name__ == '__main__':
  app.run()