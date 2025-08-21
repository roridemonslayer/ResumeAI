# These are import statements - they bring in external libraries/modules that we need
# Think of them like tools from a toolbox that we're borrowing to use in our code

import os #this is used to get the file path
import re #this is used for matching patterns in text
import json #this is used for data handling
import pdfplumber #this is for extracting text from pdf files
import fitz # PyMuPDF, used for extracting text from PDF files as a fallback
from pathlib import Path #this is used to handle file paths
from typing import List, Dict, Tuple, Optional #Python typing is a way to add hints to your code about what types of values variables, function arguments, and return values should have, helping make your code more readable and catch bugs earlier.
from docx import Document #this is used to handle docx files from microsoft word
from datetime import datetime #this is used to handle date and time when the resume was created

# Try to import spacy, but make it optional
# This is a try/except block - it tries to do something risky, and if it fails, it has a backup plan
try:
    import spacy #this is for text analysis
    SPACY_AVAILABLE = True  # This is a flag variable - like a boolean switch that remembers if spacy worked
except ImportError:  # ImportError happens when Python can't find the library to import
    SPACY_AVAILABLE = False  # Set our flag to False so the rest of the program knows spacy isn't available
    print("spaCy not installed. Some features will be limited.")

class ResumeParser: #this makes a class called resume parser    
    #a class is a blueprint for creating objects, providing initial values for state (member variables) and implementations of behavior (member functions or methods).    
    
    def __init__(self): #constructor method called when having new resume        
        #initialize parser with spacy        
        # __init__ is a special method called automatically when you create a new instance of the class
        # It's like the setup instructions that run every time you build something from this blueprint
        
        self.nlp = None  # Initialize nlp as None (empty) - this will hold our language processing tool
        
        # Check if spaCy is available before trying to use it
        if SPACY_AVAILABLE:
            try:         
                self.nlp = spacy.load("en_core_web_sm") #this tries to load a pre-trained spaCy language model called "en_core_web_sm" (the "small English model").         
                print("✅ Spacy works YAYYYYy")            
                #if it works it'll print what I have up there        
            except OSError:  # OSError happens when the system can't find or access something
                print("⚠️ Spacy doesn't work BOOOO") #this prints that like spacey doesn't work         
                self.nlp = None #sets nlp to none so the rest of the program knows its missing. 
                #basically saying the nlp can't process the human language to interpret. 
        else:
            # This runs if SPACY_AVAILABLE is False (meaning the import failed earlier)
            print("⚠️ spaCy not available. Install it with: pip install spacy")
    
    def parse_resume(self, file_path: str, user_id: int = None ) -> Dict: #returns stuff in a dict/hashmap type with a key being assigned to a value the key being the resume        
        #self just refers to the resume instance, file_path is the path to the resume, the user_id is just for user id and if there isn't one it'll say none, and -> dict returns dict with all of resume parsed info               
        
        # First, check if the file actually exists on the computer
        if not Path(file_path).exists():            
            raise FileNotFoundError(f"Resume wasn't found: {file_path}") #this js checks if the resume was in there      
            # raise is like throwing an error - it stops the program and shows an error message
        
        # Get the file extension (like .pdf, .docx) to know what type of file we're dealing with
        file_extension = Path(file_path).suffix.lower() #What this is saying is to get the file extension in lowercase.        
        
        # Based on the file type, use the appropriate method to extract text
        if file_extension == ".pdf":             
            text = self._extracting_from_pdf(file_path) #processing method for pdf          
        elif file_extension in ['.docx','.doc']:  # Check if it's a Word document
            text = self._extracting_from_docx(file_path) #processing method for docx         
        else:             
            raise ValueError(f"Unsupported file format: {file_path}") # returns false statement that the file type isn't supported like if it isn't a pdf or a docx it won't process. 
            
        # Check if we actually got any text from the file
        if not text.strip():   #this is basically saying if no white space is found. this is just checking if the string is empty      
            raise ValueError("no text could be found")  #print that no text could be found
        #this is important when Scanned PDFs without OCR (image-only PDFs) corrupted files that opened but contained no text and files with only images/graphics

        #now we're going to parse the extracted text
        parsed_data = self._parse_text(text) #so this line is to set up the parse data like the users name, experience, education etc etc. 
        #it returns the parse info in a dict form or "hash map form"

        #now we make the meta data. meta data just contained info on what the parse just processed. 
        #the meta data is It provides essential information about the parsing process itself, file characteristics, and processing statistics that are crucial for debugging, analytics, and database management so keep this in mind for next time your working with meta data. 
        parsed_data['metadata'] = { #what this does is create a metadata function in the dict parsed data. 
            # Adding a new key called 'metadata' to our parsed_data dictionary
            'file_path':file_path, #this is just the original resume file tied to the metadata
            'file_name' :Path(file_path).name, #what this does is convert a file like Path("/uploads/resumes/john_doe.pdf").name to john_doe.pdf/ it just output the file name in a simple way.
            'file_size' : os.path.getsize(file_path), #this is how much space the file takes up on the disk. the disk of the computer ex. 202020 would be like 2.0 gb
            "parsed_at" : datetime.utcnow().isoformat(), #what this does is just display the time in which the resume was parsed
            #isoformat converts into "2024-01-15T14:30:25.123456" this format when displaying the time and day it was created. 
            'user_id' : user_id, #this just tracks the users id. each user is assigned an id 
            "text_length" :len(text), #this just tracks like the lengths of the text in the file. for example if a file has like 210010 text include punctuation, letters spaces etc 
            "word_count" :len(text.split())  #this just only tracks the word count not including yk white space, just the words
            # .split() breaks text into a list of words, len() counts how many items are in that list
        }
        return parsed_data  # Send back all the parsed information as a dictionary
    
    def _extracting_from_pdf(self, pdf_path: str) -> str: #what this is, we're making a function for extracting the data from the pdf, it'll return everything in string format.
        #the pdf_path is the file path to the pdf and then it'll return it as a string
        # The underscore _ at the start means this is a "private" method - only used inside this class
        
        text = "" #this an empty string because this is where the accumulated extracted text will go 
        
        # Try PDFPlumber first (this is our preferred method)
        try: # try is just like saying "this might be risky code, try it"
            with pdfplumber.open(pdf_path) as pdf: # so what this is doing is that its opening the file for u, thats why u use with. with with
                #it opens the file and then when ur done with it, it completely closes this block out even if there's an error in the middle 
                #so that line is just opening the file
                 #it makes the the pdf is closed properly even if there is an error
                 
                # Loop through each page in the PDF
                for page in pdf.pages:  #this is going to be looping through each page in the pdf the pdf.pages is a list of all the pages in the pdf 
                    page_text = page.extract_text() #this is a method from pdf plumber. and it just tried to pull text form the pdf 
                    if page_text:  # Only add text if we actually found some (not empty)
                        text += page_text + "\n" # this one add the current page's text to the overall text, followed by a newline for separation
                        # += means "add to the existing value" - it's the same as: text = text + page_text + "\n"
                        
            if text.strip(): #this just again removes extra white space from the end and beginning of the new text
                print("📄 Text Extracted from PDF Plumber")
                return text #send the full extracted text of the document when this function is called. 
        except Exception as e: #this will run if any error is found int he try function 
            #exception is a function in python that catches errors in ur code
            #e just stores the error object in e 
            print(f"PDFPlumber failed gang: {e}") #the e will get replace with the error message 
            # f"..." is an f-string - it lets you put variables directly in strings using {variable_name}
            
        #this is just a fall back if pdfplumber doesn't work. 
        # Second attempt: Try PyMuPDF (fitz) as backup
        try: #again the try method its like js try this even if errors come up
            doc = fitz.open(pdf_path) #this opens the pdf using the  PyMuPDF
            #Returns a Document object stored in the variable doc. #Unlike the with statement, this does not auto-close — we'll have to call .close() manually later.
            for page in doc: #loops through each page in the doc, 
                text += page.get_text() #Adds (+=) that text to the text variable we've been building.
            doc.close() #this just manually closes the loop because we didn't have a with statement.
            # We MUST call .close() because fitz doesn't automatically close like pdfplumber does
            if text.strip():  # Check if we got any actual text (not just whitespace)
                print("📄 Text Extracted from PyMuPDF")
                return text #returns the extracted text. 
        except Exception as e:  # just raises the error that it failed.
            print(f"PyMuPDF failed: {e}")
        
        # If we get here, both methods failed, so return whatever text we have (might be empty)
        return text
    
    def _extracting_from_docx(self, docx_path: str) -> str: #so this is how we're going to extract the info from docx
        # This method handles Microsoft Word documents (.docx files)
        try: 
            doc = Document(docx_path)  # Create a Document object from the Word file
            text = "" #this is the empty space to store the text extracted
            
            # Loop through every paragraph in the Word document
            for paragraph in doc.paragraphs: # loops through the paragraphs in the word doc (FIXED: removed () because paragraphs is a property not method)
                text += paragraph.text + "\n" # add the text to the paragraph variable to be used later
                # Get the text from this paragraph and add it to our total text, plus a newline
            print("📄 text extracted from docx")
            return text  # Return all the text we found
        except Exception as e:  # If anything goes wrong while reading the Word document
            print(f"text extraction from DOCX: {e}") 
            return ""  # Return an empty string if extraction failed

    def _parse_text(self, text: str) -> dict: #so what this is going is just initializing what we're going to use to parse the
        # This is the main parsing method that takes raw text and organizes it into categories
        
        # If spaCy is available, process the text with it for better analysis
        doc = self.nlp(text) if self.nlp else None #what this is doing is taking the text and transform it into a doc the text from the pdf and converting it into language that is 
        #readable for the spacy model to understand.
        # This creates a spaCy document object that understands grammar, entities, etc.
        
        # Create the main structure to hold all our parsed information
        result = { #this is just extracting all the necessary from the resume like the personal info the experience
            "personal_info" : {},  # Will hold name, email, phone, etc.
            "experience" :[], # Will hold job history as a list of dictionaries
            "education" : [], # Will hold degrees and schools
            "skills" : [], # Will hold technical skills
            "certifications" : [], # Will hold professional certifications
            "awards" : [], # Will hold awards and recognition
            "projects" : [], # Will hold personal/work projects
            "raw_text" : text #this just keeps the original text if needed.
        }

        # Now fill in each section by calling specific extraction methods
        result['personal_info'] = self._extract_personal_info(text, doc) #this gets info like name, number, email.
        result["experience"] = self._extract_experience(text) #this will just extract the experience from the resume
        result['education'] = self._extract_education(text, doc) #takes the education from the resume and uses  NLP entity recognition to detect school names, degrees, and dates
        result['skills'] = self._extract_skills(text) #takes the skills
        result['certifications'] = self._extract_certifications(text) 
        result['awards'] = self._extract_awards(text)
        result['projects'] = self._extract_projects(text) #just takes the raw text

        return result  # Return the complete organized resume data
    
    #now we're going to make functions for each part of the text extraction process
    
    def _extract_personal_info(self, text: str, doc) -> dict: 
        #so this us defining the personal info method, it's taking in the raw resume text and the spaCy doc and returns a dict of the personal info. hence the ->
        personal_info = {} 
        #this is just an empty field that'll be filled with the personal info later on 

        # Extract email addresses using regular expressions (regex)
        emails = re.findall(
            #what re.findall does is that it extracts all substrings that look like emails
           r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text
        )#as seen above is a email regex pattern. the \b just makes sure that the match starts clearly and ends cleanly
        #regex tells python what kinds of text to match in the email or wtv it is ur using
        #the a-z and, the 0-9 and the room for special characters are all apart of the components for the email. 
        #the @ symbol is for the @ part of the email, think of regex pattern has characters that contain all of the possible components that could be inside the resume
        # Let's break down this regex pattern:
        # \b = word boundary (start/end of word)
        # [A-Za-z0-9._%+-]+ = one or more letters, numbers, or email-safe symbols
        # @ = the @ symbol (literal)
        # [A-Za-z0-9.-]+ = one or more letters, numbers, dots, or dashes (for domain)
        # \. = a literal dot (escaped because . has special meaning in regex)
        # [A-Z|a-z]{2,} = at least 2 letters for the domain extension (.com, .org, etc.)

        personal_info['email'] = emails[0] if emails else None #it takes the first email if any, but if there isn't then there's none else 
        # This uses a ternary operator: if emails list has items, take the first one, otherwise use None

        # Extract phone numbers using multiple patterns to catch different formats
        phone_patterns = [
         r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  #domestic numbers
         r'\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}' #international numbers more generic
        ]
        # These patterns look for:
        # Pattern 1: US phone numbers like (123) 456-7890, 123-456-7890, +1 123 456 7890
        # Pattern 2: International numbers with country codes
        
        matches = [] #stores are the all the phone numbers
        for pattern in phone_patterns: #loops through each phone number pattern
            for match in re.finditer(pattern, text): #re.finditer() finds all matches of the pattern in the text, but instead of returning a list of strings, it returns an iterator of match objects.
                # finditer is like findall, but gives us more detailed match objects
                phone = match.group(0)  # Get the full matched text
                phone = re.sub(r'\D+','',phone) #Remove non-digits
                # \D means "any non-digit character", so this removes everything except 0-9
                matches.append(phone)  # Add the cleaned phone number to our list

        personal_info['phone'] = matches[0] if matches else None  # Take first phone number found

        # Extract names (using spaCy if available)
        if doc:  # If we have spaCy processing available
            # Look for entities that spaCy identified as person names
            names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
            # doc.ents = all named entities spaCy found (people, places, organizations, etc.)
            # ent.label_ == "PERSON" filters to only keep person names
            # .text.strip() gets the actual text and removes extra whitespace
            personal_info['name'] = names[0] if names else None  # Use first name found
        else:
            # Simple name extraction without spaCy - look in first few lines for likely names
            lines = text.split('\n')[:5]  # Check first 5 lines only
            # Resumes usually have the name at the top, so we don't need to check the whole document
            for line in lines:  # Go through each of the first 5 lines
                line = line.strip()  # Remove whitespace from start/end
                # Check if this line looks like a name:
                # - Has exactly 2 words (first name, last name)
                # - Contains only letters and spaces
                if len(line.split()) == 2 and line.replace(' ', '').isalpha():
                    personal_info['name'] = line  # This looks like a name!
                    break  # Stop looking once we find one
            else:
                # This 'else' belongs to the 'for' loop, not the 'if'
                # It runs if the loop completes without hitting 'break'
                personal_info['name'] = None  # Didn't find a name

        #this uses spaCy NER to grab entities labeled PERSON 

        # Extract LinkedIn profile URLs
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        # This pattern looks for LinkedIn URLs in various formats:
        # - With or without http:// or https://
        # - With or without www.
        # - Followed by linkedin.com/in/ and then username characters
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        # re.IGNORECASE makes the search case-insensitive (matches LinkedIn, linkedin, LINKEDIN, etc.)
        personal_info['linkedin'] = linkedin_matches[0] if linkedin_matches else None

        #what this is doing is finding the first match of the url no matter where it might be on the resume. it just keeps the one it found first

        # Extract location (using spaCy if available)
        if doc:  # If spaCy is available
            # Look for geographic entities
            locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
            personal_info['location'] = locations[0] if locations else None
        else:
            personal_info['location'] = None  # Can't extract location without spaCy

        #Remember that spaCy is a NLP library that can read text and figure out what the role of each word is. 
        #the doc is coming from self.nlp(text) which is spaCy processing the resume
        #doc.ents means that all the named entities spaCy found like names, dates, cities etc 
        #GPE stands for geo political entity so country states, cities 
        #loc stands for location so like mountains rivers etc
        #doc ents is filter that keeps things that are tagged as GPE or LOC
        #it also finds the first location in the doc and saves it was personal_info['location"]
        
        return personal_info  # Return dictionary with all personal information found
    
    #extracting experience - ENHANCED VERSION
    def _extract_experience(self, text: str) -> List[Dict]:
        # This method extracts work experience and returns it as a list of job dictionaries
    
        experience = []  # This will hold all the jobs we find
        
        # Find experience section in the resume
        exp_section = self._extract_section(text, ['experience', 'work history', 'employment'])
        # Look for section headers like "Experience", "Work History", etc.
        if not exp_section:  # If we didn't find an experience section
            return []  # Return empty list - no experience found
        
        # Split the experience section into individual lines and remove empty ones
        lines = [line.strip() for line in exp_section.split('\n') if line.strip()]
        # .strip() removes whitespace, the if condition keeps only non-empty lines
        
        # Initialize variables to track what we're currently processing
        current_job = {}  # Will hold information about the current job we're parsing
        collecting_descriptions = False  # Flag to know if we're reading job description lines
        
        # Process each line in the experience section
        for line in lines:
            # Skip the main "Experience" header line
            if line.lower() in ['experience', 'work experience', 'professional experience']:
                continue  # Skip this line and go to the next one
            
            # Check if line contains a date (likely indicates a new job entry)
            if re.search(r'\b(19|20)\d{2}\b', line):
                # This regex looks for years like 1999, 2000, 2024, etc.
                # \b = word boundary, (19|20) = starts with 19 or 20, \d{2} = followed by 2 digits
                
                # Save previous job if it exists and has a title
                if current_job.get('title'):  # .get() safely checks if 'title' key exists
                    experience.append(current_job.copy())  # .copy() creates a separate copy
                
                # Start tracking a new job
                current_job = {
                    'title': 'Unknown',  # Default values in case we can't find them
                    'company': 'Unknown',
                    'duration': 'Unknown',
                    'description': []  # List to hold job responsibilities/achievements
                }
                
                # Try to extract title and date from this line
                # Look for date patterns like "Jan 2020", "March 2019 - Present", etc.
                date_match = re.search(r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{4}(?:\s*[-–—]\s*(?:Present|Current|\w+\.?\s+\d{4}))?)', line, re.IGNORECASE)
                if date_match:  # If we found a date pattern
                    current_job['duration'] = date_match.group(1)  # Save the date range
                    # Extract the part before the date as potential job title
                    title_part = line[:date_match.start()].strip()
                    if title_part:  # If there's text before the date
                        current_job['title'] = title_part
                
                collecting_descriptions = False  # Reset flag for new job
                
            # If we have a current job and this looks like a company line
            elif (current_job.get('title') and current_job.get('company') == 'Unknown' and
                not line.startswith(('•', '-', '*')) and len(line) < 100):
                # Conditions: we have a job title, no company yet, line doesn't look like bullet point, reasonable length
                current_job['company'] = line
                collecting_descriptions = True  # Start looking for job descriptions next
                
            # If this looks like a job description bullet point
            elif (current_job.get('title') and 
                (line.startswith(('•', '-', '*')) or collecting_descriptions)):
                # Remove bullet point symbols and extra whitespace
                desc = line.lstrip('•-* ').strip()
                if desc and len(desc) > 10:  # Only keep meaningful descriptions (longer than 10 chars)
                    current_job['description'].append(desc)
                collecting_descriptions = True  # Keep collecting descriptions
        
        # Don't forget the last job (loop ends but we might have one more job to save)
        if current_job.get('title'):
            experience.append(current_job)
        
        return experience  # Return list of all jobs found
    
    def _split_into_job_blocks(self, text: str) -> List[str]:
        """Split experience section into individual job blocks - IMPROVED VERSION"""
        # This method takes an experience section and tries to split it into separate job entries
        
        # Clean up the text and split into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # Only keep lines that have actual content (not just whitespace)
        
        job_blocks = []  # Will store separate job entries as text blocks
        current_block = []  # Accumulates lines for the current job being processed
        
        print(f"🔍 Processing {len(lines)} lines for job splitting")
        
        # Print all lines for debugging purposes
        print("📝 All lines in experience section:")
        for i, line in enumerate(lines):
            print(f"   {i:2d}: '{line}'")  # Print line number and content
        
        # Look for job title patterns that indicate a new job entry
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip the main "Experience" header
            if line_stripped.lower() in ['experience', 'work experience', 'professional experience']:
                print(f"⏭️ Skipping main header: {line_stripped}")
                continue  # Don't include section headers in job blocks
            
            # Check if this line looks like a job title using regex patterns
            job_title_patterns = [
                r'^[^•\d].*[A-Za-z].*$',  # Doesn't start with bullet or number, contains letters
                r'.*Intern.*',  # Contains the word "Intern"
                r'.*Fellow.*',  # Contains the word "Fellow" 
                r'.*Instructor.*',  # Contains the word "Instructor"
                r'.*Engineer.*',  # Contains the word "Engineer"
            ]
            
            # Test if the line matches any job title pattern
            is_job_title = any(re.search(pattern, line_stripped, re.IGNORECASE) for pattern in job_title_patterns)
            # any() returns True if at least one pattern matches
            
            # Also check if the next line might contain a date range
            has_date_next = False
            if i + 1 < len(lines):  # Make sure there is a next line
                next_line = lines[i + 1].strip()
                # Look for date patterns like "Jan 2020 - Dec 2021"
                date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[–—-]\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})'
                has_date_next = re.search(date_pattern, next_line, re.IGNORECASE) is not None
            
            # If this looks like a job title and we have a current block, save the current block
            if (is_job_title or has_date_next) and current_block:
                block_content = '\n'.join(current_block)  # Combine all lines in current block
                if len(block_content.strip()) > 20:  # Only save blocks with reasonable content
                    job_blocks.append(block_content)
                    print(f"💼 Saved job block: {current_block[0][:50]}...")  # Print first 50 chars
                
                # Start new job block
                current_block = [line_stripped]
                print(f"🆕 Starting new job block with: {line_stripped}")
            else:
                # Add line to current job block
                current_block.append(line_stripped)
                print(f"   ➕ Added to current block: {line_stripped}")
        
        # Don't forget the last block when the loop ends
        if current_block:
            block_content = '\n'.join(current_block)
            if len(block_content.strip()) > 20:  # Only save if it has reasonable content
                job_blocks.append(block_content)
                print(f"💼 Saved final job block: {current_block[0][:50]}...")
        
        print(f"📦 Total job blocks created: {len(job_blocks)}")
        
        # Show what blocks were created (for debugging)
        for i, block in enumerate(job_blocks):
            print(f"\n--- Job Block {i+1} ---")
            # Show first 200 characters of each block
            print(block[:200] + ("..." if len(block) > 200 else ""))
            print("--- End Block ---\n")
        
        return job_blocks  # Return list of job block strings
    
    def _parse_job_block(self, block: str) -> Optional[Dict]:
        """Parse individual job block into structured data - IMPROVED VERSION"""
        # This method takes a text block for one job and extracts structured information
        
        try:
            # Split block into lines and remove empty ones
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:  # If no lines left after cleaning
                return None  # Nothing to parse
            
            # Create structure to hold job information
            job_info = {
                "title": None,       # Job title
                "company": None,     # Company name
                "location": None,    # Work location
                "duration": None,    # Date range
                "description": []    # List of job responsibilities
            }

            print(f"🔍 Parsing job block with {len(lines)} lines:")
            for i, line in enumerate(lines):
                print(f"   Line {i}: '{line}'")  # Debug: show each line

            # Step 1: Find title (usually first line)
            if lines:
                job_info['title'] = lines[0]  # Assume first line is the job title
                print(f"✅ Title: '{job_info['title']}'")

            # Step 2: Find duration and company (could be in various positions)
            for i, line in enumerate(lines):
                # Look for date patterns in each line
                date_match = re.search(r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[–—-]\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}))', line, re.IGNORECASE)
                if date_match and not job_info['duration']:  # If we found a date and don't have one yet
                    job_info['duration'] = date_match.group(1)  # Save the date range
                    print(f"✅ Duration: '{job_info['duration']}'")
                
                # Look for company name (usually contains organization keywords)
                if not job_info['company'] and ('Remote' in line or any(org in line for org in ['School', 'University', 'Foundation', 'AI', 'Coding'])):
                    job_info['company'] = line  # This line likely contains company info
                    print(f"✅ Company: '{job_info['company']}'")
                    
                    # Check if location is specified in the same line
                    if 'Remote' in line:
                        job_info['location'] = 'Remote'
                        print(f"✅ Location: '{job_info['location']}'")

            # Step 3: Extract descriptions (bullet points)
            description_lines = []
            for line in lines:
                # Look for bullet points (they usually start with special characters)
                if re.match(r'^[•\-*]\s', line):
                    description_lines.append(line)  # This is a job responsibility
            
            # Clean up the descriptions by removing bullet point symbols
            job_info['description'] = [re.sub(r'^[•\-*]\s*', '', desc).strip() for desc in description_lines]
            # re.sub() replaces the bullet point symbols with empty string, .strip() removes extra whitespace
            print(f"✅ Descriptions: {len(job_info['description'])} found")

            # Return job if we have essential info (at least a title)
            if job_info.get('title'):
                print(f"🎉 Successfully parsed job:")
                print(f"   Title: {job_info['title']}")
                print(f"   Company: {job_info['company']}")
                print(f"   Location: {job_info['location']}")
                print(f"   Duration: {job_info['duration']}")
                print(f"   Descriptions: {len(job_info['description'])}")
                return job_info  # Return the structured job information
            else:
                print("❌ No title found, skipping job")
                return None  # Can't create a job entry without a title

        except Exception as e:  # If anything goes wrong during parsing
            print(f"❌ Error in _parse_job_block: {e}")
            import traceback
            traceback.print_exc()  # Print detailed error information for debugging
            return None

    def _extract_education(self, text: str, doc) -> List[Dict]:
        """Extract education with duplicate prevention"""
        # This method finds educational background information and organizes it
        
        education = []  # Will store list of education entries
        
        # First, try to find a dedicated education section
        education_section = self._extract_section(
            text, 
            ['education', 'academic background', 'qualifications', 'academic', 'schooling']
        )

        if not education_section:
            print("⚠️ No education section found, searching entire text...")
            education_section = text  # Use entire resume text as fallback
        
        # Extract organizations using spaCy if available (for school names)
        organizations = []
        if doc:  # If spaCy is available
            # Find entities that spaCy identified as organizations
            organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            # ORG = organization entities (companies, schools, etc.)

        # Enhanced degree patterns to catch various degree formats
        degree_patterns = [
            # Full degree names like "Bachelor of Science in Computer Science"
            r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Diploma|Certificate)(?:\s+of\s+(?:Science|Arts|Engineering|Business|Law|Medicine))?\b[^.\n]*',
            # Abbreviated degrees like "BS", "MS", "MBA"
            r'\b(?:BS|BA|MS|MA|MBA|PhD|BSc|MSc|MD|JD|LLM|BFA|MFA)\b[^.\n]*',
            # Degrees with periods like "B.S.", "M.A."
            r'\b(?:B\.S\.|B\.A\.|M\.S\.|M\.A\.|Ph\.D\.|M\.B\.A\.)\b[^.\n]*',
            # High school education
            r'\b(?:High School Diploma|GED)\b[^.\n]*'
        ]

        degrees = []  # Will store all degrees found
        # Search for each pattern in the education section
        for pattern in degree_patterns:
            found_degrees = re.findall(pattern, education_section, re.IGNORECASE)
            degrees.extend(found_degrees)  # Add all found degrees to our list
            # extend() adds each item individually, unlike append() which adds the whole list

        # Look for GPA information
        gpa_pattern = r'GPA:?\s*(\d+\.?\d*(?:/\d+\.?\d*)?|\d+\.?\d*)'
        # This pattern looks for:
        # - "GPA:" or "GPA" followed by optional space
        # - Numbers like "3.5", "3.75", "3.5/4.0"
        gpa_matches = re.findall(gpa_pattern, education_section, re.IGNORECASE)
        
        # Remove duplicates while preserving order
        seen_degrees = set()  # Set to track what we've already seen
        unique_degrees = []   # List to store unique degrees
        for degree in degrees:
            degree_clean = degree.strip().lower()  # Clean and standardize for comparison
            # Only add if we haven't seen this degree before and it's reasonable length
            if degree_clean not in seen_degrees and len(degree_clean) > 5:
                seen_degrees.add(degree_clean)  # Remember we've seen this
                unique_degrees.append(degree.strip())  # Add original (not lowercased) to results
        
        # Create education entries by combining degrees with organizations
        for i, degree in enumerate(unique_degrees):
            edu_info = {
                'degree': degree,
                # Try to match with organization, or use default if none found
                'institution': organizations[i] if i < len(organizations) else "Institution not found",
                "year": None,      # Will try to extract year
                "gpa": None        # Will try to extract GPA
            }
            
            # Extract year from the degree line or nearby text
            year_match = re.search(r'\b(19|20)\d{2}\b', degree)
            # Look for 4-digit years starting with 19 or 20 (1900s or 2000s)
            if year_match:
                edu_info['year'] = year_match.group()  # Save the year
            
            # Extract GPA if found and matches this education entry
            if gpa_matches and i < len(gpa_matches):
                edu_info['gpa'] = gpa_matches[i]
            
            education.append(edu_info)  # Add this education entry
        
        # Remove duplicate entries based on degree and institution combination
        final_education = []
        seen_combos = set()  # Track combinations we've seen
        for edu in education:
            # Create a unique identifier combining degree and institution
            combo = f"{edu['degree']}-{edu['institution']}".lower()
            if combo not in seen_combos:
                seen_combos.add(combo)  # Remember this combination
                final_education.append(edu)  # Add to final results
        
        return final_education  # Return list of unique education entries

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume"""
        # This method finds and extracts technical skills
   
        # First try to find a dedicated skills section
        skills_section = self._extract_section(text, ['skills', 'technical skills', 'competencies'])
        
        if skills_section:
            # Remove the header line (like "Skills:" or "Technical Skills:")
            lines = skills_section.split('\n')
            content = '\n'.join(lines[1:]) if len(lines) > 1 else skills_section
            # If multiple lines, skip first (header), otherwise use whole section
            
            # Replace common separators with commas for easier parsing
            content = re.sub(r'[•·▪▫◦‣⁃]', ',', content)  # Replace bullet points with commas
            content = re.sub(r'[\n\r\|;]', ',', content)   # Replace newlines, pipes, semicolons with commas
            content = re.sub(r'\s*,\s*', ',', content)     # Clean up spacing around commas
            
            # Extract individual skills by splitting on commas
            potential_skills = [s.strip() for s in content.split(',') if s.strip()]
            # Split by comma, remove whitespace, keep only non-empty items
            
            # Filter valid skills based on length and content
            skills = []
            for skill in potential_skills:
                # Keep skills that are reasonable length and not common words
                if (2 <= len(skill) <= 50 and  # Between 2 and 50 characters
                    not skill.lower() in ['skills', 'technical', 'and', 'or', 'with'] and  # Not header words
                    skill not in skills):  # Not already in our list (avoid duplicates)
                    skills.append(skill)
            
            return skills[:100]  # Limit to 100 skills max (prevent huge lists)
        
        return []  # Return empty list if no skills section found

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications with better filtering"""
        # This method finds professional certifications and licenses
        
        # Look for certification sections
        cert_section = self._extract_section(text, [
            'certifications', 'certificates', 'licenses', 'credentials'
        ])

        if not cert_section:
            return []  # No certification section found

        # Split into lines and clean up
        cert_lines = [line.strip() for line in cert_section.split('\n') if line.strip()]
        certifications = []

        for line in cert_lines:
            # Clean up bullet points and extra whitespace
            clean_line = re.sub(r'^[•·▪▫◦‣⁃\-\*]\s*', '', line.strip())
            # Remove bullet point symbols from the beginning of lines
            
            # Filter valid certifications based on content and length
            if (len(clean_line) > 5 and  # Longer than 5 characters
                # Contains certification keywords OR looks official (has acronyms)
                (any(word in clean_line.lower() for word in ['certified', 'certificate', 'license', 'credential']) or
                 re.search(r'[A-Z]{2,}', clean_line)) and  # Contains acronyms (likely cert names)
                clean_line not in certifications):  # Avoid duplicates
                certifications.append(clean_line)

        return certifications[:10]  # Limit to 10 certifications

    def _extract_awards(self, text: str) -> List[str]:
        """Extract awards with better filtering"""
        # This method finds awards, honors, and recognition
        
        # Look for awards sections
        awards_section = self._extract_section(text, [
            'awards', 'honors', 'achievements', 'recognition', 'accomplishments'
        ])
        
        if not awards_section:
            return []  # No awards section found
        
        # Split into lines and clean up
        award_lines = [line.strip() for line in awards_section.split('\n') if line.strip()]
        awards = []
        
        for line in award_lines:
            # Clean up bullet points
            clean_line = re.sub(r'^[•·▪▫◦‣⁃\-\*]\s*', '', line.strip())
            
            # Filter out section headers and keep actual awards
            if (len(clean_line) > 5 and  # Reasonable length
                # Don't include section headers themselves
                not clean_line.lower().startswith(('award', 'honor', 'achievement', 'recognition')) and
                clean_line not in awards):  # Avoid duplicates
                awards.append(clean_line)
        
        return awards[:8]  # Limit to 8 awards

    def _extract_projects(self, text: str) -> List[Dict]:
        """Enhanced project extraction with better parsing"""
        # This method finds and parses personal or work projects
        
        # Look for projects section
        proj_section = self._extract_section(text, [
            'projects', 'side projects', 'personal projects', 'key projects', 'notable projects'
        ])
        
        if not proj_section:
            print("⚠️ No projects section found")
            return []  # No projects section found
        
        print(f"🚀 Found projects section: {len(proj_section)} characters")
        
        projects = []  # Will store project information
        
        # Method 1: Split by clear project separators
        # Look for patterns that typically separate different projects
        project_patterns = [
            r'\n(?=[A-Z][^a-z\n]{5,})',  # All caps project names
            r'\n(?=\d+\.\s*[A-Z])',      # Numbered projects (1. Project Name)
            r'\n(?=[A-Z][a-zA-Z\s]{10,}:)',  # Project Name: format
            r'\n(?=•\s*[A-Z][a-zA-Z\s]{5,})',  # Bullet points with project names
        ]
        
        project_blocks = []  # Will store separate project text blocks
        # Try each pattern to see if it can split the projects effectively
        for pattern in project_patterns:
            potential_blocks = re.split(pattern, proj_section)
            if len(potential_blocks) > 1:  # If pattern found separators
                project_blocks = potential_blocks
                print(f"📝 Split projects using pattern, found {len(project_blocks)} blocks")
                break  # Use this pattern and stop trying others
        
        # Method 2: If no clear splits, try line-by-line approach
        if len(project_blocks) <= 1:
            lines = proj_section.split('\n')
            current_project = []  # Accumulate lines for current project
            project_blocks = []
            
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                # Check if this line looks like a project title
                # Project titles are usually: short-ish, capitalized, may have special formatting
                if (len(line) < 100 and  # Not too long for a title
                    (line.isupper() or  # All caps
                     line[0].isupper() or  # Starts with capital
                     line.endswith(':') or  # Ends with colon
                     re.match(r'^\d+\.', line) or  # Starts with number
                     line.startswith('•'))):  # Bullet point
                    
                    # Save previous project if we have content
                    if current_project and len('\n'.join(current_project).strip()) > 20:
                        project_blocks.append('\n'.join(current_project))
                    
                    # Start new project
                    current_project = [line]
                else:
                    # Add to current project description
                    if current_project:  # Only if we have a project started
                        current_project.append(line)
            
            # Add the last project
            if current_project and len('\n'.join(current_project).strip()) > 20:
                project_blocks.append('\n'.join(current_project))
        
        print(f"📋 Processing {len(project_blocks)} project blocks")
        
        # Parse each project block to extract structured information
        for i, block in enumerate(project_blocks):
            block = block.strip()
            if len(block) < 20:  # Skip very short blocks (not enough for a real project)
                continue
            
            # Split block into lines
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                continue
            
            # First line is likely the project name
            project_name = lines[0]
            
            # Clean up the project name by removing formatting
            project_name = re.sub(r'^[•·▪▫◦‣⁃\-\*]\s*', '', project_name)  # Remove bullets
            project_name = re.sub(r'^\d+\.\s*', '', project_name)  # Remove numbers like "1. "
            project_name = project_name.rstrip(':')  # Remove trailing colon
            
            # Rest of the lines form the description
            description_lines = lines[1:] if len(lines) > 1 else []
            description = '\n'.join(description_lines).strip()
            
            # Only add if we have a reasonable project name
            if (len(project_name) >= 3 and len(project_name) <= 100 and 
                not project_name.lower() in ['projects', 'key projects', 'notable projects']):
                
                project_info = {
                    'name': project_name,
                    'description': description if description else 'No description available'
                }
                projects.append(project_info)
                print(f"✅ Added project: {project_name}")
        
        print(f"🎉 Total projects extracted: {len(projects)}")
        return projects[:10]  # Limit to 10 projects max

    def _extract_section(self, text: str, section_names: List[str]) -> Optional[str]:
        """Extract a specific section from resume text"""
        # This is a helper method that finds and extracts specific sections from the resume
        
        lines = text.split('\n')  # Split entire resume into lines
        section_start = -1  # Will mark where our target section begins
        section_end = len(lines)  # Will mark where our target section ends (default: end of document)
        
        # Find section start by looking for section headers
        for i, line in enumerate(lines):
            line_clean = line.strip().lower()  # Clean line for comparison
            # Check if this line contains any of our target section names
            for section_name in section_names:
                # If section name is found in line and line is short (likely a header)
                if section_name.lower() in line_clean and len(line_clean) < 50:
                    section_start = i  # Mark this as section start
                    break
            if section_start != -1:  # If we found the section
                break  # Stop looking
        
        if section_start == -1:  # If we never found the section
            return None  # Section doesn't exist
        
        # Find section end (next major section or end of document)
        for i in range(section_start + 1, len(lines)):  # Start looking after section header
            line = lines[i].strip()
            # Check if this line looks like a new section header
            if (line and len(line) < 50 and  # Non-empty and short (header-like)
                any(keyword in line.lower() for keyword in ['experience', 'education', 'skills', 'projects', 'awards'])):
                section_end = i  # Mark end of current section
                break
        
        # Extract the section content
        section_lines = lines[section_start:section_end]
        return '\n'.join(section_lines)  # Return section as text


