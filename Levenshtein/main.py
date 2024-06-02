from Levenshtein import distance as lev
from collections import Counter
import pandas as pd
import nltk as nltk
import re
import math

# regex from https://gist.github.com/gaulinmp/da5825de975ed0ea6a24186434c24fe4
re_stripper_alpha = re.compile('[^a-zA-Z]+')

def similarity_ngrams(a, b):

    matches = [i for i in a if i in b]

    matchesLen = len(matches)

    if(matchesLen == 0):
        return 0.0

    return (len(a) + len(b)) * matchesLen


NGRAM_SIZE = 2

oldTemplateFile = pd.read_csv('/home/marcobertschi/Logram/Logram/Levenshtein/OpenSSHTemplate.csv')
newTemplateFile = pd.read_csv('/home/marcobertschi/Logram/Logram/Levenshtein/OpenSSHTemplate_modified.csv')

merge = pd.merge(oldTemplateFile, newTemplateFile, on=['EventTemplate'], how='right', indicator= True);
print(merge);

newTemplates = merge[merge['_merge'] == 'right_only']
newTemplates.insert(0, 'Matches', 0.0, allow_duplicates=True)
newTemplates.insert(0, 'Levenshtein_Factor', 9999.0, allow_duplicates=True)
newTemplates.insert(0, 'OldTemplate', '', allow_duplicates=True)
print(newTemplates)

for index, row in newTemplates.iterrows():
    print(row['_merge'], ' ', row['EventTemplate'])
    ngramNew = list(nltk.ngrams(re_stripper_alpha.sub(' ', row['EventTemplate']).split(), NGRAM_SIZE))
    levenshtein_factor = 999999;
    similarity = 0.0
    for indexOldTemplate, rowOldTemplate in oldTemplateFile.iterrows():
        levenshtein = lev(row[0], rowOldTemplate[0]);
        size_diff = (len(rowOldTemplate[0]) - len(row[0])) + -1
        new_levenshtein_factor = levenshtein * size_diff
        ngramOld = list(nltk.ngrams(re_stripper_alpha.sub(' ', rowOldTemplate[0]).split(), NGRAM_SIZE))

        newSimilarity = similarity_ngrams(ngramNew,ngramOld)

        if(new_levenshtein_factor < levenshtein_factor and levenshtein != len(rowOldTemplate[0])):
            print('Edit Distance (Lev / Len Factor), new best match: ', new_levenshtein_factor, ' (was old template) :', rowOldTemplate[0]);
            levenshtein_factor = new_levenshtein_factor
            newTemplates._set_value(index, 'Levenshtein_Factor', new_levenshtein_factor);
            newTemplates._set_value(index, 'OldTemplate', rowOldTemplate[0]);
            newTemplates._set_value(index, 'Matches', 0.0);

        if(newSimilarity > similarity):
            newTemplates._set_value(index, 'Levenshtein_Factor', 0.0);
            newTemplates._set_value(index, 'OldTemplate', rowOldTemplate[0]);
            newTemplates._set_value(index, 'Matches', newSimilarity);



print(newTemplates);

