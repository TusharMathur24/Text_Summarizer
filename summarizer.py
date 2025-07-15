import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab') 

def summarize_text(text, summary_length=3):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    stop_words = set(stopwords.words('english'))
    word_frequencies = {}
    for word in words:
        if word.isalpha() and word not in stop_words:
            word_frequencies[word] = word_frequencies.get(word, 0) + 1

    max_freq = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_freq

    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if len(sentence.split(' ')) < 30:
                    sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word]

    summary_sentences = heapq.nlargest(summary_length, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    
    return summary

if __name__ == "__main__":
    print("=== TEXT SUMMARIZER ===")
    input_text = input("\nEnter the text you want to summarize:\n\n")
    summary = summarize_text(input_text, summary_length=3)
    print("\n=== SUMMARY ===")
    print(summary)