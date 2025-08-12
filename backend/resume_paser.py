import os #this is used to get the file path
import re #this is used for matching patterns in text
import json #this is used for data handling
import spacy #this is for text analysis
import pdfplumber #this is for extracting text from pdf files
import fitz # PyMuPDF, used for extracting text from PDF files as a fallback
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
            self.nlp = None #sets nlp to none so the rest of the program knows its missing. 
            #basically sayign the nlp can't process the human language to interperet. 
    
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

        #now we make the meta data. meta data just contained info on what the parse just processed. 

        #the meta data is It provides essential information about the parsing process itself, file characteristics, and processing statistics that are crucial for debugging, analytics, and database management so keep this in mind for next time your working with meta data. 
        parsed_data['metadata'] = { #what this does is create. a metadata fucntion in the dict parrsated data. 
            'file_path':file_path, #this is just the origial resume file tied to the metadata
            'file_name' :Path(file_path).name, #what this does is convert a file like Path("/uploads/resumes/john_doe.pdf").name to john_doe.pdf/ it just outpiut the file name in a simple way.
            'file_size' : os.get.getsize(file_path), #this is how much space the file takes up on the disk. the disk of the computer ex. 202020 would be like 2.0 gb
            "parsed_at" : datetime.utcnow().isoformat(), #what this does is just display the time in which the resume was parsed
            #isoformay converts into "2024-01-15T14:30:25.123456" this format when displaying the time and day it was created. 
            'user_id' : user_id, #this just tracks the users id. each user is assigned an id 
            "text_length" :len(text), #this just tracks like the lenghts of the text in the file. for example if a file has like 210010 text include puncation, letters spaces etc 
            "word_count" :len(text.split())  #this just only tracks the word count not including yk white space, just the words

        }
        return parsed_data
    def _extracting_from_pdf(self, pdf_path: str) -> str: #what this is, we're making a function for extracting the data from the pdf, it'll return everything in string format.
    #the pdf_path is the file path to the pdf and then it'll return it as a string

        text = "" #this an empty string because this is wehre the accumilated extracted text will go 
        try: # try is just like syaing "this might be risky code, try it"
            with pdfplumber.open(pdf_path) as pdf: # so what this is doing is that its opening the file for u, thats why u use with. with with
                #it opens the file and then when ur done with it, it complatetley clsoes this block out even if there;s an error in the middle 
                #so that line is just opening the file
                 #it makes the the pdf is cloed properaly even if there is an error
                for page in pdf.pages:  #this is going to be looping through each page in the pdf the pdf.pages is a list of all the pages in the pdf 
                    page_text = page.extract_text() #this is a method from pdf plumber. and it just tried to pull text form the pdf 
                    if page_text: 
                        text += page_text + "\n" # this one add the current page's text to the overall text, followed by a newline for separation
            if text.strip(): #this just again removes extra whtie space from the end and beginnign of the new text
                print("Text Extracted from PDF Plumber")
                return text #send the full extreacted text of the document when this function is called. 
        except Exception as e: #this will run if any error is found int he try function 
            #exception is a function in pythin that catches errors in ur code
            #e just stores the error onbject in e 
            print(f"PDFPlumber failed gang: {e}") #the e will get repalce with the error message 
        #this is just a fall back if pdfplumber doesn't work. 
        try: #again the try method its like js try this even if errors come up
            doc = fitz.open(pdf_path) #this opens the pdf using the  PyMuPDF
            #Returns a Document object stored in the variable doc. #Unlike the with statement, this does not auto-close — we’ll have to call .close() manually later.
            for page in doc: #loops throguh each page in the doc, 
                text += page.get_text() #Adds (+=) that text to the text variable we’ve been building.
            doc.close() #this just manually closes the loop becuase we didn't have a with statement.
            if text.strip():
                print("Text Extracted from PDF")
                return text #returns the extracted text. 
        except Exception as e:  # just raises the error that it failed.
            print(f"PyMuPDF failed: {e}")
    
    
    def _extracting_from_docx(self, dock_path: str) -> str: #so this is how we're going to extract the info from docx
        try: 
            doc = Document(dock_path) 
            text = "" #this is the empty space to store the text extracted
            for paragraphs in doc.paragraphs(): # loops through the paragraphs  in the word doc 
                text += paragraphs.text + "\n" # add the text to the paragrph varible to be used later
                print("text extracted from docx")
                return text
        except Exception as e:
            print(f"text extraction from DOCx: {e}") 

    def _parse_text(self, text: str) -> dict #so what this is going is just intianlting what we're goign to use to parse the text.
        doc = self.nlp(text) #what htis is doign is taking the text and transform it itno a doc the text from the pdf and converting it into language that is 
        #redable for the spacy model to understand.
        result = {
            "personal Info" : {}, 
            "experience" :[], 
            "education" : [], 
            "skills " : [], 
            "certificaitons" : [],
            "awards" : [], 
            "projects" : [], 
            "raw_text" : text
        }


 


    








