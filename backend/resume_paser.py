from pyresparser import ResumeParser #this is just importing resume parser library

#paser instance 

parser = ResumeParser("resume.pdf") #this is just the file path to my resume
data = parser.get_extracted_data() #this is getting the extracted data from the pdf 
print(data)
