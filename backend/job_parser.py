import re #for text cleaning
import nltk #helps convert text into meaningful words
import torch #used to run BERT
from typing import Dict, List, Tuple
from collections import Counter
from transformers import AutoTokenizer, AutoModel #loads pre-trained BERT models
from sklearn.metrics.pairwise import cosine_similarity #compares how two pieces of texts are similar
import numpy as np #numerical computation






try:
   nltk.data.find('tokenizers/punkt')
   nltk.data.find('corpora/stopwords')
   nltk.data.find('taggers/averaged_perceptron_tagger')
   nltk.data.find('corpora/wordnet')
except LookupError:
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('averaged_perceptron_tagger')
   nltk.download('wordnet')




from nltk.corpus import stopwords #filler words are filtered out
from nltk.tokenize import word_tokenize, sent_tokenize #breaks text into words
from nltk.tag import pos_tag #breaks text into sentences
from nltk.stem import WordNetLemmatizer #running -> run, turns words into their base root
from nltk.chunk import ne_chunk #Named Entity Recognition (NER) using a shallow parser




class AdvancedJobDescriptionParser:
   def __init__(self):
       #initialize nltk componenets
       self.stop_words = set(stopwords.words('english'))
       self.lemmatizer = WordNetLemmatizer()
       #initialize bert model
       self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
       self.bert_model = AutoModel.from_pretrained('bert-base-uncased')


       self.technical_skills = {
           "programming_languages": [
               "python", "java", "javascript", "typescript", "c++", "c#", "php",
               "ruby", "go", "rust", "kotlin", "swift", "scala", "r"
           ],
           "web_technologies": [
               "react", "angular", "vue", "nodejs", "express", "django", "flask",
               "spring", "laravel", "rails", "html", "css", "sass", "bootstrap"
           ],
           "databases": [
               "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
               "oracle", "sqlite", "cassandra", "dynamodb"
           ],
           "cloud_devops": [
               "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
               "terraform", "ansible", "chef", "puppet", "ci/cd"
           ],
           "data_science": [
               "machine learning", "deep learning", "tensorflow", "pytorch",
               "pandas", "numpy", "scikit-learn", "tableau", "power bi"
           ]
       }


       self.soft_skills = [
           "communication", "leadership", "teamwork", "problem solving",
           "analytical thinking", "creativity", "time management", "adaptability",
           "critical thinking", "collaboration", "project management",
           "decision making", "negotiation", "presentation", "mentoring"
       ]
      
       self.experience_patterns = {
           "entry": ["entry level", "junior", "0-1 years", "0-2 years", "new grad",
                    "recent graduate", "trainee", "intern", "associate"],
           "mid": ["mid level", "2-4 years", "3-5 years", "experienced", "regular",
                  "2+ years", "3+ years"],
           "senior": ["senior", "lead", "5+ years", "7+ years", "principal",
                     "manager", "architect", "expert", "specialist", "director"]
       }


       self.responsibility_keywords = {
           "development": ["develop", "build", "create", "implement", "code", "program"],
           "design": ["design", "architect", "plan", "model", "prototype"],
           "management": ["manage", "lead", "supervise", "coordinate", "oversee"],
           "analysis": ["analyze", "research", "investigate", "evaluate", "assess"],
           "collaboration": ["collaborate", "work with", "partner", "coordinate with"]
       }


   def clean_and_preprocess(self, text: str) -> str:
       #enhanced text cleaning and preprocessing
       text = text.lower()


       text = re.sub(r'[^\w\s\-\+\.]', ' ', text) #removed special chars
       text = ' '.join(text.split()) #removes extra whitespace
       return text.strip()


   def extract_keywords_nltk(self, text: str) -> Dict[str, List[str]]:
       tokens = word_tokenize(text)
       filtered_tokens = [
           word for word in tokens
           if word not in self.stop_words and len(word) > 2
       ]


       pos_tags = pos_tag(filtered_tokens)
       nouns = [word for word, pos in pos_tags if pos.startswith('NN')]
       adjectives = [word for word, pos in pos_tags if pos.startswith('JJ')]
       verbs = [word for word, pos in pos_tags if pos.startswith('VB')]


       lemmatized_nouns = [self.lemmatizer.lemmatize(word) for word in nouns]
       lemmatized_verbs = [self.lemmatizer.lemmatize(word, 'v') for word in verbs]


       noun_freq = Counter(lemmatized_nouns).most_common(10)
       verb_freq = Counter(lemmatized_verbs).most_common(10)
       adj_freq = Counter(adjectives).most_common(10)


       return {
           "nouns": [word for word, freq in noun_freq],
           "verbs": [word for word, freq in verb_freq],
           "all keywords": list(set(lemmatized_nouns + lemmatized_verbs + adjectives))
       }
   #This function converts a piece of text into a numerical BERT embedding, which captures the semantic meaning of the sentence.
   # for example, it knows that java and javascript are different things
   def get_bert_embeddings(Self, text: str) -> np.ndarray:
       #get bert embeddings for understanding
       inputs = self.tokenizer(text, return_tensors="pt",max_length = 512,
                               truncation = True, padding= True)
       with torch.no_grad():
           outputs = self.bert_model(**inputs)
      
       embeddings = outputs.last_hidden_state[:, 0, :].numpy()
       return embeddings
   #It uses BERT embeddings to compare the job description to predefined technical skills
   #and see which ones are semantically similar, even if not mentioned word-for-word.
   def semantic_skill_matching(self, text: str) -> Dict[str, List[Tuple[str, float]]]:
       text_embedding = self.get_bert_embeddings(text)
       semantic_matches = {}
       for category, skills in self.technical_skills.items():
           matches = []
           for skill in skills:
               skill_embedding = self.get_bert_embeddings(f"experience with {skill}")
               similarity = cosine_similarity(text_embedding, skill_embedding)[0][0]
               if similarity > 0.7:
                   matches.append((skill, float(similarity)))
           if matches:
               semantic_matches[category] = sorted(matches, key=lambda x: x[1], reverse=True)
       return semantic_matches
  
   def extract_technical_skills(self, text: str) -> Dict[str, List[str]]:
       found_skills = {}
       for category, skills in self.technical_skills.items():
           category_skills = []
           for skill in skills:
               patterns = [
                   rf'\b{re.escape(skill)}\b',
                   rf'{re.escape(skill)}\.js',
                   rf'{re.escape(skill)}\s*(programming|development|framework)',
               ]
               for pattern in patterns:
                   if re.search(pattern, text, re.IGNORECASE):
                       category_skills.append(skill)
                       break
           if category_skills:
               found_skills[category] = list(set(category_skills))
       return found_skills


   def extract_soft_skills(self, text: str) -> List[str]:
       found_soft_skills = []
      
       for skill in self.soft_skills:
           patterns = [
               rf'\b{re.escape(skill)}\b',
               rf'excellent\s+{re.escape(skill)}',
               rf'strong\s+{re.escape(skill)}',
               rf'{re.escape(skill)}\s+skills?',
           ]
          
           for pattern in patterns:
               if re.search(pattern, text, re.IGNORECASE):
                   found_soft_skills.append(skill)
                   break
   def extract_responsibilities(self, text: str) -> Dict[str, List[str]]:
       responsibilities = {}
       sentences = sent_tokenize(text)
      
       for category, keywords in self.responsibility_keywords.items():
           category_responsibilities = []
          
           for sentence in sentences:
               sentence_lower = sentence.lower()
               for keyword in keywords:
                   if keyword in sentence_lower:
                       category_responsibilities.append(sentence.strip())
                       break
          
           if category_responsibilities:
               responsibilities[category] = list(set(category_responsibilities))
      
       return responsibilities


  
   def extract_education_requirements(self, text: str) ->Dict[str, List[str]]:
       education_info = {
           "degrees": [],
           "fields": [],
           "certifications" : []
       }
       degree_patterns = {
           "bachelor": r"bachelor'?s?\s+(?:degree\s+)?(?:in\s+)?(\w+(?:\s+\w+)*)",
           "master": r"master'?s?\s+(?:degree\s+)?(?:in\s+)?(\w+(?:\s+\w+)*)",
           "phd": r"ph\.?d\.?\s+(?:in\s+)?(\w+(?:\s+\w+)*)",
           "associate": r"associate\s+degree\s+(?:in\s+)?(\w+(?:\s+\w+)*)"
       }


       for degree_type, pattern in degree_patterns.items():
           matches = re.findall(pattern, text, re.IGNORECASE)
           if matches:
               education_info["degrees"].append(degree_type)
               education_info["fields"].extend(matches)


       cert_keywords = ["certifications", "certified", "certificate", "license"]
       for keyword in cert_keywords:
           if keyword in text.lower():
               education_info["certifications"].append(keyword)
       return education_info
  
   def analyze_job_complexity(self, parsed_data: Dict) -> str:
       complexity_score = 0
       total_tech_skills = sum(len(skills) for skills in parsed_data.get("technical_skills", {}).values())
       complexity_score += min(total_tech_skills * 2, 20)


       exp_level = parsed_data.get("experience_level", "not specified")
       exp_scores = {"entry": 5, "mid": 10, "senior": 15, "not specified": 0}
       complexity_score += exp_scores.get(exp_level, 0)


       if parsed_data.get("education_requirements", {}).get("degrees"):
           complexity_score += 10


       complexity_score += len(parsed_data.get("soft_skills", [])) * 1


       if complexity_score >= 40:
           return "high"
       elif complexity_score >= 25:
           return "medium"
       else:
           return "low"


   def parse(self, job_description: str) -> Dict:
       print("start job desc parsing")
       clean_text = self.clean_and_preprocess(job_description)
       print("text preprocessing completed")
       nltk_keywords = self.extract_keywords_nltk(clean_text)
       print("nltk keyword extraction completed")
       technical_skills = self.extract_technical_skills(clean_text)
       soft_skills = self.extract_soft_skills(clean_text)   
       print("skills extraction completed")


       try:
           semantic_matches = self.semantic_skill_matching(clean_text)
           print("bert semantic analysis completed")
       except Exception as e:
           print(f"BERT analysis failed: {e}")
           semantic_matches = {}


       experience_level = self.extract_experience_level(clean_text)
       education_requirements = self.extract_education_requirements(clean_text)
       responsibilities = self.extract_responsibilities(job_description)


       parsed_data = {
           "technical_skills": technical_skills,
           "soft_skills": semantic_matches,
           "nltk_keywords": nltk_keywords,
           "experience_level": experience_level,
           "education_requirements": education_requirements,
           "responsibilities": responsibilities,
           "raw_text_length": len(job_description),
           "processed_text_length": len(clean_text),
           "processed": True
       }


       parsed_data["job_complexity"] = self.analyze_job_complexity(parsed_data)
       print("job desc parsing completed successfully")


       return parsed_data


   def extract_experience_level(self, text: str) -> str:
       for level, patterns in self.experience_patterns.items():
           for pattern in patterns:
               if pattern in text:
                   return level
       return "not specified"
  
