import pandas as pd
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle


# Download NLTK data with error handling
def ensure_nltk_data():
    packages = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
    for package in packages:
        try:
            if package == 'punkt':
                nltk.data.find('tokenizers/punkt')
            elif package in ['stopwords', 'wordnet', 'omw-1.4']:
                nltk.data.find(f'corpora/{package}')
        except LookupError:
            nltk.download(package, quiet=True)

ensure_nltk_data()


ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()


def transform_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    
    # Try NLTK tokenizer, fallback to simple split
    try:
        tokens = nltk.word_tokenize(text)
    except LookupError:
        # If punkt data is missing, download and retry
        nltk.download('punkt', quiet=True)
        try:
            tokens = nltk.word_tokenize(text)
        except:
            # Final fallback: simple split
            tokens = text.split()

    # keep alphanumeric tokens
    toks = [t for t in tokens if t.isalnum()]

    # remove stopwords and punctuation
    toks = [t for t in toks if t not in stopwords.words('english') and t not in string.punctuation]

    # lemmatize then stem
    out = [ps.stem(lemmatizer.lemmatize(t)) for t in toks]
    return " ".join(out)


def main():
    print('Loading dataset...')
    df = pd.read_csv('sms-spam.csv', encoding='latin-1', usecols=[0,1], names=['label','text'], header=0)
    print('Total rows:', len(df))

    df['text'] = df['text'].fillna('')
    print('Preprocessing texts (this may take a minute)...')
    df['clean'] = df['text'].apply(transform_text)

    # label mapping: spam -> 1, ham -> 0
    df['y'] = df['label'].map(lambda x: 1 if str(x).strip().lower() == 'spam' else 0)

    X = df['clean'].tolist()
    y = df['y'].values

    print('Creating TF-IDF vectorizer with ngram_range=(1,2) and fitting...')
    vec = TfidfVectorizer(ngram_range=(1,2), max_features=20000)
    X_vec = vec.fit_transform(X)

    print('Training MultinomialNB...')
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42, stratify=y)
    clf = MultinomialNB()
    clf.fit(X_train, y_train)

    print('Evaluating on test set...')
    preds = clf.predict(X_test)
    print('Accuracy:', accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))

    # Save vectorizer and model
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vec, f)
    with open('model.pkl', 'wb') as f:
        pickle.dump(clf, f)

        # Save metrics to a JSON file so the backend/frontend can show performance
        metrics = {
            'accuracy': accuracy_score(y_test, preds),
            'classification_report': classification_report(y_test, preds, output_dict=True)
        }
        import json
        with open('metrics.json', 'w') as fh:
            json.dump(metrics, fh, indent=2)

        print('Saved vectorizer.pkl and model.pkl')
        print('Saved metrics.json')


if __name__ == '__main__':
    main()
