from pyresparser import ResumeParser

data = ResumeParser("resume.pdf").get_extracted_data() # this gets the file path and extracts the date


print(data)
