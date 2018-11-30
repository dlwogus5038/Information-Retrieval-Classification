from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()
str = '我不是'
str1 = str.encode('utf-8')
str1 = str1.decode('utf-8')
str2 = 'application'
#str3 = str2.encode('utf-8')
print(porter_stemmer.stem(str))
print(porter_stemmer.stem(str1))
print(porter_stemmer.stem(str2))
#print(porter_stemmer.stem(str3))
