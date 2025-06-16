import re
from typing import Dict, List
class JobDescriptionParser:
    def __init__(self):
        self.technical_skills = [
            "python", "java", "javascript", "react", "angular", "vue", 
            "nodejs", "sql", "mongodb", "postgresql", "mysql", "aws", 
            "azure", "docker", "git", "html", "css", "flask", "django"
        ]

        self.soft_skills = [
            "communication", "leadership", "teamwork", "problem solving",
            "analytical", "creative", "organized", "time management"
        ]

        self.experience_patterns = {
            "entry": ["entry level", "junior", "0-1 years", "0-2 years", "new grad", "recent graduate"],
            "mid": ["mid level", "2-4 years", "3-5 years", "experienced"],
            "senior": ["senior", "lead", "5+ years", "7+ years", "principal", "manager"]
        }
        pass
    
    def clean_text(self, text: str) -> str:
        #cleaning job description pasted
        text = text.lower()
        text = ' '.join(text.split())

        return text.strip()

    def extract_skills(self, text: str) -> str:
        found_skills = {
            "technical": [],
            "soft": []
        }

        #looking for technical and soft skills that are mentioned in job desc
        for skill in self.technical_skills:
            #regex pattern to match skill as whole word
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_skills["technical"].append(skill)
        
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_skills["soft"].append(skill)
        return found_skills

    def extract_experience_level(self, text: str) -> str:
        for level, patterns in self.experience_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return level
        return "not specified"

    def extract_education(self, text: str) -> List[str]:
        education_found = []
        education_keywords = [
            "bachelor", "master", "phd", "degree", "diploma", 
            "certification", "associate degree", "high school"
        ]
        for keyword in education_keywords:
            if keyword in text:
                education_found.append(keyword)
        return education_found
    
    def parse(self, job_description: str) -> Dict:
        #clean text
        clean_text = self.clean_text(job_description)
        #extract info from job description
        skills = self.extract_skills(clean_text)
        experience = self.extract_experience_level(clean_text)
        education = self.extract_education(clean_text)

        return {
        "skills": skills,
        "experience_level": experience,
        "education_requirements": education,
        "raw_text_length": len(job_description),
        "processed": True
        }

def test_parser():
    # Sample job description for testing
    sample_job = """
    We are looking for a Senior Python Developer to join our team.
    
    Requirements:
    - 5+ years of experience in Python development
    - Strong knowledge of Flask, Django, and SQL
    - Experience with AWS and Docker
    - Bachelor's degree in Computer Science
    - Excellent communication and problem solving skills
    - Leadership experience preferred
    
    Responsibilities:
    - Develop web applications using Python and React
    - Work with databases like PostgreSQL
    - Collaborate with the team and provide technical leadership
    
    Apply now! We are an equal opportunity employer.
    """

    parser = JobDescriptionParser()
    result = parser.parse(sample_job)
    print("Parsing result:")
    print(f"Technical Skills Found: {result['skills']['technical']}")
    print(f"Soft Skills Found: {result['skills']['soft']}")
    print(f"Experience Level: {result['experience_level']}")
    print(f"Education Requirements: {result['education_requirements']}")
if __name__ == "__main__":
    test_parser()





