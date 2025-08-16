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

    def _parse_text(self, text: str) -> dict: #so what this is going is just intianlting what we're goign to use to parse the
        doc = self.nlp(text) #what this is doing is taking the text and transform it itno a doc the text from the pdf and converting it into language that is 
        #redable for the spacy model to understand.
        result = { #this is just extracting all the neccasry from the resume like the perosnalfo info the experience
            "personal Info" : {}, 
            "experience" :[], 
            "education" : [], 
            "skills " : [], 
            "certificaitons" : [],
            "awards" : [], 
            "projects" : [], 
            "raw_text" : text #this just keeps the original text if needed.
            
        }

        result['personal_info'] = self._extract_personal_info(text, doc) #this gets info like name, number, email.
        result["experience"] = self._extract_experience(text) #this wil just extract the expeirience from the resume
        result['education'] = self._extract_education(text, doc) #takes the edcuation from the resume and uses  NLP entity recognition to detect school names, degrees, and dates
        result['skills'] = self._extract_skills(text) #takes the skills
        result['certifications'] = self._extract_certifications(text) 
        result['awards'] = self._extract_awards(text)
        result['projects'] = self._extract_projects(text) #just tkaes the raw text

        return result
    #now we;re going to make functions for each part of the text extraction process

    
    def _extract_personal_info(self, text: str, doc) -> dict: 
        #so this us definign the perosnal info metho, it's taking in the raw resume text and the spaCy doc and retruns a dict of the perosnal info. hence the ->
        personal_info = {} 
        #this is just an empty field that'll be filled with the personal info later on 

        emails = re.findall(
            #what re.findall does is that it extracts all subtrings that look like emails
           r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text
        )#as seen above is a email rejex pattern. the \b just makes sure that the match stars cleanrly and ends cleaney
        #rejex tell s python what kinds of text to match in the email or wtv it is ur using
        #the a-z and, the 0-9 and the room for specical characters are all apart of the components for the email. 
        #the @ symbol is for the @ part of the email, think of rejex pattern has characters that contain all of the possible components that could be inside the ressume

        personal_info['email'] = emails[0] if emails else None #it takes the first email if any, but if there isn't then there's none else 

        phone_patterns = [
         r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  #domnestic numbers
         r'\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}' #internatuonak numbers more generic
        ]
        matches = [] #stores are the all the phone numbers
        for pat in phone_patterns: #loops through each phone number 
            for m in re.finditer(pat,text): #re.finditer() finds all matches of the pattern in the text, but instead of returning a list of strings, it returns an iterator of match objects.
                s = m.group(0)
                s = re.sub(r'\D+','',s)
                matches.append(s)

        personal_info['phone'] = matches[0] if matches else None

        names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
        personal_info['names'] = names[0] if names else None

        #this uses spaCy NER tto grab entitites labeled PERSON 

        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORESCASE)
        personal_info['linkedin'] = linkedin_matches[0] if linkedin_matches else None

        #what this is doing is finding the first match of the url no matter where it might be on the resume. it just keeps the oneit found first

        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        personal_info["locations"] = matches[0] if locations else None

        #Remeber that spaCY is a NLP library that can read text and figure out what the role of each word is. 
        #the doc is comign from self.nlp(text) which is spaCy processing the resume
        #doc.ents means that all the named entinties spaCy found like names, dates, ciities etc 
        #GPE stands for geo political entity so country states, coities 
        #loc stans for location so like moutnations rivers etc
        #doc ents is filer that keeps things tat are taged as GPE or LOC
        #it also finds the first locaiton in the doc and saves it was personal_info['loction"]
    
    #extracing experience
    def _extract_experience(self, text: str ) -> str: 
        experience = []
        experience_section = self._extract_section(text, [
            'experience', 'work history', 'employment', 'professional experience'
        ])
        #so the extract_section is basically scanning the document to see if any of these names for expeiernce are present
        #this makes sure it works so even if this ecpeierince section isn't titled expeirnece it'll still perfrom these tasks
        if not experience_section: 
            return experience #this will return an empty string if the name of the expeienrce thing isnt  in the list
        job_blocks = re.split(r'\n(?=\d{4}|\d{1,2}/\d{4}|[A-Z][a-z]+ \d{4})', experience_section)
        #what this does is split the text into chunks where one chunk is assinged to one job based on data patterns that often mark the start of a new job
        # so its saying \d{4} look for 4 digit year loike 2021. d[1,2]/\d{4} look for more/year [A-Z][a-z]+ \d{4} → look for something like "January 2020".
        for block in job_blocks:
            if len(block.strip()) < 20: #skil short blocks
                continue 
        #if a chunk is too short, it'll problen not be a  real job detialed portion so it'll get skipped
            job_info = self._parse_job_block(block) # what this basically does is that it pull the structured detaiols out of the documents
            if job_info: #this is saying if there stuff in the job_info
                experience.append(job_info) #appened it to the expeience block if job_info is found in the text
    #job block parsing
    def _parse_job_block(self, block: str) -> Optional[Dict]: #this is a helper function to take one chunk of text in the job section of the resume and turns it into neat dictionary with structured info
        #the -> Optional[Dict] means that it'll either return a dict if parsing works or none if theres nothign usuaful to work with 

        lines = block.stirp().split('\n') #the strip() remove any extra black space from the start and end of the text/ 
        #the split turns the text into a lsit of lines so you can process each line individually 
        if len(lines) < 2:
            return None
        #this is saying if theres less than 2 lines then  the model will look at it like it's nto a real job and return none 

        job_info ={ #what this does is create an empty temapltes for job details
            #the values will fill as the model parses the data 
            "title" : None, 
            "company" : None, 
            "duration" : None, 
            "description" : [], #both of these are empty lists because there can be multiople bullet points where as the others would js be one liners
            "achievements" : []
        }
        date_pattern = r'b(?:\d{1,2}/\d{4}|\d{4}|[A-Z][a-z]+ \d{4}|\d{1,2}/\d{1,2}/\d{4})\b'
        #this date_pattern is looking for data formats like 05/2020,2022, 00/02/2023 or like jan, 2018 just any way taht the user might write the data 







    








