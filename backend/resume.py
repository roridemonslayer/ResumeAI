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
try:
    import spacy #this is for text analysis
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("spaCy not installed. Some features will be limited.")

class ResumeParser: #this makes a class called resume parser    
    #a class is a blueprint for creating objects, providing initial values for state (member variables) and implementations of behavior (member functions or methods).    
    def __init__(self): #constructor method called when having new resume        
        #initialize parser with spacy        
        self.nlp = None
        if SPACY_AVAILABLE:
            try:         
                self.nlp = spacy.load("en_core_web_sm") #this tries to load a pre-trained spaCy language model called "en_core_web_sm" (the "small English model").         
                print("✅ Spacy works YAYYYYy")            
                #if it works it'll print what I have up there        
            except OSError:         
                print("⚠️ Spacy doesn't work BOOOO") #this prints that like spacey doesn't work         
                self.nlp = None #sets nlp to none so the rest of the program knows its missing. 
                #basically saying the nlp can't process the human language to interpret. 
        else:
            print("⚠️ spaCy not available. Install it with: pip install spacy")
    
    def parse_resume(self, file_path: str, user_id: int = None ) -> Dict: #returns stuff in a dict/hashmap type with a key being assigned to a value the key being the resume        
        #self just refers to the resume instance, file_path is the path to the resume, the user_id is just for user id and if there isn't one it'll say none, and -> dict returns dict with all of resume parsed info               
        if not Path(file_path).exists():            
            raise FileNotFoundError(f"Resume wasn't found: {file_path}") #this js checks if the resume was in there      
        
        file_extension = Path(file_path).suffix.lower() #What this is saying is to get the file extension in lowercase.        
        if file_extension == ".pdf":             
            text = self._extracting_from_pdf(file_path) #processing method for pdf          
        elif file_extension in ['.docx','.doc']:             
            text = self._extracting_from_docx(file_path) #processing method for docx         
        else:             
            raise ValueError(f"Unsupported file format: {file_path}") # returns false statement that the file type isn't supported like if it isn't a pdf or a docx it won't process. 
            
        if not text.strip():   #this is basically saying if no white space is found. this is just checking if the string is empty      
            raise ValueError("no text could be found")  #print that no text could be found
        #this is important when Scanned PDFs without OCR (image-only PDFs) corrupted files that opened but contained no text and files with only images/graphics

        #now we're going to parse the extracted text
        parsed_data = self._parse_text(text) #so this line is to set up the parse data like the users name, experience, education etc etc. 
        #it returns the parse info in a dict form or "hash map form"

        #now we make the meta data. meta data just contained info on what the parse just processed. 
        #the meta data is It provides essential information about the parsing process itself, file characteristics, and processing statistics that are crucial for debugging, analytics, and database management so keep this in mind for next time your working with meta data. 
        parsed_data['metadata'] = { #what this does is create a metadata function in the dict parsed data. 
            'file_path':file_path, #this is just the original resume file tied to the metadata
            'file_name' :Path(file_path).name, #what this does is convert a file like Path("/uploads/resumes/john_doe.pdf").name to john_doe.pdf/ it just output the file name in a simple way.
            'file_size' : os.path.getsize(file_path), #this is how much space the file takes up on the disk. the disk of the computer ex. 202020 would be like 2.0 gb
            "parsed_at" : datetime.utcnow().isoformat(), #what this does is just display the time in which the resume was parsed
            #isoformat converts into "2024-01-15T14:30:25.123456" this format when displaying the time and day it was created. 
            'user_id' : user_id, #this just tracks the users id. each user is assigned an id 
            "text_length" :len(text), #this just tracks like the lengths of the text in the file. for example if a file has like 210010 text include punctuation, letters spaces etc 
            "word_count" :len(text.split())  #this just only tracks the word count not including yk white space, just the words
        }
        return parsed_data
    
    def _extracting_from_pdf(self, pdf_path: str) -> str: #what this is, we're making a function for extracting the data from the pdf, it'll return everything in string format.
        #the pdf_path is the file path to the pdf and then it'll return it as a string
        text = "" #this an empty string because this is where the accumulated extracted text will go 
        
        # Try PDFPlumber first
        try: # try is just like saying "this might be risky code, try it"
            with pdfplumber.open(pdf_path) as pdf: # so what this is doing is that its opening the file for u, thats why u use with. with with
                #it opens the file and then when ur done with it, it completely closes this block out even if there's an error in the middle 
                #so that line is just opening the file
                 #it makes the the pdf is closed properly even if there is an error
                for page in pdf.pages:  #this is going to be looping through each page in the pdf the pdf.pages is a list of all the pages in the pdf 
                    page_text = page.extract_text() #this is a method from pdf plumber. and it just tried to pull text form the pdf 
                    if page_text: 
                        text += page_text + "\n" # this one add the current page's text to the overall text, followed by a newline for separation
            if text.strip(): #this just again removes extra white space from the end and beginning of the new text
                print("📄 Text Extracted from PDF Plumber")
                return text #send the full extracted text of the document when this function is called. 
        except Exception as e: #this will run if any error is found int he try function 
            #exception is a function in python that catches errors in ur code
            #e just stores the error object in e 
            print(f"PDFPlumber failed gang: {e}") #the e will get replace with the error message 
            
        #this is just a fall back if pdfplumber doesn't work. 
        try: #again the try method its like js try this even if errors come up
            doc = fitz.open(pdf_path) #this opens the pdf using the  PyMuPDF
            #Returns a Document object stored in the variable doc. #Unlike the with statement, this does not auto-close — we'll have to call .close() manually later.
            for page in doc: #loops through each page in the doc, 
                text += page.get_text() #Adds (+=) that text to the text variable we've been building.
            doc.close() #this just manually closes the loop because we didn't have a with statement.
            if text.strip():
                print("📄 Text Extracted from PyMuPDF")
                return text #returns the extracted text. 
        except Exception as e:  # just raises the error that it failed.
            print(f"PyMuPDF failed: {e}")
        
        return text
    
    def _extracting_from_docx(self, docx_path: str) -> str: #so this is how we're going to extract the info from docx
        try: 
            doc = Document(docx_path) 
            text = "" #this is the empty space to store the text extracted
            for paragraph in doc.paragraphs: # loops through the paragraphs in the word doc (FIXED: removed () because paragraphs is a property not method)
                text += paragraph.text + "\n" # add the text to the paragraph variable to be used later
            print("📄 text extracted from docx")
            return text
        except Exception as e:
            print(f"text extraction from DOCX: {e}") 
            return ""

    def _parse_text(self, text: str) -> dict: #so what this is going is just initializing what we're going to use to parse the
        doc = self.nlp(text) if self.nlp else None #what this is doing is taking the text and transform it into a doc the text from the pdf and converting it into language that is 
        #readable for the spacy model to understand.
        result = { #this is just extracting all the necessary from the resume like the personal info the experience
            "personal_info" : {}, 
            "experience" :[], 
            "education" : [], 
            "skills" : [], 
            "certifications" : [],
            "awards" : [], 
            "projects" : [], 
            "raw_text" : text #this just keeps the original text if needed.
        }

        result['personal_info'] = self._extract_personal_info(text, doc) #this gets info like name, number, email.
        result["experience"] = self._extract_experience(text) #this will just extract the experience from the resume
        result['education'] = self._extract_education(text, doc) #takes the education from the resume and uses  NLP entity recognition to detect school names, degrees, and dates
        result['skills'] = self._extract_skills(text) #takes the skills
        result['certifications'] = self._extract_certifications(text) 
        result['awards'] = self._extract_awards(text)
        result['projects'] = self._extract_projects(text) #just takes the raw text

        return result
    #now we're going to make functions for each part of the text extraction process
    
    def _extract_personal_info(self, text: str, doc) -> dict: 
        #so this us defining the personal info method, it's taking in the raw resume text and the spaCy doc and returns a dict of the personal info. hence the ->
        personal_info = {} 
        #this is just an empty field that'll be filled with the personal info later on 

        emails = re.findall(
            #what re.findall does is that it extracts all substrings that look like emails
           r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text
        )#as seen above is a email regex pattern. the \b just makes sure that the match starts clearly and ends cleanly
        #regex tells python what kinds of text to match in the email or wtv it is ur using
        #the a-z and, the 0-9 and the room for special characters are all apart of the components for the email. 
        #the @ symbol is for the @ part of the email, think of regex pattern has characters that contain all of the possible components that could be inside the resume

        personal_info['email'] = emails[0] if emails else None #it takes the first email if any, but if there isn't then there's none else 

        phone_patterns = [
         r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  #domestic numbers
         r'\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}' #international numbers more generic
        ]
        matches = [] #stores are the all the phone numbers
        for pattern in phone_patterns: #loops through each phone number pattern
            for match in re.finditer(pattern, text): #re.finditer() finds all matches of the pattern in the text, but instead of returning a list of strings, it returns an iterator of match objects.
                phone = match.group(0)
                phone = re.sub(r'\D+','',phone) #Remove non-digits
                matches.append(phone)

        personal_info['phone'] = matches[0] if matches else None

        # Extract names (using spaCy if available)
        if doc:
            names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
            personal_info['name'] = names[0] if names else None
        else:
            # Simple name extraction without spaCy - look in first few lines for likely names
            lines = text.split('\n')[:5]  # Check first 5 lines
            for line in lines:
                line = line.strip()
                if len(line.split()) == 2 and line.replace(' ', '').isalpha():
                    personal_info['name'] = line
                    break
            else:
                personal_info['name'] = None

        #this uses spaCy NER to grab entities labeled PERSON 

        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        personal_info['linkedin'] = linkedin_matches[0] if linkedin_matches else None

        #what this is doing is finding the first match of the url no matter where it might be on the resume. it just keeps the one it found first

        # Extract location (using spaCy if available)
        if doc:
            locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
            personal_info['location'] = locations[0] if locations else None
        else:
            personal_info['location'] = None

        #Remember that spaCy is a NLP library that can read text and figure out what the role of each word is. 
        #the doc is coming from self.nlp(text) which is spaCy processing the resume
        #doc.ents means that all the named entities spaCy found like names, dates, cities etc 
        #GPE stands for geo political entity so country states, cities 
        #loc stands for location so like mountains rivers etc
        #doc ents is filter that keeps things that are tagged as GPE or LOC
        #it also finds the first location in the doc and saves it was personal_info['location"]
        
        return personal_info
    
    #extracting experience - ENHANCED VERSION
    def _extract_experience(self, text: str) -> List[Dict]:
        """Enhanced experience extraction method"""
        experience = []
        
        try:
            # Look for experience section
            experience_section = self._extract_section(text, [
                'experience', 'work history', 'employment', 'professional experience',
                'work experience', 'career history', 'employment history'
            ])
            
            if not experience_section:
                print("⚠️ No experience section found, trying to extract from full text...")
                # Fallback: look for job-like patterns in full text
                experience_section = text
            
            print(f"🔍 Experience section found: {len(experience_section)} characters")
            
            # Split into job blocks using improved logic
            job_blocks = self._split_into_job_blocks(experience_section)
            
            print(f"📋 Found {len(job_blocks)} potential job blocks")
            
            # Parse each job block
            for i, block in enumerate(job_blocks):
                try:
                    block = block.strip()
                    if len(block) < 30:  # Skip very short blocks
                        continue
                    
                    print(f"🔄 Processing job block {i+1}: {block[:100]}...")
                    
                    job_info = self._parse_job_block(block)
                    if job_info and job_info.get('title'):
                        experience.append(job_info)
                        print(f"✅ Successfully parsed job: {job_info.get('title', 'Unknown')}")
                    else:
                        print(f"❌ Failed to parse job block {i+1}")
                        
                except Exception as e:
                    print(f"⚠️ Error parsing job block {i+1}: {e}")
                    continue
            
            print(f"🎉 Total jobs extracted: {len(experience)}")
            return experience
            
        except Exception as e:
            print(f"❌ Critical error in _extract_experience: {e}")
            return []

    def _split_into_job_blocks(self, text: str) -> List[str]:
        """Split experience section into individual job blocks"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Job title indicators - expanded list
        job_indicators = [
            'intern', 'fellow', 'instructor', 'engineer', 'developer', 'analyst',
            'manager', 'specialist', 'coordinator', 'assistant', 'associate',
            'director', 'consultant', 'technician', 'lead', 'senior', 'junior',
            'software', 'data', 'web', 'full stack', 'backend', 'frontend',
            'machine learning', 'quantum computing', 'python'
        ]
        
        job_blocks = []
        current_block = []
        
        print(f"🔍 Processing {len(lines)} lines for job splitting")
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_lower = line.lower()
            
            # Skip section headers
            if any(header in line_lower for header in ['experience', 'work history', 'employment']) and len(line) < 50:
                print(f"⏭️ Skipping header: {line}")
                i += 1
                continue
            
            # Check if this line looks like a job title
            is_job_title = any(indicator in line_lower for indicator in job_indicators)
            
            # Look ahead for date patterns in the next few lines
            has_date_pattern = False
            check_lines = [line]
            for j in range(1, min(4, len(lines) - i)):  # Check next 3 lines
                check_lines.append(lines[i + j])
            
            for check_line in check_lines:
                if re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b.*(?:Present|Current|\d{4})', 
                            check_line, re.IGNORECASE):
                    has_date_pattern = True
                    break
            
            # Start new job block if we find a job title with dates nearby
            if is_job_title and has_date_pattern and current_block:
                # Save previous block
                print(f"💼 Found new job, saving previous block: {current_block[0][:50]}...")
                job_blocks.append('\n'.join(current_block))
                current_block = [line]
                print(f"🆕 Starting new job block: {line}")
            elif is_job_title and has_date_pattern:
                # Start first block
                current_block = [line]
                print(f"🆕 Starting job block: {line}")
            elif current_block:  # Add to existing block
                current_block.append(line)
            
            i += 1
        
        # Add the last block
        if current_block:
            print(f"💼 Adding final job block: {current_block[0][:50]}...")
            job_blocks.append('\n'.join(current_block))
        
        print(f"📦 Total job blocks created: {len(job_blocks)}")
        return job_blocks

    def _parse_job_block(self, block: str) -> Optional[Dict]:
        """Parse individual job block into structured data"""
        try:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                return None

            job_info = {
                "title": None,
                "company": None,
                "location": None,
                "duration": None,
                "description": []
            }

            print(f"🔍 Parsing job block with {len(lines)} lines:")
            for i, line in enumerate(lines[:5]):  # Show first 5 lines
                print(f"   {i}: {line}")

            # Extract job title (first line that contains job keywords)
            job_keywords = ['intern', 'fellow', 'instructor', 'engineer', 'developer', 'analyst', 
                        'manager', 'specialist', 'coordinator', 'assistant', 'associate', 
                        'director', 'consultant', 'technician', 'lead', 'senior', 'junior',
                        'software', 'data', 'web', 'machine learning', 'quantum computing']
            
            title_line_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('•') or line.startswith('-'):
                    break  # Stop at bullet points
                    
                if any(keyword in line.lower() for keyword in job_keywords) or i == 0:
                    # Clean the title by removing date information
                    title = line
                    # Remove common date patterns from title
                    title = re.sub(r'\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}.*$', '', title, flags=re.IGNORECASE)
                    title = re.sub(r'\s+\d{1,2}/\d{4}.*$', '', title)
                    title = re.sub(r'\s+\d{4}.*$', '', title)
                    job_info['title'] = title.strip()
                    title_line_idx = i
                    print(f"✅ Found title: {job_info['title']}")
                    break

            # Extract duration from the entire block
            date_patterns = [
                r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\s*[–—-]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)',
                r'(\d{1,2}/\d{4})\s*[–—-]\s*(\d{1,2}/\d{4}|Present|Current)',
                r'(\d{4})\s*[–—-]\s*(\d{4}|Present|Current)',
            ]

            for pattern in date_patterns:
                match = re.search(pattern, block, re.IGNORECASE)
                if match:
                    start_date, end_date = match.groups()
                    job_info['duration'] = f"{start_date} – {end_date}"
                    print(f"✅ Found duration: {job_info['duration']}")
                    break

            # Extract company name (look for line after title that's not a bullet or date)
            for i in range(title_line_idx + 1, min(title_line_idx + 4, len(lines))):
                if i < len(lines):
                    line = lines[i]
                    
                    # Skip lines with bullets, dates, or known description starters
                    if (line.startswith('•') or line.startswith('-') or 
                        re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4}|Present|Current)', line, re.IGNORECASE) or
                        any(line.lower().startswith(starter) for starter in ['researched', 'demonstrated', 'collaborated', 
                            'built', 'developed', 'implemented', 'led', 'mentored', 'organized', 'boosted', 'increased'])):
                        continue
                    
                    # This should be the company (if it's reasonable length)
                    if 3 < len(line) < 100:
                        job_info['company'] = line.strip()
                        print(f"✅ Found company: {job_info['company']}")
                        break

            # Extract location patterns
            location_patterns = [
                r'\bRemote\b',
                r'\bHybrid\b', 
                r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, State
                r'\b[A-Z][a-z\s]+,\s*[A-Z][a-z\s]+\b'  # City, Country
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, block)
                if match:
                    job_info['location'] = match.group().strip()
                    print(f"✅ Found location: {job_info['location']}")
                    break

            # Extract descriptions (bullet points and substantial content lines)
            print("🔍 Extracting descriptions...")
            for line in lines:
                line = line.strip()
                
                # Skip very short lines
                if len(line) < 10:
                    continue
                
                # Skip title and company lines
                if (job_info.get('title') and line == job_info['title']) or \
                (job_info.get('company') and line == job_info['company']):
                    continue
                
                # Skip date-only lines
                if re.match(r'^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[–—-]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)$', 
                        line, re.IGNORECASE):
                    continue
                
                # Clean and add description lines
                clean_line = line
                if line.startswith('•'):
                    clean_line = line[1:].strip()
                elif line.startswith('-'):
                    clean_line = line[1:].strip()
                elif line.startswith('*'):
                    clean_line = line[1:].strip()
                
                # Add substantial content that's not already captured
                if (len(clean_line) > 10 and 
                    clean_line != job_info.get('title', '') and 
                    clean_line != job_info.get('company', '') and
                    clean_line not in job_info['description']):
                    
                    # Check if it's likely a description (contains action words or is a bullet point)
                    action_indicators = ['researched', 'demonstrated', 'collaborated', 'built', 'developed', 
                                    'implemented', 'led', 'mentored', 'organized', 'boosted', 'increased',
                                    'created', 'designed', 'analyzed', 'improved', 'optimized', 'managed']
                    
                    if (line.startswith('•') or line.startswith('-') or 
                        any(indicator in clean_line.lower() for indicator in action_indicators) or
                        len(clean_line) > 30):  # Long lines are likely descriptions
                        
                        job_info['description'].append(clean_line)
                        print(f"   📝 Added description: {clean_line[:60]}...")

            print(f"✅ Total descriptions extracted: {len(job_info['description'])}")

            # Return job if we have essential info
            if job_info.get('title'):
                return job_info
            else:
                print("❌ No title found, skipping job")
                return None

        except Exception as e:
            print(f"❌ Error in _parse_job_block: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    

    def _extract_education(self, text: str, doc) -> List[Dict]:
        """Extract education with duplicate prevention"""
        education = []
        education_section = self._extract_section(
            text, 
            ['education', 'academic background', 'qualifications', 'academic', 'schooling']
        )

        if not education_section:
            print("⚠️ No education section found, searching entire text...")
            education_section = text
        
        # Extract organizations using spaCy if available
        organizations = []
        if doc:
            organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        # Enhanced degree patterns
        degree_patterns = [
            r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Diploma|Certificate)(?:\s+of\s+(?:Science|Arts|Engineering|Business|Law|Medicine))?\b[^.\n]*',
            r'\b(?:BS|BA|MS|MA|MBA|PhD|BSc|MSc|MD|JD|LLM|BFA|MFA)\b[^.\n]*',
            r'\b(?:B\.S\.|B\.A\.|M\.S\.|M\.A\.|Ph\.D\.|M\.B\.A\.)\b[^.\n]*',
            r'\b(?:High School Diploma|GED)\b[^.\n]*'
        ]

        degrees = []
        for pattern in degree_patterns:
            found_degrees = re.findall(pattern, education_section, re.IGNORECASE)
            degrees.extend(found_degrees)

        # Look for GPA information
        gpa_pattern = r'GPA:?\s*(\d+\.?\d*(?:/\d+\.?\d*)?|\d+\.?\d*)'
        gpa_matches = re.findall(gpa_pattern, education_section, re.IGNORECASE)
        
        # Remove duplicates while preserving order
        seen_degrees = set()
        unique_degrees = []
        for degree in degrees:
            degree_clean = degree.strip().lower()
            if degree_clean not in seen_degrees and len(degree_clean) > 5:
                seen_degrees.add(degree_clean)
                unique_degrees.append(degree.strip())
        
        for i, degree in enumerate(unique_degrees):
            edu_info = {
                'degree': degree,
                'institution': organizations[i] if i < len(organizations) else "Institution not found",
                "year": None,
                "gpa": None
            }
            
            # Extract year from the degree line or nearby text
            year_match = re.search(r'\b(19|20)\d{2}\b', degree)
            if year_match:
                edu_info['year'] = year_match.group()
            
            # Extract GPA if found
            if gpa_matches and i < len(gpa_matches):
                edu_info['gpa'] = gpa_matches[i]
            
            education.append(edu_info)
        
        # Remove duplicate entries based on degree and institution
        final_education = []
        seen_combos = set()
        for edu in education:
            combo = f"{edu['degree']}-{edu['institution']}".lower()
            if combo not in seen_combos:
                seen_combos.add(combo)
                final_education.append(edu)
        
        return final_education
    def _extract_skills(self, text: str) -> List[str]:
        """Enhanced skills extraction that properly handles categorized skills"""
        # First, try to find the skills section
        skills_section = self._extract_section(text, [
            'skills', 'technical skills', 'core competencies', 'technologies', 
            'technical competencies', 'proficiencies', 'expertise'
        ])
        
        found_skills = []
        
        if skills_section:
            print("🔧 Found skills section, parsing...")
            
            # Handle structured skills (like "Languages: skill1, skill2")
            category_pattern = r'([A-Za-z][A-Za-z\s/]+):\s*([^:\n]+(?:\n[^:\n]+)*?)(?=\n[A-Za-z][A-Za-z\s/]+:|$)'
            category_matches = re.findall(category_pattern, skills_section, re.MULTILINE)
            
            if category_matches:
                print(f"📋 Found {len(category_matches)} skill categories")
                for category, skills_text in category_matches:
                    print(f"   Processing category: {category}")
                    
                    # Clean up the skills text - handle line breaks and various separators
                    skills_text = re.sub(r'\n+', ' ', skills_text)  # Replace newlines with spaces
                    skills_text = re.sub(r'[•·▪▫◦‣⁃]', ',', skills_text)  # Replace bullets with commas
                    skills_text = re.sub(r'\s*[,;|]\s*', ',', skills_text)  # Normalize separators
                    skills_text = re.sub(r'\s+', ' ', skills_text)  # Clean up extra spaces
                    
                    # Split by commas and clean each skill
                    category_skills = [s.strip() for s in skills_text.split(',') if s.strip()]
                    
                    for skill in category_skills:
                        # Clean up individual skill
                        skill = skill.strip()
                        
                        # Filter out invalid skills
                        if (len(skill) >= 2 and len(skill) <= 50 and 
                            not re.match(r'^(skills?|technical|core|competencies|technologies)$', skill, re.IGNORECASE) and
                            skill not in found_skills):  # Avoid duplicates
                            found_skills.append(skill)
                            print(f"     ✅ Added skill: {skill}")
            
            else:
                # Fallback: treat the entire section as comma-separated skills
                print("📝 No categories found, treating as flat list")
                cleaned_section = re.sub(r'[•·▪▫◦‣⁃]', ',', skills_section)
                cleaned_section = re.sub(r'[\|\;]', ',', cleaned_section)
                cleaned_section = re.sub(r'\n+', ',', cleaned_section)
                cleaned_section = re.sub(r'\s*,\s*', ',', cleaned_section)
                
                potential_skills = [s.strip() for s in cleaned_section.split(',') if s.strip()]
                
                for skill in potential_skills:
                    skill = skill.strip()
                    if (len(skill) >= 2 and len(skill) <= 50 and 
                        not re.match(r'^(skills?|technical|core|competencies|technologies)$', skill, re.IGNORECASE) and
                        not skill.lower() in ['and', 'or', 'with', 'including', 'experience'] and
                        skill not in found_skills):
                        found_skills.append(skill)
        
        # Fallback: look for common technical skills in the entire text if skills section is sparse
        if len(found_skills) < 5:
            print("🔍 Skills section sparse, searching for common technical terms...")
            skill_keywords = [
                # Programming Languages
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin',
                'HTML', 'CSS', 'HTML/CSS', 'MatLab', 'MATLAB', 'R', 'Scala',
                # Web Technologies  
                'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask', 'Bootstrap', 'Tailwind', 'Next.js',
                # Databases
                'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle',
                # Cloud & DevOps
                'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab', 'Google Colab',
                # Data & AI
                'Machine Learning', 'Data Analysis', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'Tableau', 'Power BI', 'Excel',
                'Matplotlib', 'Seaborn', 'Jupyter', 'Jupyter Notebook', 'Qiskit', 'YFinance', 'LangChain', 'FastAPI',
                # Tools
                'VS Code', 'PyCharm', 'Figma', 'Softr', 'Zustand', 
                # Other Technical
                'API', 'REST', 'GraphQL', 'Microservices', 'Agile', 'Scrum'
            ]
            
            text_lower = text.lower()
            for skill in skill_keywords:
                # Check for exact matches or close variations
                if (skill.lower() in text_lower or 
                    skill.replace(' ', '').lower() in text_lower.replace(' ', '') or
                    skill.replace('.', '').lower() in text_lower.replace('.', '')):
                    if skill not in found_skills:
                        found_skills.append(skill)
        
        # Remove duplicates while preserving order and limit to reasonable number
        seen = set()
        final_skills = []
        for skill in found_skills:
            skill_lower = skill.lower().replace(' ', '').replace('.', '')
            if skill_lower not in seen and len(final_skills) < 30:  # Increased limit
                seen.add(skill_lower)
                final_skills.append(skill)
        
        print(f"✅ Found {len(final_skills)} unique skills")
        return final_skills
        
        
        
            

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications with better filtering"""
        cert_section = self._extract_section(text, [
            'certifications', 'certificates', 'licenses', 'credentials'
        ])

        if not cert_section:
            return []

        cert_lines = [line.strip() for line in cert_section.split('\n') if line.strip()]
        certifications = []

        for line in cert_lines:
            # Clean up bullet points and extra whitespace
            clean_line = re.sub(r'^[•·▪▫◦‣⁃\-\*]\s*', '', line.strip())
            
            # Filter valid certifications (longer than 5 chars, contains cert keywords or looks official)
            if (len(clean_line) > 5 and 
                (any(word in clean_line.lower() for word in ['certified', 'certificate', 'license', 'credential']) or
                 re.search(r'[A-Z]{2,}', clean_line)) and  # Contains acronyms (likely cert names)
                clean_line not in certifications):  # Avoid duplicates
                certifications.append(clean_line)

        return certifications[:10]  # Limit to 10 certifications

    def _extract_awards(self, text: str) -> List[str]:
        """Extract awards with better filtering"""
        awards_section = self._extract_section(text, [
            'awards', 'honors', 'achievements', 'recognition', 'accomplishments'
        ])
        
        if not awards_section:
            return []
        
        award_lines = [line.strip() for line in awards_section.split('\n') if line.strip()]
        awards = []
        
        for line in award_lines:
            # Clean up bullet points
            clean_line = re.sub(r'^[•·▪▫◦‣⁃\-\*]\s*', '', line.strip())
            
            # Filter out section headers and keep actual awards
            if (len(clean_line) > 5 and 
                not clean_line.lower().startswith(('award', 'honor', 'achievement', 'recognition')) and
                clean_line not in awards):
                awards.append(clean_line)
        
        return awards[:8]  # Limit to 8 awards

    def _extract_projects(self, text: str) -> List[Dict]:
        """Enhanced project extraction with better parsing"""
        proj_section = self._extract_section(text, [
            'projects', 'side projects', 'personal projects', 'key projects', 'notable projects'
        ])
        
        if not proj_section:
            print("⚠️ No projects section found")
            return []
        
        print(f"🚀 Found projects section: {len(proj_section)} characters")
        
        projects = []
        
        # Method 1: Split by clear project separators
        # Look for patterns like "Project Name" followed by description
        project_patterns = [
            r'\n(?=[A-Z][^a-z\n]{5,})',  # All caps project names
            r'\n(?=\d+\.\s*[A-Z])',      # Numbered projects (1. Project Name)
            r'\n(?=[A-Z][a-zA-Z\s]{10,}:)',  # Project Name: format
            r'\n(?=•\s*[A-Z][a-zA-Z\s]{5,})',  # Bullet points with project names
        ]
        
        project_blocks = []
        for pattern in project_patterns:
            potential_blocks = re.split(pattern, proj_section)
            if len(potential_blocks) > 1:
                project_blocks = potential_blocks
                print(f"📝 Split projects using pattern, found {len(project_blocks)} blocks")
                break
        
        # Method 2: If no clear splits, try line-by-line approach
        if len(project_blocks) <= 1:
            lines = proj_section.split('\n')
            current_project = []
            project_blocks = []
            
            for line in lines:
                line = line.strip()
                if not line:
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
        
        # Parse each project block
        for i, block in enumerate(project_blocks):
            block = block.strip()
            if len(block) < 20:  # Skip very short blocks
                continue
            
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                continue
            
            # First line is likely the project name
            project_name = lines[0]
            
            # Clean up the project name
            project_name = re.sub(r'^[•·▪▫◦‣⁃\-\*]\s*', '', project_name)  # Remove bullets
            project_name = re.sub(r'^\d+\.\s*', '', project_name)  # Remove numbers
            project_name = project_name.rstrip(':')  # Remove trailing colon
            
            # Rest is description
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
        """Enhanced section extraction with better boundary detection"""
        text_lower = text.lower()
        
        for section_name in section_names:
            # Create more flexible pattern that handles various formatting
            patterns = [
                rf'\b{re.escape(section_name)}\b.*?(?=\n\s*(?:[A-Z][A-Z\s]*|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n|\Z)',  # Next section or end
                rf'\b{re.escape(section_name)}\b.*?(?=\n\n[A-Z]|\Z)',  # Double newline + capital or end
                rf'\b{re.escape(section_name)}\b[:\-\s]*\n(.*?)(?=\n[A-Z][A-Z\s]{3,}\n|\Z)',  # Section header pattern
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
                if match:
                    # Get the original case text using the match positions
                    start, end = match.span()
                    original_text = text[start:end]
                    print(f"📍 Found section '{section_name}': {len(original_text)} characters")
                    return original_text
        
        return None


def parse_resume_for_flask(file_path: str, user_id: int = None) -> Dict: 
    """Enhanced function for Flask integration with better error handling"""
    parser = ResumeParser()
    try:
        parsed_data = parser.parse_resume(file_path, user_id)
        return{
            'success': True,
            'data': parsed_data,
            'message': 'Resume parsed successfully'
        }
    except Exception as e:
        return{
            'success': False,
            'data': None, 
            'message': f'Resume parsing failed: {str(e)}'
        }

if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with your resume file
    test_file = "rori.pdf"  # Make sure this file exists
    
    if Path(test_file).exists():
        try:
            print("🔄 Starting to parse resume...")
            result = parser.parse_resume(test_file)
            print("✅ Resume parsed successfully!")
            print("\n" + "="*50)
            print("           📋 RESUME PARSING RESULTS")
            print("="*50)
            
            # Personal Info
            personal_info = result.get('personal_info', {})
            print(f"👤 Name: {personal_info.get('name', 'Not found')}")
            print(f"📧 Email: {personal_info.get('email', 'Not found')}")
            print(f"📱 Phone: {personal_info.get('phone', 'Not found')}")
            print(f"📍 Location: {personal_info.get('location', 'Not found')}")
            
            # Skills - Better formatting
            skills = result.get('skills', [])
            if skills:
                print(f"\n💪 Skills ({len(skills)}):")
                # Group skills into lines of 3-4 for better readability
                for i in range(0, len(skills), 4):
                    skill_group = skills[i:i+4]
                    print(f"   {' | '.join(skill_group)}")
            else:
                print("\n💪 Skills: None found")
            
            # Experience - Cleaner format
            experience = result.get('experience', [])
            if experience:
                print(f"\n💼 Work Experience ({len(experience)}):")
                for i, exp in enumerate(experience, 1):
                    if isinstance(exp, dict):
                        title = exp.get('title', 'Unknown Title')
                        company = exp.get('company', 'Unknown Company')
                        duration = exp.get('duration', 'Duration not specified')
                        
                        print(f"\n   {i}. {title}")
                        print(f"      Company: {company}")
                        print(f"      Duration: {duration}")
                        
                        # Show key responsibilities (limit to 2-3)
                        descriptions = exp.get('description', [])
                        if descriptions:
                            print(f"      Key Responsibilities:")
                            for desc in descriptions[:3]:
                                print(f"        • {desc}")
                            if len(descriptions) > 3:
                                print(f"        • ... and {len(descriptions) - 3} more")
            else:
                print("\n💼 Experience: None found")
            
            # Education - No duplicates
            education = result.get('education', [])
            if education:
                print(f"\n🎓 Education ({len(education)}):")
                for i, edu in enumerate(education, 1):
                    if isinstance(edu, dict):
                        degree = edu.get('degree', 'Unknown Degree')
                        institution = edu.get('institution', 'Unknown Institution')
                        year = edu.get('year', 'Year not specified')
                        
                        print(f"\n   {i}. {degree}")
                        print(f"      Institution: {institution}")
                        print(f"      Year: {year}")
            else:
                print("\n🎓 Education: None found")
            
            # Projects - Better parsing
            projects = result.get('projects', [])
            if projects:
                print(f"\n🚀 Projects ({len(projects)}):")
                for i, project in enumerate(projects, 1):
                    if isinstance(project, dict):
                        name = project.get('name', 'Unknown Project')
                        desc = project.get('description', 'No description')
                        
                        print(f"\n   {i}. {name}")
                        if desc and desc != 'No description available':
                            # Truncate long descriptions
                            if len(desc) > 200:
                                print(f"      {desc[:200]}...")
                            else:
                                print(f"      {desc}")
            else:
                print("\n🚀 Projects: None found")
            
            # Certifications
            certifications = result.get('certifications', [])
            if certifications:
                print(f"\n🏆 Certifications ({len(certifications)}):")
                for cert in certifications:
                    print(f"   • {cert}")
            else:
                print("\n🏆 Certifications: None found")
            
            # Awards  
            awards = result.get('awards', [])
            if awards:
                print(f"\n🏅 Awards & Recognition ({len(awards)}):")
                for award in awards:
                    print(f"   • {award}")
            else:
                print("\n🏅 Awards: None found")
            
            # Metadata
            metadata = result.get('metadata', {})
            print(f"\n📊 Document Info:")
            print(f"   File: {metadata.get('file_name', 'Unknown')}")
            print(f"   Size: {metadata.get('file_size', 0):,} bytes")
            print(f"   Words: {metadata.get('word_count', 0):,}")
            
            print("="*50)
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {e}")
            print("Full traceback:")
            traceback.print_exc()
    else:
        print(f"❌ Test file '{test_file}' not found. Please add a resume file to test.") 