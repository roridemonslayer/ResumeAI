import os #this is used to get the file path
import re #this is used for matching patterns in text
import json #this is used for data handling
import spacy #this is for text analysis
import pdfplumber #this is for extracting text from pdf files
from pathlib import Path #this is used to handle file paths
from typing import List, Dict, Tuple, Optional #Python typing is a way to add hints to your code about what types of values variables, function arguments, and return values should have, helping make your code more readable and catch bugs earlier.
from docx import Document #this is used to handle docx files from microsoft word
from datetime import datetime #this is used to handle date and time when the resume was created



class ResumeParser: #this makes a class called resume parser    
    #a class is a blueprint for creating objects, providing initial values for state (member variables) and implementations of behavior (member functions or methods).    
    def __init__(self): #contructor method called when having new resume        
        #initialzie parser with spacy        
        try:         
            self.nlp = spacy.load("en_core_web_sm") #this tries to load a pre-trained spaCy language model called "en_core_web_sm" (the "small English model").         
            print("Spacy works YAYYYYy")            
            #if it works it'll print what I have up there        
        except OSError:         
            print("Spacy doesn't work BOOOO") #this prints that like spacey doenst work         
            self.nlp = None #sets nlp to none so the rest of the program knows its missing
    
    def parse_resume(self, file_path: str, user_id: int = None ) -> Dict: #returns stuff in a dict/hashmap type with a key being assinged to a value the key being the resume        
        #self just refers to the resume instace, file_path is the path to the resume, the user_id is just for user id and if there isn't one it'll say none, and -> dict returns dict with all of resume paseerd info               
        if not Path(file_path).exists():            
            raise FileNotFoundError(f"Resume wasn't found: {file_path}") #this js checks if the resume was in there      
        if not self.nlp:  # FIXED: removed () because nlp is not a function            
            raise Exception("Spacy couldn't be loaded. Resume not parsed")        
        
        file_extension = Path(file_path).suffix.lower() #What this is saying is to get the file extension in lowercase.        
        if file_extension == ".pdf":             
            text = self.extract_the_text_from_pdf(file_path) #prcessing method for pdf          
        elif file_extension in ['.docx','.doc']:             
            text = self.extract_the_text_from_docx(file_path) #processing method for docx         
        else:             
            raise ValueError(f"Unsupported file format: {file_path}") # returns false statement that the file type isn't suppsorted like if it isnt a pdf or a docx it wont procress. 
            
        
        if not text.strip():   #this is basically saying if no white space is found. this is just checking if the string is empty      
            raise ValueError("no text could be found")  #print that no text could be found
        #this is important when Scanned PDFs without OCR (image-only PDFs) corrupted files that opened but contained no text and files with only images/graphics


        #now we're going to parse the extracted text
        parsed_data = self._parse_text(text) #so this line is to set up the parse data like the users name, experience, educaiton etc etc. 
        #it returnse the parse info in a dict form or "hash map form"

        #now we make the meta data. meta data is