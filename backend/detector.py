import re
import math
import logging
from typing import List, Dict, Tuple
import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline
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
        logger.info(f"Loading models on device: {self.device}")
        
        try:
            # Load GPT-2 tokenizer and model
            logger.info("Loading GPT-2 model and tokenizer...")
            self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            self.model = GPT2LMHeadModel.from_pretrained('gpt2').to(self.device)
            self.model.eval()
            logger.info("✓ GPT-2 model loaded")
        except Exception as e:
            logger.error(f"Failed to load GPT-2 model: {str(e)}")
            raise e
        
        try:
            # Load RoBERTa OpenAI Detector (detects GPT-generated text)
            logger.info("Loading RoBERTa GPT-2 detector...")
            self.gpt_detector = pipeline(
                "text-classification",
                model="openai-community/roberta-base-openai-detector",
                device=0 if self.device == "cuda" else -1
            )
            logger.info("✓ RoBERTa detector loaded")
            self.roberta_available = True
        except Exception as e:
            logger.warning(f"RoBERTa detector not available: {e}")
            self.roberta_available = False
        
        try:
            # Load sentiment analyzer (detects tone inconsistencies)
            logger.info("Loading sentiment analyzer...")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if self.device == "cuda" else -1
            )
            logger.info("✓ Sentiment analyzer loaded")
            self.sentiment_available = True
        except Exception as e:
            logger.warning(f"Sentiment analyzer not available: {e}")
            self.sentiment_available = False

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

        # Add Hugging Face model scores to ensemble
        scores = [ppl_score, burst_score, ent_score]
        
        # RoBERTa GPT detector (optional, if available)
        roberta_score = self.roberta_gpt_detection(p_text)
        if self.roberta_available:
            scores.append(roberta_score)
        
        # Sentiment consistency score (optional, if available)
        sentences = [s.strip() for s in p_text.split('.') if s.strip()]
        sentiment_score = self.sentiment_consistency_score(sentences)
        if self.sentiment_available:
            # Invert sentiment score (high consistency = low AI score)
            scores.append(1.0 - sentiment_score)
        
        # Ensemble Score (weighted average)
        # Statistical methods: 60% weight (proven across all LLMs)
        # HuggingFace models: 40% weight (better for GPT detection)
        stat_ensemble = (ppl_score + burst_score + ent_score) / 3.0
        
        if len(scores) > 3:
            # Include HF models
            hf_ensemble = sum(scores[3:]) / (len(scores) - 3)
            ensemble = (stat_ensemble * 0.6) + (hf_ensemble * 0.4)
        else:
            ensemble = stat_ensemble
        
        ai_percentage = round(ensemble * 100)

        # Confidence calculation (based on variance of individual indicators)
        mean_score = sum(scores) / len(scores)
        var_score = sum((s - mean_score) ** 2 for s in scores) / len(scores)
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

        result = {
            "text": paragraph,
            "ai_score": ai_percentage,
            "confidence": confidence,
            "metrics": {
                "perplexity": round(ppl_score, 4),
                "burstiness": round(burst_score, 4),
                "entropy": round(ent_score, 4),
            },
            "flag": flag,
            "models_used": {
                "statistical": True,
                "roberta": self.roberta_available,
                "sentiment": self.sentiment_available
            }
        }
        
        # Add HF scores if available
        if self.roberta_available:
            result["metrics"]["roberta_score"] = round(roberta_score, 4)
        if self.sentiment_available:
            result["metrics"]["sentiment_consistency"] = round(sentiment_score, 4)
        
        return result

    def roberta_gpt_detection(self, text: str) -> float:
        """
        Use RoBERTa model to detect GPT-generated text.
        Returns score between 0-1 (higher = more likely AI).
        """
        if not self.roberta_available or not text.strip():
            return 0.5
        
        try:
            # Truncate to max tokens (512 for RoBERTa)
            text = text[:512]
            result = self.gpt_detector(text)[0]
            
            # Result format: {"label": "Fake" or "Real", "score": float}
            if result["label"] == "Fake":
                return min(result["score"], 1.0)
            else:
                return 1.0 - min(result["score"], 1.0)
        except Exception as e:
            logger.warning(f"RoBERTa detection error: {e}")
            return 0.5
    
    def sentiment_consistency_score(self, sentences: List[str]) -> float:
        """
        Analyze sentiment consistency across sentences.
        AI text often has abrupt tone shifts (humanizers create unnatural transitions).
        Returns score 0-1 (higher = more consistent/likely human).
        """
        if not self.sentiment_available or len(sentences) < 2:
            return 0.5
        
        try:
            sentiments = []
            for sent in sentences[:10]:  # Analyze first 10 sentences
                if sent.strip():
                    result = self.sentiment_pipeline(sent[:512])[0]
                    # Normalize sentiment score
                    if result["label"] == "POSITIVE":
                        sentiments.append(result["score"])
                    else:
                        sentiments.append(1.0 - result["score"])
            
            if len(sentiments) < 2:
                return 0.5
            
            # Calculate standard deviation of sentiments
            # Lower std = more consistent (more human-like)
            std_dev = np.std(sentiments)
            
            # Convert to human-likelihood score (lower std = higher score)
            consistency = 1.0 - min(std_dev, 1.0)
            return consistency
        except Exception as e:
            logger.warning(f"Sentiment analysis error: {e}")
            return 0.5

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
