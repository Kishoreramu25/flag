import re
import math
import logging
from typing import List, Dict
import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import textstat
import nltk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIContentDetector")

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except Exception as e:
        logger.warning(f"Failed to download NLTK punkt resource: {e}")

class AIContentDetector:
    def __init__(self):
        # Force CPU if CUDA execution is not needed or fails, fallback to CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading GPT-2 model and tokenizer on device: {self.device}")
        
        try:
            # Load tokenizer and model once at startup
            # Using float32 precision for precision and CPU compatibility
            self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            self.model = GPT2LMHeadModel.from_pretrained('gpt2').to(self.device)
            self.model.eval()  # Set model to evaluation mode
            logger.info("GPT-2 model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load GPT-2 model: {str(e)}")
            raise e

    def calculate_perplexity(self, text: str) -> float:
        """
        Calculate perplexity of a given text block using GPT-2.
        AI text has LOWER perplexity.
        """
        if not text.strip():
            return 0.0

        try:
            # Tokenize text
            inputs = self.tokenizer(text, return_tensors='pt')
            input_ids = inputs['input_ids'].to(self.device)
            
            # GPT-2 token limit limit is 1024
            if input_ids.size(1) > 1022:
                input_ids = input_ids[:, :1022]

            # We need at least 2 tokens to evaluate perplexity
            if input_ids.size(1) <= 1:
                return 0.0

            with torch.no_grad():
                outputs = self.model(input_ids, labels=input_ids)
                loss = outputs.loss  # Average Cross-Entropy loss
                perplexity = torch.exp(loss).item()
                
            # Keep perplexity bounded
            if math.isnan(perplexity) or math.isinf(perplexity):
                return 150.0  # Fallback to high perplexity (human-like)
                
            return perplexity
        except Exception as e:
            logger.error(f"Error calculating perplexity: {str(e)}")
            return 150.0  # Fallback to high perplexity (human-like)

    def calculate_burstiness(self, text: str) -> float:
        """
        Calculate sentence length variation (Coefficient of Variation).
        Human text has high burstiness (varied lengths).
        AI text has low burstiness (uniform lengths).
        """
        if not text.strip():
            return 0.0

        try:
            # Tokenize sentences using NLTK, fallback to regex if it fails
            try:
                sentences = nltk.sent_tokenize(text)
            except Exception:
                sentences = re.split(r'(?<=[.!?])\s+', text)
                
            sentences = [s.strip() for s in sentences if s.strip()]
            if not sentences:
                return 0.0

            # Count words per sentence
            lens = []
            for s in sentences:
                words = s.split()
                if words:
                    lens.append(len(words))

            if not lens:
                return 0.0

            mean = sum(lens) / len(lens)
            if mean == 0:
                return 0.0

            # Calculate standard deviation
            variance = sum((x - mean) ** 2 for x in lens) / len(lens)
            std_dev = math.sqrt(variance)
            
            # Coefficient of Variation
            cv = std_dev / mean
            return cv
        except Exception as e:
            logger.error(f"Error calculating burstiness: {str(e)}")
            return 0.8  # Fallback to high burstiness (human-like)

    def calculate_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy of the vocabulary choices.
        AI text has lower entropy (more predictable vocabulary).
        """
        if not text.strip():
            return 0.0

        try:
            # Tokenize words, fallback to regex if NLTK fails
            try:
                words = nltk.word_tokenize(text.lower())
            except Exception:
                words = re.findall(r'\b\w+\b', text.lower())

            # Filter punctuation
            words = [w for w in words if w.isalnum()]
            total_words = len(words)
            if total_words == 0:
                return 0.0

            # Count frequencies
            from collections import Counter
            counts = Counter(words)
            
            # Shannon entropy calculation
            entropy = 0.0
            for count in counts.values():
                p = count / total_words
                entropy -= p * math.log2(p)
                
            return entropy
        except Exception as e:
            logger.error(f"Error calculating entropy: {str(e)}")
            return 5.0  # Fallback to moderate entropy

    def analyze_paragraph(self, paragraph: str) -> Dict[str, any]:
        """
        Analyzes a single paragraph and returns perplexity, burstiness,
        entropy, and overall aggregated ensemble score.
        """
        p_text = paragraph.strip()
        if not p_text or len(p_text.split()) < 5:
            # Return neutral empty score for very short paragraphs
            return {
                "text": paragraph,
                "ai_score": 0.0,
                "confidence": 100.0,
                "perplexity_score": 0.0,
                "burstiness_score": 0.0,
                "entropy_score": 0.0,
                "flag": "Very Low"
            }

        # Calculate raw statistics
        perplexity = self.calculate_perplexity(p_text)
        cv = self.calculate_burstiness(p_text)
        entropy = self.calculate_entropy(p_text)

        # Normalize raw values into AI likelihood scores (0 to 1)
        
        # 1. Perplexity Normalization (Log scale from 10.0 to 150.0)
        min_ppl, max_ppl = 10.0, 150.0
        if perplexity <= min_ppl:
            ppl_score = 1.0
        elif perplexity >= max_ppl:
            ppl_score = 0.0
        else:
            ppl_score = 1.0 - (math.log(perplexity) - math.log(min_ppl)) / (math.log(max_ppl) - math.log(min_ppl))

        # 2. Burstiness Normalization (CV scale from 0.1 to 0.9)
        # Uniform length (low CV) = High AI score (1.0)
        # Varied length (high CV) = Low AI score (0.0)
        min_cv, max_cv = 0.1, 0.9
        if cv <= min_cv:
            burst_score = 1.0
        elif cv >= max_cv:
            burst_score = 0.0
        else:
            burst_score = 1.0 - (cv - min_cv) / (max_cv - min_cv)

        # 3. Entropy Normalization (Ratio of actual vs max possible entropy)
        # Max possible entropy is when all words are unique
        word_count = len(p_text.split())
        max_possible_entropy = math.log2(word_count) if word_count > 1 else 1.0
        norm_ent = entropy / max_possible_entropy if max_possible_entropy > 0 else 1.0
        
        # Scale between 0.65 (repetitive, AI) and 0.92 (rich, Human)
        min_ent, max_ent = 0.65, 0.92
        if norm_ent <= min_ent:
            ent_score = 1.0
        elif norm_ent >= max_ent:
            ent_score = 0.0
        else:
            ent_score = 1.0 - (norm_ent - min_ent) / (max_ent - min_ent)

        # Ensemble Score (average of the three normalized indicators)
        ensemble = (ppl_score + burst_score + ent_score) / 3.0
        ai_percentage = round(ensemble * 100)

        # Confidence calculation (base on variance of individual indicators)
        scores = [ppl_score, burst_score, ent_score]
        mean_score = sum(scores) / 3.0
        var_score = sum((s - mean_score) ** 2 for s in scores) / 3.0
        std_dev = math.sqrt(var_score)
        
        # 100 if all agree, decreases if they disagree
        confidence = round(100.0 - (std_dev * 20.0))
        confidence = max(50, min(100, confidence))

        # Flag assignment
        if ai_percentage <= 20:
            flag = "Very Low"
        elif ai_percentage <= 40:
            flag = "Low"
        elif ai_percentage <= 60:
            flag = "Medium"
        elif ai_percentage <= 80:
            flag = "High"
        else:
            flag = "Very High"

        return {
            "text": paragraph,
            "ai_score": ai_percentage,
            "confidence": confidence,
            "perplexity_score": round(ppl_score, 4),
            "burstiness_score": round(burst_score, 4),
            "entropy_score": round(ent_score, 4),
            "flag": flag
        }

    def analyze_document(self, paragraphs: List[str]) -> Dict[str, any]:
        """
        Analyzes a document paragraph-by-paragraph, and returns aggregated metrics.
        """
        if not paragraphs:
            return {
                "overall_ai_percentage": 0,
                "confidence": 100,
                "word_count": 0,
                "ai_words": 0,
                "paragraphs": []
            }

        paragraph_analyses = []
        total_weighted_ai_score = 0.0
        total_words = 0
        ai_words_estimate = 0.0

        for p in paragraphs:
            p_words = len(p.split())
            if p_words == 0:
                continue
            
            analysis = self.analyze_paragraph(p)
            paragraph_analyses.append(analysis)
            
            total_words += p_words
            total_weighted_ai_score += analysis["ai_score"] * p_words
            # Estimate of words that might be AI-generated
            ai_words_estimate += (analysis["ai_score"] / 100.0) * p_words

        if total_words == 0:
            return {
                "overall_ai_percentage": 0,
                "confidence": 100,
                "word_count": 0,
                "ai_words": 0,
                "paragraphs": []
            }

        overall_ai_percentage = round(total_weighted_ai_score / total_words)
        
        # Aggregate confidence as average of paragraph confidences
        avg_confidence = round(sum(p["confidence"] for p in paragraph_analyses) / len(paragraph_analyses)) if paragraph_analyses else 100

        return {
            "overall_ai_percentage": overall_ai_percentage,
            "confidence": avg_confidence,
            "word_count": total_words,
            "ai_words": round(ai_words_estimate),
            "paragraphs": paragraph_analyses
        }