def test_advanced_parser():
   sample_job = """
   Senior Full Stack Developer - Remote Opportunity
  
   We are seeking an experienced Senior Full Stack Developer to join our innovative team.
  
   Requirements:
   - 5+ years of experience in full-stack web development
   - Expert knowledge of Python, JavaScript, and React
   - Strong experience with Node.js, Django, and PostgreSQL
   - Proficiency with AWS cloud services and Docker containerization
   - Experience with machine learning libraries like TensorFlow or PyTorch
   - Bachelor's degree in Computer Science or related field
   - Excellent communication and leadership skills
   - Strong problem-solving abilities and analytical thinking
  
   Responsibilities:
   - Design and develop scalable web applications using modern frameworks
   - Lead technical discussions and mentor junior developers
   - Collaborate with cross-functional teams to deliver high-quality solutions
   - Implement CI/CD pipelines and manage cloud infrastructure
   - Analyze user requirements and translate them into technical specifications
  
   Preferred Qualifications:
   - Master's degree in Computer Science
   - AWS or Azure certifications
   - Experience with microservices architecture
   - Knowledge of data science and analytics tools
  
   We offer competitive salary, flexible work arrangements, and excellent benefits.
   """
   print("testing advanced job desc parser")
   print("=" * 50)
   parser = AdvancedJobDescriptionParser()
   result = parser.parse(sample_job)


   print("parsing results")
   print("=" * 50)


   print(f"\n🔧 Technical Skills by Category:")
   for category, skills in result['technical_skills'].items():
       print(f"  {category.replace('_', ' ').title()}: {skills}")


   print(f"\n Soft Skills: {result['soft_skills']}")
  
   print(f"\n Experience Level: {result['experience_level']}")
   print(f"\n Education Requirements:")


   for key, value in result['education_requirements'].items():
       if value:
           print(f"  {key.title()}: {value}")
   print(f"\n Responsibilities by Category:")


   for category, resp_list in result['responsibilities'].items():
       print(f"  {category.title()}:")
       for resp in resp_list[:2]:
           print(f"  - {resp[:80]}...")


   print(f"\n NLTK keywords: ")
   print(f" Top Nouns: {result['nltk_keywords']['nouns'][:5]}")
   print(f" Top Verbs: {result['nltk_keywords']['verbs'][:5]}")


   print(f"\n  Job Complexity: {result['job_complexity'].upper()}")


   if result['semantic_matches']:
       print(f"\n  BERT Semantic Matches:")
       for category, matches in result['semantic_matches'].items():
           print(f"  {category}: {[(skill, f'{score:.2f}') for skill, score in matches[:3]]}")


  
if __name__ == "__main__":
   test_advanced_parser()
  


