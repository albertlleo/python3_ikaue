# -*- coding: utf-8 -*-
# (C) 2018 IKAUE, Marketing de Optimizacion
# created by Albert Moral Lleó <albert@ikaue.com>

"""
This module generates a csv with the data extracted from 10 urls html text using Google NLP_ikaue tool.
"""

import os
import sys
import logging
from sys import argv


import pandas as pd
from string import punctuation
from bs4 import BeautifulSoup
from google.cloud import language_v1
from googlesearch import search
from urllib.request import urlopen, Request

#from python3_ikaue.NLP_ikaue.core.config_helper import set_log_file
sys.path.insert(1, "../core/")
from config_helper import set_log_file


def get_urls(keyword, gcnl_max_results):

    """
    This function returns an array of urls that appears on the search applying the keyword
    :param keyword: string concatenated with "+" to perform a bs4 query search
    :param gcnl_max_results: max url to get for each query
    :return: urls in array format
    """

    # to search
    query = keyword

    links = []
    try:
        for j in search(query,  num_results=gcnl_max_results):
            if "elcorteingles" in j.split("."):
                gcnl_max_results-=1
            else:
                links.append(j)
        logging.info('Links appended')

    except Exception as message:
        logging.error(message)
        sys.exit(1)

    return links


def get_html_text(urls):
    """
    This function retrieve only the text from the html given by every url using Beautiful Soup 4.
    :param urls: urls obtained in array format
    :return: A dctionary where the key is the url and the value is all the text for this url.
    """


    # build the Google Cloud Natural Language (GCNL) service object
    results_text = {}
    for url in urls:
        # print the keyword to analyze
        try:
            req = Request(url, headers={
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

            webpage = urlopen(req).read()

            soup = BeautifulSoup(webpage, features="html.parser")


        except Exception as message:
            logging.error(f"Could not retrieve html: {message}")
            sys.exit(1)




        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.decompose()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())

        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

        # drop blank lines
        results_text[url] = '\n'.join(chunk for chunk in chunks if chunk)

    logging.info('html text extracted')
    return results_text


def sample_analyze_entities(text_content, json_key_file_path="../core/google-credentials-analytics.json"):

    """
    This function analyzes Entities in a String
    :param text_content: The text content to analyze
    :param json_key_file_path: Path where credentials are located.
    :return:
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

    try:
        response = client.analyze_entities(request={'document': document, 'encoding_type': encoding_type})
    except Exception as message:
        logging.error(f"Could not retrieve response from Google NLP Client: {message}")
        sys.exit(1)

    return response



def retrieve_text_by_url(gcnl_keywords,gcnl_max_results):

    """
    This function is in charge of retrieve the urls given the words and substracting the text of its html.
    :param gcnl_keywords: Array de palabras/términos que deseamos realizar el análisis
    :param gcnl_max_results: Maximium of urls per search
    :return: A dictionary where the the keys are the queries performed and the values are a dictionary where its key
             are each url searched and the value is the text of its url.
    """

    text_by_url={}
    for keyword in gcnl_keywords:

        print(u">> keyword: '%s'" % keyword)
        keyword = '+'.join(keyword.split())

        # Retrieve 5 top urls
        urls = get_urls(keyword, gcnl_max_results)

        # Dict where keys are each keyword, and inside resides another dict with key as url and value the html text of \
        # its url.
        text_by_url[keyword] = get_html_text(
            urls)

    return text_by_url


def obtain_nlp_csv(text_by_url,cnl_filename,min_salience):
    """
    This function retrieve the NLP analysis and creates a csv with this information.
    :param text_by_url: A dictionary where the the keys are the queries performed and the values are a dictionary where
                        its key are each url searched and the value is the text of its url.
    :return: A csv.
    """

    cols=["keyword","url","EntityName","Language","Salience"]
    csv_final = pd.DataFrame(columns=cols)

    for key in text_by_url.keys():
        for url in text_by_url[key].keys():

            # Only pass 1000 chars to NLP Google function

            response = sample_analyze_entities(text_by_url[key][url][:1000])

            # Loop through entitites returned from the API
            for entity in response.entities:
                if entity.salience < min_salience:
                    pass
                else:
                    #
                    csv_final.loc[len(csv_final)]=[key,url, entity.name, language_v1.Entity.Type(entity.type_).name, entity.salience]

                    #print(u"Representative name for the entity: {}".format(entity.name))

                    # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
                    #print(u"Entity type: {}".format(language_v1.Entity.Type(entity.type_).name))

                    # Get the salience score associated with the entity in the [0, 1.0] range
                    #print(u"Salience score: {}".format(entity.salience))

                    # Loop over the metadata associated with entity. For many known entities,
                    # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
                    # Some entity types may have additional metadata, e.g. ADDRESS entities
                    # may have metadata for the address street_name, postal_code, et al.
                    """for metadata_name, metadata_value in entity.metadata.items():
                        #print(u"{}: {}".format(metadata_name, metadata_value))
                        csv.append(metadata_name)
                        csv.append(metadata_value)"""

                    # Loop over the mentions of this entity in the input document.
                    # The API currently supports proper noun mentions.
                    """for mention in entity.mentions:
                        pass
                        #print(u"Mention text: {}".format(mention.text.content))
    
                        # Get the mention type, e.g. PROPER for proper noun
                        print(
                            u"Mention type: {}".format(language_v1.EntityMention.Type(mention.type_).name)
                        )
                        # csv.append(mention.text.content)
                        # csv.append(language_v1.EntityMention.Type(mention.type_).name)"""

                # Get the language of the text, which will be the same as
                # the language specified in the request or, if not specified,
                # the automatically-detected language.
                #print(u"Language of the text: {}".format(response.language))


    return csv_final.to_csv(cnl_filename,encoding='utf-8')

def retrieve_keywords():
    """
    This module retrieve keywords from input file passed as arg[1]
    :return: keywords
    """
    script, filename = argv

    text_file = open(filename, 'r')
    # gcnl_keywords = [word.strip(punctuation) for line in text_file for word in line.split()]
    gcnl_keywords = [word.strip("\n") for word in text_file if word != ""]

    # Delete last empty element of the array
    # gcnl_keywords.pop()

    return gcnl_keywords

def set_logs(case_directory):
    """
    This function set the logs for this script file.
    :param logs: log file name
    :return:
    """

    if os.path.isdir(case_directory):
        log_file_name = 'log.txt'
        logger = set_log_file(case_directory, log_file_name)
        logger.addHandler(logging.StreamHandler())
    else:
        message = 'Input case directory not existing - Aborting'
        logging.error(message)
        sys.exit(1)

def main():
    # Initialize logs
    set_logs("logs")

    # Set variables up
    cnl_filename = "out/venca-keywords.csv"
    gcnl_max_results = 5
    # gcnl_max_words = 100
    gcnl_min_salience = 0.000015


    # Retrieve keywords from input file
    gcnl_keywords= retrieve_keywords()

    # Start by obtaining
    text_by_url = retrieve_text_by_url(gcnl_keywords, gcnl_max_results)


    obtain_nlp_csv(text_by_url,cnl_filename,gcnl_min_salience)




if __name__ == "__main__":
    main()


