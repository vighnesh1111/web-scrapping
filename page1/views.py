from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import pandas as pd
import spacy
from bs4 import BeautifulSoup
import requests
import os

# Create your views here.
def index(request):
    return render(request, 'index.html')

def upload(request):
    if request.method == "POST":
        csv_file = request.FILES['csvfile']
        print(csv_file)
        
        fs = FileSystemStorage()
        filename = fs.save('inputs/'+csv_file.name, csv_file)
        file_url = fs.url(filename)
        
    print(file_url)  
    neww = file_url[1:]
    print(neww)  
    if (os.path.exists(neww)):
        inputFile = neww
        outputFolder = 'output text/'
        outputExcel = 'outputResults.xlsx'

        df = pd.read_excel(inputFile)

        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)

        outputdf = pd.DataFrame(columns=['URL ID', 'Title', 'Article Text', 'Entities', 'Num_Sentences', 'Num_Entities',
                                 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE',
                                 'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX',
                                 'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT',
                                 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'])

    # Load spaCy model for NER
        nlp = spacy.load('en_core_web_sm')

        def articleText(url):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('h1').get_text() if soup.find('h1') else ""

            paragraphs = soup.find_all('p')
            article_text = '\n'.join([p.get_text() for p in paragraphs])

            return title, article_text

    # Function to perform textual analysis and compute variables
        def analyze_text(title, article_text):
            doc = nlp(article_text)
            entities = [ent.text for ent in doc.ents]

            num_sentences = len(list(doc.sents))
            num_entities = len(entities)
            positive_score, negative_score, polarity_score, subjectivity_score = 0, 0, 0, 0
            avg_sentence_length = len(article_text.split()) / num_sentences
            words = article_text.split()
            complex_words = [word for word in words if len(word) > 6]
            percentage_complex_words = (len(complex_words) / len(words)) * 100
            fog_index = 0
            avg_words_per_sentence = len(words) / num_sentences
            complex_word_count = len(complex_words)
            word_count = len(words)
            syllable_per_word = 0
            personal_pronouns = 0
            avg_word_length = sum(len(word) for word in words) / len(words)

            return  entities, num_sentences, num_entities, positive_score, negative_score, \
           polarity_score, subjectivity_score, avg_sentence_length, percentage_complex_words, fog_index, \
           avg_words_per_sentence, complex_word_count, word_count, syllable_per_word, personal_pronouns, avg_word_length

        for index, row in df.iterrows():
            url_id = row['URL_ID']
            url = row['URL']

            title, article_text = articleText(url)
            entities, num_sentences, num_entities, positive_score, negative_score, polarity_score, \
            subjectivity_score, avg_sentence_length, percentage_complex_words, fog_index, \
            avg_words_per_sentence, complex_word_count, word_count, syllable_per_word, \
            personal_pronouns, avg_word_length = analyze_text(title, article_text)

            output_file = os.path.join(outputFolder, f'{url_id}.txt')
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(f'Title: {title}\n\n')
                file.write(article_text)

            outputdf = outputdf._append({'URL ID': url_id, 'Title': title, 'Article Text': article_text, 'Entities': entities,
                                'Num_Sentences': num_sentences, 'Num_Entities': num_entities,
                                'POSITIVE SCORE': positive_score, 'NEGATIVE SCORE': negative_score,
                                'POLARITY SCORE': polarity_score, 'SUBJECTIVITY SCORE': subjectivity_score,
                                'AVG SENTENCE LENGTH': avg_sentence_length,
                                'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words, 'FOG INDEX': fog_index,
                                'AVG NUMBER OF WORDS PER SENTENCE': avg_words_per_sentence,
                                'COMPLEX WORD COUNT': complex_word_count, 'WORD COUNT': word_count,
                                'SYLLABLE PER WORD': syllable_per_word, 'PERSONAL PRONOUNS': personal_pronouns,
                                'AVG WORD LENGTH': avg_word_length}, ignore_index=True)

            print( url_id, title, article_text,  entities, num_sentences, num_entities,
                                positive_score,  negative_score,
                                 polarity_score,  subjectivity_score, avg_sentence_length, percentage_complex_words, 
                                 fog_index, avg_words_per_sentence, complex_word_count, word_count,
                                syllable_per_word,  personal_pronouns,
                                 avg_word_length)

        outputdf.to_excel(outputExcel, index=False)
    return render(request, 'upload.html')