from sklearn.metrics import confusion_matrix
import pandas as pd
import pickle as pi
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import re
import nltk
from nltk.stem.porter import PorterStemmer
from bs4 import BeautifulSoup
import unicodedata
import inflect
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, GridSearchCV

missing_values = ["no info", ".", "n/a", "na", "--", "N/A", "NA", "??", "?"]
df = pd.read_csv('C:/Users/atwiine/PycharmProjects/finalyearproject/man.csv', encoding='latin', sep=',', delimiter=None, header=0,
                 index_col=None, squeeze=False, engine='python', usecols=range(0, 3),na_values=missing_values)

df.columns = ['Post', 'Comment', 'Sentiment']
df['Post'].fillna(method="ffill", inplace=True)
df['Comment'].fillna(method="ffill", inplace=True)
df['Sentiment'].fillna(method="ffill", inplace=True)

#######
stemmer = PorterStemmer()


def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def remove_between_square_brackets(text):
    return re.sub('\[[^]]*\]', '', text)


def denoise_text(text):
    text = strip_html(text)
    text = remove_between_square_brackets(text)
    return text


def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words


def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words


def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words


def decontracted(Post):
    # specific
    Post = re.sub(r"won\'t", "will not", Post)
    Post = re.sub(r"can\'t", "can not",  Post)
    Post = re.sub(r"can\'t", "shall not",  Post)
    Post = re.sub(r"wont", "will not",  Post)
    Post = re.sub(r"cant", "can not",  Post)
    Post = re.sub(r"shant", "shall not",  Post)

    # general
    Post = re.sub(r"n\'t", " not",  Post)
    Post = re.sub(r"nt", " not",  Post)
    Post = re.sub(r"\'re", " are",  Post)
    Post = re.sub(r"\'s", " is",  Post)
    Post = re.sub(r"\'d", " would",  Post)
    Post = re.sub(r"\'ll", " will",  Post)
    Post = re.sub(r"\'t", " not", Post)
    Post = re.sub(r"\'ve", " have",  Post)
    Post = re.sub(r"\'m", " am",  Post)
    Post = re.sub(r"ur", " your",  Post)
    Post = re.sub(r"y\'", " you",  Post)
    Post = re.sub(r"luv", " love",  Post)
    Post = re.sub(r"2", "too",  Post)
    Post = re.sub(r"bac", "back",  Post)
    return Post


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def tokenize(Post):
    Post = decontracted(Post)
    Post = denoise_text(Post)
    # remove non letters
    Post = re.sub("[^a-zA-Z]", " ", Post)
    # tokenize
    tokens = nltk.word_tokenize(Post)
    tokens = remove_non_ascii(tokens)
    tokens = remove_punctuation(tokens)
    tokens = replace_numbers(tokens)
    # stem
    stems = stem_tokens(tokens, stemmer)
    return stems


def de_contracted(Comment):
    # specific
    Comment = re.sub(r"won\'t", "will not", Comment)
    Comment = re.sub(r"can\'t", "can not",  Comment)
    Comment = re.sub(r"shan\'t", "shall not",  Comment)
    Comment = re.sub(r"wont", "will not",  Comment)
    Comment = re.sub(r"cant", "can not",  Comment)
    Comment = re.sub(r"shant", "shall not",  Comment)




    # general
    Comment = re.sub(r"n\'t", " not",  Comment)
    Comment = re.sub(r"nt", " not",  Comment)
    Comment = re.sub(r"\'re", " are",  Comment)
    Comment = re.sub(r"\'s", " is",  Comment)
    Comment = re.sub(r"\'d", " would",  Comment)
    Comment = re.sub(r"\'ll", " will",  Comment)
    Comment = re.sub(r"\'t", " not", Comment)
    Comment = re.sub(r"\'ve", " have",  Comment)
    Comment = re.sub(r"\'m", " am",  Comment)
    Comment = re.sub(r"ur", " your",  Comment)
    Comment = re.sub(r"y\'", " you",  Comment)
    Comment = re.sub(r"luv", " love",  Comment)
    Comment = re.sub(r"2", "too",  Comment)
    Comment = re.sub(r"bac", "back",  Comment)
    return Comment


def stem_token(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def tokeniz(Comment):
    Comment = decontracted(Comment)
    Comment = denoise_text(Comment)
    # remove non letters
    Comment = re.sub("[^a-zA-Z]", " ", Comment)
    # tokenize
    tokens = nltk.word_tokenize(Comment)
    tokens = remove_non_ascii(tokens)
    tokens = remove_punctuation(tokens)
    tokens = replace_numbers(tokens)
    # stem
    stems = stem_tokens(tokens, stemmer)
    return stems


def Post(X):
    return X.iloc[:, 0].values.astype('U')


def Comment(X):
    return X.iloc[:, 1].values.astype('U')


# pipeline to get all tfidf and word count for first column
pipeline_one = Pipeline([
    ('column_selection', FunctionTransformer(Post, validate=False)),
    ('feature-extractors', FeatureUnion([('tfidf', TfidfVectorizer()),
                                        ('counts', CountVectorizer(analyzer='word', tokenizer=tokenize, lowercase=True,
                                                                   stop_words='english', token_pattern=r'\w{1,}',
                                                                   max_features=1200))]))])

# Then a second pipeline to do the same for the second column
pipeline_two = Pipeline([
    ('column_selection', FunctionTransformer(Comment, validate=False)),
    ('feature-extractors', FeatureUnion([('tfidf', TfidfVectorizer()),
                                        ('counts', CountVectorizer(analyzer='word', tokenizer=tokeniz, lowercase=True,
                                                                   stop_words='english', token_pattern=r'\w{1,}',
                                                                   max_features=1200))]))])


# Then you would again feature union these pipelines
# to get different feature selection for each column
final_transformer = FeatureUnion([('first-column-features', pipeline_one),
                                  ('second-column-feature', pipeline_two)])

# Your dataframe has your target as the first column, so make sure to drop first
y = df['Sentiment']
#print(y)
df = df.drop('Sentiment', axis=1)

# Now fit transform should work
features = final_transformer.fit_transform(df)

X_train, X_test, y_train, y_test = train_test_split(features, y, train_size=0.67, test_size=0.33, random_state=1234)

nb = MultinomialNB(alpha=6, class_prior=None, fit_prior=None)
nb = nb.fit(X=X_train, y=y_train)
y_pred = nb.predict(X_test)

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

# train classifier

nb = MultinomialNB(alpha=6, class_prior=None, fit_prior=None)
nb = nb.fit(X=features, y=y)

#Save the model

filename = 'naive_model.sav'
pi.dump(nb, open(filename, 'wb'))


#load the model from the disk
loaded_model = pi.load(open(filename, 'rb'))
result = loaded_model.score(X_test, y_test)
print(result)
