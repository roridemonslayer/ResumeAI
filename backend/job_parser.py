import re
import nltk
import torch
from typing import Dict, List, Tuple
from collections import Counter
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np