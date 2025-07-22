from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq
import ssl
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  

class TextSummarizer:
    def __init__(self):
        self.download_nltk_data()
    
    def download_nltk_data(self):
        """Download required NLTK data with error handling."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)
        
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            pass
    
    def summarize_text(self, text, summary_length=3):
        """
        Summarize text using extractive summarization based on word frequency.
        
        Args:
            text (str): The text to summarize
            summary_length (int): Number of sentences in the summary
        
        Returns:
            dict: Dictionary containing summary and statistics
        """
        if not text or not text.strip():
            return {
                'summary': "No text provided for summarization.",
                'original_sentences': 0,
                'summary_sentences': 0,
                'compression_ratio': 0,
                'word_count': 0,
                'error': True
            }
        
        try:
            sentences = sent_tokenize(text)
            original_word_count = len(word_tokenize(text))
            
            if len(sentences) <= summary_length:
                return {
                    'summary': text,
                    'original_sentences': len(sentences),
                    'summary_sentences': len(sentences),
                    'compression_ratio': 100.0,
                    'word_count': original_word_count,
                    'error': False
                }
            
            words = word_tokenize(text.lower())
            
            try:
                stop_words = set(stopwords.words('english'))
            except LookupError:
                logger.warning("Stopwords not found. Using basic stopwords list.")
                stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            
            word_frequencies = {}
            for word in words:
                if word.isalpha() and word not in stop_words:
                    word_frequencies[word] = word_frequencies.get(word, 0) + 1
            
            if not word_frequencies:
                return {
                    'summary': "Unable to generate summary - no valid words found.",
                    'original_sentences': len(sentences),
                    'summary_sentences': 0,
                    'compression_ratio': 0,
                    'word_count': original_word_count,
                    'error': True
                }
            
            max_freq = max(word_frequencies.values())
            for word in word_frequencies:
                word_frequencies[word] = word_frequencies[word] / max_freq
            
            sentence_scores = {}
            for sentence in sentences:
                sentence_words = word_tokenize(sentence.lower())
                score = 0
                word_count = 0
                
                for word in sentence_words:
                    if word in word_frequencies:
                        score += word_frequencies[word]
                        word_count += 1
                
                sentence_word_count = len(sentence.split())
                if 5 <= sentence_word_count <= 30 and word_count > 0:
                    sentence_scores[sentence] = score / word_count
            
            if not sentence_scores:
                for sentence in sentences:
                    sentence_words = word_tokenize(sentence.lower())
                    score = 0
                    for word in sentence_words:
                        if word in word_frequencies:
                            score += word_frequencies[word]
                    if score > 0:
                        sentence_scores[sentence] = score
            
            if not sentence_scores:
                return {
                    'summary': "Unable to generate summary.",
                    'original_sentences': len(sentences),
                    'summary_sentences': 0,
                    'compression_ratio': 0,
                    'word_count': original_word_count,
                    'error': True
                }
            
            actual_summary_length = min(summary_length, len(sentence_scores))
            summary_sentences = heapq.nlargest(actual_summary_length, sentence_scores, key=sentence_scores.get)
            
            original_order_sentences = []
            for sentence in sentences:
                if sentence in summary_sentences:
                    original_order_sentences.append(sentence)
            
            summary = ' '.join(original_order_sentences)
            summary_word_count = len(word_tokenize(summary))
            compression_ratio = (summary_word_count / original_word_count) * 100
            
            return {
                'summary': summary,
                'original_sentences': len(sentences),
                'summary_sentences': len(original_order_sentences),
                'compression_ratio': compression_ratio,
                'word_count': original_word_count,
                'summary_word_count': summary_word_count,
                'error': False
            }
            
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            return {
                'summary': f"Error occurred during summarization: {str(e)}",
                'original_sentences': 0,
                'summary_sentences': 0,
                'compression_ratio': 0,
                'word_count': 0,
                'error': True
            }

summarizer = TextSummarizer()

@app.route('/')
def index():
    """Main page with the summarizer form."""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handle text summarization request."""
    try:
        text = request.form.get('text', '').strip()
        summary_length = int(request.form.get('summary_length', 3))
        
        if not text:
            flash('Please enter some text to summarize.', 'error')
            return redirect(url_for('index'))
        
        if summary_length < 1 or summary_length > 20:
            flash('Summary length must be between 1 and 20 sentences.', 'error')
            return redirect(url_for('index'))
        
        result = summarizer.summarize_text(text, summary_length)
        
        result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['original_text'] = text
        
        if result['error']:
            flash(result['summary'], 'error')
            return redirect(url_for('index'))
        
        return render_template('result.html', result=result)
        
    except ValueError:
        flash('Please enter a valid number for summary length.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in summarize route: {str(e)}")
        flash('An error occurred while processing your request.', 'error')
        return redirect(url_for('index'))

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """API endpoint for text summarization."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        summary_length = data.get('summary_length', 3)
        
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        if summary_length < 1 or summary_length > 20:
            return jsonify({'error': 'Summary length must be between 1 and 20'}), 400
        
        result = summarizer.summarize_text(text, summary_length)
        result['timestamp'] = datetime.now().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in API summarize: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)