def parse_resume_for_flask(file_path: str, user_id: int = None) -> Dict: 
    """Enhanced function for Flask integration with better error handling"""
    # This is a standalone function (not part of the class) for easy use with Flask web framework
    
    parser = ResumeParser()  # Create a new parser instance
    try:
        # Try to parse the resume
        parsed_data = parser.parse_resume(file_path, user_id)
        # If successful, return success response
        return{
            'success': True,           # Flag indicating success
            'data': parsed_data,       # The actual parsed resume data
            'message': 'Resume parsed successfully'  # Human-readable message
        }
    except Exception as e:  # If anything goes wrong
        # Return error response instead of crashing
        return{
            'success': False,          # Flag indicating failure
            'data': None,              # No data since parsing failed
            'message': f'Resume parsing failed: {str(e)}'  # Error message
        }

# This section only runs when the script is executed directly (not imported)
if __name__ == "__main__":
    parser = ResumeParser()  # Create a parser instance
    
    # Test with your resume file
    test_file = "rori.pdf"  # Make sure this file exists in the same directory
    
    # Check if the test file exists before trying to parse it
    if Path(test_file).exists():
        try:
            print("🔄 Starting to parse resume...")
            result = parser.parse_resume(test_file)  # Parse the resume
            print("✅ Resume parsed successfully!")
            print("\n" + "="*50)
            print("           📋 RESUME PARSING RESULTS")
            print("="*50)
            
            # Display Personal Information
            personal_info = result.get('personal_info', {})  # Get personal info, default to empty dict
            print(f"👤 Name: {personal_info.get('name', 'Not found')}")
            print(f"📧 Email: {personal_info.get('email', 'Not found')}")
            print(f"📱 Phone: {personal_info.get('phone', 'Not found')}")
            print(f"📍 Location: {personal_info.get('location', 'Not found')}")
            
            # Display Skills - Better formatting
            skills = result.get('skills', [])
            if skills:  # If we found skills
                print(f"\n💪 Skills ({len(skills)}):")
                # Group skills into lines of 3-4 for better readability
                for i in range(0, len(skills), 4):  # Process in groups of 4
                    skill_group = skills[i:i+4]  # Take next 4 skills
                    print(f"   {' | '.join(skill_group)}")  # Join with pipe separator
            else:
                print("\n💪 Skills: None found")
            
            # Display Experience - Cleaner format
            experience = result.get('experience', [])
            if experience:  # If we found work experience
                print(f"\n💼 Work Experience ({len(experience)}):")
                for i, exp in enumerate(experience, 1):  # Number each job starting from 1
                    if isinstance(exp, dict):  # Make sure it's a dictionary
                        # Extract job details with defaults
                        title = exp.get('title', 'Unknown Title')
                        company = exp.get('company', 'Unknown Company')
                        duration = exp.get('duration', 'Duration not specified')
                        
                        print(f"\n   {i}. {title}")
                        print(f"      Company: {company}")
                        print(f"      Duration: {duration}")
                        
                        # Show key responsibilities (limit to 2-3 to avoid clutter)
                        descriptions = exp.get('description', [])
                        if descriptions:  # If there are job descriptions
                            print(f"      Key Responsibilities:")
                            for desc in descriptions[:3]:  # Show only first 3
                                print(f"        • {desc}")
                            if len(descriptions) > 3:  # If there are more than 3
                                print(f"        • ... and {len(descriptions) - 3} more")
            else:
                print("\n💼 Experience: None found")
            
            # Display Education - No duplicates
            education = result.get('education', [])
            if education:  # If we found education information
                print(f"\n🎓 Education ({len(education)}):")
                for i, edu in enumerate(education, 1):  # Number each entry
                    if isinstance(edu, dict):  # Make sure it's a dictionary
                        # Extract education details with defaults
                        degree = edu.get('degree', 'Unknown Degree')
                        institution = edu.get('institution', 'Unknown Institution')
                        year = edu.get('year', 'Year not specified')
                        
                        print(f"\n   {i}. {degree}")
                        print(f"      Institution: {institution}")
                        print(f"      Year: {year}")
            else:
                print("\n🎓 Education: None found")
            
            # Display Projects - Better parsing
            projects = result.get('projects', [])
            if projects:  # If we found projects
                print(f"\n🚀 Projects ({len(projects)}):")
                for i, project in enumerate(projects, 1):  # Number each project
                    if isinstance(project, dict):  # Make sure it's a dictionary
                        name = project.get('name', 'Unknown Project')
                        desc = project.get('description', 'No description')
                        
                        print(f"\n   {i}. {name}")
                        if desc and desc != 'No description available':
                            # Truncate very long descriptions for readability
                            if len(desc) > 200:
                                print(f"      {desc[:200]}...")
                            else:
                                print(f"      {desc}")
            else:
                print("\n🚀 Projects: None found")
            
            # Display Certifications
            certifications = result.get('certifications', [])
            if certifications:  # If we found certifications
                print(f"\n🏆 Certifications ({len(certifications)}):")
                for cert in certifications:
                    print(f"   • {cert}")
            else:
                print("\n🏆 Certifications: None found")
            
            # Display Awards  
            awards = result.get('awards', [])
            if awards:  # If we found awards
                print(f"\n🏅 Awards & Recognition ({len(awards)}):")
                for award in awards:
                    print(f"   • {award}")
            else:
                print("\n🏅 Awards: None found")
            
            # Display Metadata (information about the parsing process)
            metadata = result.get('metadata', {})
            print(f"\n📊 Document Info:")
            print(f"   File: {metadata.get('file_name', 'Unknown')}")
            print(f"   Size: {metadata.get('file_size', 0):,} bytes")  # :, adds commas to numbers
            print(f"   Words: {metadata.get('word_count', 0):,}")
            
            print("="*50)  # Closing line
            
        except Exception as e:  # If parsing fails
            import traceback
            print(f"❌ Error: {e}")
            print("Full traceback:")
            traceback.print_exc()  # Print detailed error information for debugging
    else:
        print(f"❌ Test file '{test_file}' not found. Please add a resume file to test.")