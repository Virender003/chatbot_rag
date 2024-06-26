# -*- coding: utf-8 -*-
"""chat_RAG.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Prl-L1bj4DjtarWHVy0MC7R4aWrdgsef
"""

!pip install python-docx
!pip install PyPDF2

import nltk
import string
import random
from docx import Document
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from google.colab import files

# Download NLTK resources
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

# Initialize Generative AI
genai.configure(api_key='your gemenai api key')
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# Function to upload a file
def upload_file():
    print("Select the type of file you want to upload:")
    print("1. Text file (.txt)")
    print("2. PDF file (.pdf)")
    print("3. Word file (.docx)")
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        print("Please upload your text file:")
        uploaded = files.upload()
        file_name = next(iter(uploaded))
        file_contents = open_file_and_read_contents(file_name)
        return file_contents

    elif choice == '2':
        print("Please upload your PDF file:")
        uploaded = files.upload()
        file_name = next(iter(uploaded))
        file_contents = read_pdf(file_name)
        return file_contents

    elif choice == '3':
        print("Please upload your Word file:")
        uploaded = files.upload()
        file_name = next(iter(uploaded))
        file_contents = read_word_file(file_name)
        return file_contents

    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        return None

# Function to open and read text file
def open_file_and_read_contents(file_name):
    try:
        with open(file_name, 'r') as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        print("File not found or unable to open the file.")
        return None
    except IOError:
        print("An error occurred while reading the file.")
        return None

# Function to read PDF file
def read_pdf(file_name):
    try:
        with open(file_name, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            file_contents = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                file_contents += page.extract_text()
            return file_contents
    except Exception as e:
        print("Error:", e)
        return None

# Function to read Word file
def read_word_file(file_name):
    try:
        doc = Document(file_name)
        file_contents = ''
        for paragraph in doc.paragraphs:
            file_contents += paragraph.text + '\n'
        return file_contents
    except Exception as e:
        print("Error:", e)
        return None

# Preprocess and tokenize file contents
def preprocess_file_contents(file_contents):
    file_contents = file_contents.lower()
    sent_tokens = nltk.sent_tokenize(file_contents)
    word_tokens = nltk.word_tokenize(file_contents)
    return sent_tokens, word_tokens

# Lemmatization and punctuation removal function
def LemNormalize(text):
    lemmer = nltk.stem.WordNetLemmatizer()
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    return [lemmer.lemmatize(token) for token in nltk.word_tokenize(text.lower().translate(remove_punct_dict))]

# Response generation functions
def response(user_response, sent_tokens):
    robo_response = ''
    sent_tokens.append(user_response)

    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)

    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]

    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if req_tfidf == 0:
        robo_response = "I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = sent_tokens[idx]
        return robo_response

# Main conversation loop
flag = True
file_uploaded = False
print("ROBO: My name is VirBot. If you want to exit, type 'Bye!'")

while flag:
    if not file_uploaded:
        user_input = input("ROBO: Do you want to upload a file first? (yes/no): ")
        if user_input.lower() == 'yes':
            file_contents = upload_file()
            if file_contents:
                sent_tokens, word_tokens = preprocess_file_contents(file_contents)
                print("ROBO: File uploaded successfully. You can start the conversation now.")
                file_uploaded = True
        elif user_input.lower() == 'no':
            print("ROBO: Okay, let's start the conversation.")
            file_uploaded = True
        elif user_input.lower() == 'bye':
            print("ROBO: Goodbye!")
            flag = False
            break
        else:
            print("ROBO: Please enter 'yes', 'no', or 'bye'.")

    if file_uploaded:
        user_input = input("You: ")

        # Generate response from the text file
        text_file_response = response(user_input, sent_tokens)
        print("ROBO:", text_file_response)

        # Ask user if they're satisfied with the response
        satisfied = input("ROBO: Are you satisfied with the answer? (yes/no): ")
        if satisfied.lower() == 'yes':
            print("ROBO: Great!")
        elif satisfied.lower() == 'no':
            # Generate response from Gemini AI
            gemini_response = chat.send_message(user_input)
            print("ROBO:", gemini_response.text)
        elif satisfied.lower() == 'bye':
            print("ROBO: Goodbye!")
            flag = False
            break
        else:
            print("ROBO: Please enter 'yes', 'no', or 'bye'.")