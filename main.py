# -*- coding: utf-8 -*-
# base-aa-pgsql.py
# base configuration
# (C) 2018 IKAUE, Marketing de Optimizacion
# created by Albert Moral Lleó <albert@ikaue.com>

# PRE-REQUISITES
# Python 3.x (tested with version 2.7.13 on Debian 9 x86_64)
# lxml (pip install lxml)
# requests (pip install requests)

from google.cloud import language_v1
import os
from urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
from googlesearch import search


def get_urls(keyword, gcnl_max_results):
    """

    :param keyword: string concatenated with "+" to perform a bs4 query search
    :param gcnl_max_results: max url to get for each query
    :return:
    """

    # to search
    query = keyword

    links = []
    for j in search(query, num=gcnl_max_results, stop=gcnl_max_results, pause=2):
        links.append(j)
    """ 
    urls = []
  
    page = requests.get(
      "https://www.google.es/search?q=%s&oq=%s&aqs=chrome.0.69i59j69i60j0.2775j0j9&sourceid=chrome&ie=UTF-8&num=%s" % (
        keyword, keyword, gcnl_max_results))
    soup = BeautifulSoup(page.content, "html.parser")
    links = soup.findAll("a")
    for link in links:
      link_href = link.get('href')
      if "url?q=" in link_href and not "webcache" in link_href:
        urls.append(link.get('href').split("?q=")[1].split("&sa=U")[0])
  
    return urls[:5]
    """
    return links


def get_html_text(urls):
    # configuration: service account JSON key file
    json_key_file = "google-credentials-analytics.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_file

    # build the Google Cloud Natural Language (GCNL) service object
    results_text = {}
    for url in urls:
        # print the keyword to analyze

        req = Request(url, headers={
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        results_text[url] = '\n'.join(chunk for chunk in chunks if chunk)

    return results_text


def sample_analyze_entities(text_content, json_key_file_path="google-credentials-analytics.json"):
    """
    Analyzing Entities in a String

    Args:
      text_content The text content to analyze
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_file_path
    client = language_v1.LanguageServiceClient()

    # text_content = 'California is a state.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = ""
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entities(request={'document': document, 'encoding_type': encoding_type})

    return response


def retrieve_text_by_url(gcnl_keywords):
    for keyword in gcnl_keywords:

        print(u">> keyword: '%s'" % keyword)
        keyword = '+'.join(keyword.split())

        # Retrieve 5 top urls
        urls = get_urls(keyword, gcnl_max_results)

        # OBTENER TEXT LIMITE 5000 paraules.

        text_by_url[keyword] = get_html_text(
            urls)  # dict con keys de cada keyword, y dentro de cada key otro dict por cada url y su texto

    return text_by_url


def obtain_nlp_csv():
    csv_final = []
    for key in text_by_url.keys():
        for url in text_by_url[key].keys():

            """# Obtain 1000 words aprox (obtaining 7000 characters with a medium of 7 chars by expresion)
            words = [t for t in text_by_url[key][url].split()]
            words_limited = 5000 if len(words) > gcnl_max_words else 0 #If there are more than 1000 words apply an average of 4000 characters per 1000 words (average of 4 letters per word)
      
            #sample_analyze_entities(words_limited)"""

            response = sample_analyze_entities(text_by_url[key][url][:1000])  # Only pass 1000 chars to google

            # Loop through entitites returned from the API
            for entity in response.entities:
                csv = [url, entity.name, language_v1.Entity.Type(entity.type_).name, entity.salience]

                print(u"Representative name for the entity: {}".format(entity.name))

                # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
                print(u"Entity type: {}".format(language_v1.Entity.Type(entity.type_).name))

                # Get the salience score associated with the entity in the [0, 1.0] range
                print(u"Salience score: {}".format(entity.salience))

                # Loop over the metadata associated with entity. For many known entities,
                # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
                # Some entity types may have additional metadata, e.g. ADDRESS entities
                # may have metadata for the address street_name, postal_code, et al.
                for metadata_name, metadata_value in entity.metadata.items():
                    print(u"{}: {}".format(metadata_name, metadata_value))
                    csv.append(metadata_name)
                    csv.append(metadata_value)

                # Loop over the mentions of this entity in the input document.
                # The API currently supports proper noun mentions.
                for mention in entity.mentions:
                    print(u"Mention text: {}".format(mention.text.content))

                    # Get the mention type, e.g. PROPER for proper noun
                    print(
                        u"Mention type: {}".format(language_v1.EntityMention.Type(mention.type_).name)
                    )
                    # csv.append(mention.text.content)
                    # csv.append(language_v1.EntityMention.Type(mention.type_).name)

            # Get the language of the text, which will be the same as
            # the language specified in the request or, if not specified,
            # the automatically-detected language.
            print(u"Language of the text: {}".format(response.language))
        csv_final = csv_final + csv

    return csv_final


if __name__ == "__main__":
    # Initialize variables

    cnl_filename = "out/venca-keywords.xlsx"
    gcnl_keywords = ["camiseta mujer", "tops mujer"]
    gcnl_max_results = 5
    gcnl_max_words = 100
    # gcnl_min_salience = 0.000015

    text_by_url = {}

    text_by_url = retrieve_text_by_url(gcnl_keywords)

    # csv = obtain_nlp_csv(text_by_url)
    # print(csv[:5])


