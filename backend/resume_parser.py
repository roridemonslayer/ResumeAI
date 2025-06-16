from pyresparser import ResumeParser

data = ResumeParser("resume.pdf").get_extracted_data() # this gets the file path and extracts the date

print("=== EXTRACTED DATA ===")
print(data)

if __name__ ==  "__main__":
    test_resume_parsing()

print("Hello")