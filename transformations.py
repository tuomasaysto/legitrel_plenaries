# -*- coding: utf-8 -*-
#@author: Tuomas Äystö

import re
from string import ascii_lowercase
from langdetect import detect
import pandas as pd



# Find date from the plenary document
def find_date(x, y):
 
    # convetion changes in 2015        
    # if the year is >= 2015
    if y >= 2015:    
        t = "nimenhuuto"
        x = x.split(t, 1)[0]
    
    # if the year is 2010-2014
    if y <= 2014:    
        t = "päiväjärjestys"
        x = x.split(t, 1)[0]

    # find weekday
    weekdays = ["maanantai", "tiistai", "keskiviikko", "torstai", "perjantai", "lauantai", "sunnuntai"]
    
    for i in weekdays:
        if x.find(i) != -1:
            a = x.index(i)
            break
    
    # find day number
    b = x[a:]
    for i, c in enumerate(b):
        if c.isdigit():
            
            day = b[i]  
            day_idx = i
            
            if b[i+1] == ".":
                    break
            
            if (b[i+1]).isdigit():
                day += b[i+1]
                day_idx = i+1
                break
    
    # find month (for years 2010-2014)
    month_names = ["tammikuu", "helmikuu", "maaliskuu", "huhtikuu", "toukokuu", "kesäkuu", "heinäkuu", "elokuu", "syyskuu", "lokakuu", "marraskuu", "joulukuu"]
    month = ""
    
    # years 2010-2020
    if y <= 2014:
    
        x = x[:500]
        
        for i, c in enumerate(month_names):
            if x.find(c) != -1:
                month = str(i+1)

                break
    
    # find month (for years 2015-2020)
    e = b[day_idx:]
    
    if y >= 2015:
        for i, c in enumerate(e):
            if c == ".":
                month = e[i+1]
                
                if e[i+2] == ".":
                    break
                            
                if (e[i+2]).isdigit():    
                    month += e[i+2]
                    break
            
    # combine the above into YYMMDD -date
    if len(day) < 2:
        day = "0"+day

    if len(month) < 2:
        month = "0"+month
    
    yr = str(y)
    yr = yr[2:]
    pvm = yr+month+day
    
    return int(pvm)


# Abreviations in Finnish, that are written with a dot
abreviations = open('lookups/lyhenteet.txt', encoding='utf-8').read()
abreviations = list(abreviations.split(" "))
abreviations = [i +"." for i in abreviations]

# Replace dots with commas, if they are between numbers (helps with parsing)
def remove_dots_between_nmbrs(x):
    
    for idx, i in enumerate(x):
        if(idx<(len(x)-1)): 
            if x[idx] == ".":
                 if (x[idx-1]).isnumeric() == True:
                     if (x[idx+1]).isnumeric() == True:    
                        x = x[:idx] + "," + x[idx+1:]
            
    return x


# Remove the unnecessary beginning of the document (years 2010-2014)
def remove_leadup(x):

    if x.find("päiväjärjestyksen asiat:") != -1:
        x = x[x.find("päiväjärjestyksen asiat:"):]
        return x
 
    if x.find("ulkopuolella päiväjärjestyksen esiteltävät asiat") != -1:
        x = x[x.find("ulkopuolella päiväjärjestyksen esiteltävät asiat"):]
        return x
    
    else:
        return x
        

# Remove the unnecessary beginning of the document (2015-2020)
def remove_leadup_2(x):
    x = x[x.find("nimenhuuto"):]
    
    if x.find("nimenhuuto") != -1:
       
        return x


# Remove speech interjections (text in parantheses by document convention)
def del_text_in_parenthesis(text, brackets="()"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []

    for character in text:
        for i, b in enumerate(brackets):
            if character == b: 
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close
                if count[kind] < 0: 
                    count[kind] = 0  
                else:  
                    break
        else: 
            if not any(count):
                saved_chars.append(character)
    return ''.join(saved_chars)

def del_text_in_brackets(text, brackets="[]"):
    count = [0] * (len(brackets) // 2)
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b:
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close 
                if count[kind] < 0: 
                    count[kind] = 0 
                else:  
                    break
        else: 
            if not any(count):
                saved_chars.append(character)
    return ''.join(saved_chars)



# Remove swedish language sentences
def remove_swe(x):
    y = 0
    for inx, i in enumerate(x):
        try:
            if detect(i) == "sv":
                if "talman" not in i and "östman" not in i:  # Speech starts, don't remove
                    x[inx] = ""
                    y += 1
        except:
            continue

    x = list(filter(None, x))
    return x, y


# Text preprocessing and tokenization. y = year.
def preprocessing(text, y):
    
    text = text + "."    # dot at the end
    
    text = text.replace("-\n","")   # remove line changes with a dash
    
    text = text.replace("\n"," ")    # remove line changes
   
    # remove consequtive .!? punctuation
    text = re.sub(r'(\.)\1+', r'\1', text)
    text = re.sub(r'(\!)\1+', r'\1', text)
    text = re.sub(r'(\?)\1+', r'\1', text)
                
    # remove lonely letters
    letters = []
    for i in ascii_lowercase:
        letters.append(i)
        letters.append(i+".")
    
    letters.extend(["å", "å.", "ä", "ä.", "ö", "ö."])
    
    wordlist = text.split()
    wordlist2 = []
    for i in wordlist:
        if i not in letters:
            wordlist2.append(i)
    
    text = ' '.join(wordlist2)

    # remove dots between numbers
    text = remove_dots_between_nmbrs(text)
   
    # Add <split> to mark the locations where sentences should be split
    wordlist = text.split()
    wordlist2 = []

    for index, elem in enumerate(wordlist):
       
        if(index<(len(wordlist)-1)): 
        
            # Ignore abreviations with a dot
            if elem not in abreviations:
                elem = elem.replace(".",".<split>")    
                wordlist2.append(elem)
                
            # Don't ignore abreviations, if they end a sentence    
            elif elem in abreviations:

                a = wordlist[index+1]
                if a[0].isupper():
                               
                    elem = elem.replace(".",".<split>")
                    wordlist2.append(elem)
             
                else:
                    wordlist2.append(elem)
 
        else:
            elem = elem.replace(".",".<split>")
            wordlist2.append(elem)
        
    text = ' '.join(wordlist2)
    
    # Remove unnecessary beginning from the document. Convention change in 2015.
    if y <=2014:
        text = remove_leadup(text)    
    if y >=2015:
        text = remove_leadup_2(text)  

    # Remove speech interjections
    text = del_text_in_parenthesis(text)     
    text = del_text_in_brackets(text)

    # Replace "!" and "?" with <split> to mark sentence splitting location 
    text = text.replace("?","?<split>")
    text = text.replace("!","!<split>")
    
    # Tokenize into sentences 
    sentences = text.split("<split>")
    
    # Remove swedish language sentences. Save the number of removals as well.
    sentences, removed_swedish = remove_swe(sentences) 
     
    # Cleanup
    for idx, i in enumerate(sentences):
        if i == " .":
            sentences[idx-1] += "  "
            del sentences[idx:idx+1]
    
    sentences = list(filter(None, sentences)) 
    sentences = [x.strip() for x in sentences]
    
    return sentences, removed_swedish


# Add the Speakers and Deputy Speakers of the Parliament, as well as their
# terms (start and end times) into lists
df = pd.read_excel('lookups/puhemiehet.xlsx', sheet_name=0)
parl_speakers = list(df['par_speaker'])
df = pd.read_excel('lookups/puhemiehet.xlsx', sheet_name=0)
starting_times = list(df['start'])
df = pd.read_excel('lookups/puhemiehet.xlsx', sheet_name=0)
ending_times = list(df['end']) 

    
# Check, if the MP is the Speaker or the Deputy Speaker of the Parliament
# at the current time
def is_a_chair(name, time):
    
    if name in parl_speakers:
        
        if (time >= starting_times[parl_speakers.index(name)] and 
        time <= ending_times[parl_speakers.index(name)]):
            return True

        elif (parl_speakers.count(name) == 2 and 
              time >= starting_times[parl_speakers.index(name)+1] and 
              time <= ending_times[parl_speakers.index(name)+1]):
            return True    

        else:
            return False
    
    else:
        return False
        

# Add MPs into a list ("firstname lastname")
df_edustajat = pd.read_excel('lookups/kansanedustajat.xlsx', sheet_name=0)
edustajat = list(df_edustajat['edustajat_kokonimi']) 
 

# Add Ministers (title firstname lastname) into a list
df = pd.read_excel('lookups/ministerit_nimikkein.xlsx', sheet_name=0)
ministerilista = list(df['ministerit_ja_nimikkeet']) 


# Check, if a sentence is a start of a speech
# x = sentence, y = list with MPs with parties and Ministers with titles
def check_speech_start(x, y):

    for i in y:
        if i in x:
            return True
    
        elif i + " (vastauspuheenvuoro):" in x:
            return True
        
        elif i + " (esittelypuheenvuoro):" in x:
            return True


# Check, if sentence is a (content-based) end of a speech    
def check_speech_end(x):
 
    speechs_ends = ["keskustelu päättyi", "keskustelu on päättynyt", "yleiskeskustelu päättyi",
                    "selonteko hyväksyttiin", "kysymys on loppuun käsitelty",
                    "asian käsittely keskeytetään", "keskustelu pääministerin ilmoituksen johdosta",
                    "puhetta oli ryhtynyt johtamaan"]
    
    for i in speechs_ends:
        if i in x:
            return True


# Find an MP name in a string
def find_name(x):
    for i in edustajat:
        if i in x:
            return i


# Based on time, get a list with MPs with their parties at this time, plus
# the complete Ministers lists.
def date_to_mplist_with_parties(x):
    df2 = pd.read_excel('lookups/edustajat_puolueineen_ajankohtina.xlsx', sheet_name=0)
    for idx, i in enumerate (df2.columns):
           
        if i > x:
            correct_column = df2.columns[idx-1]
            y = (list(df2[correct_column]))
            
            # convention change in 2015: no "/" before party abreviation
            if x > 141231:
                y = [s.replace("/", "") for s in y]
 
            return y + ministerilista
            break
        
        elif x >= 200604:
            correct_column = 200604
            y = (list(df2[correct_column]))
            return y + ministerilista
            break
    
# Get MP's party based on the name (x) and the time (y)
df_mps = pd.read_excel('lookups/kansanedustajat.xlsx', sheet_name=0)
cols = list(df_mps)
times = list(df_mps)
times.pop(0)

def name_to_party(x, y):
    
    for idx, i in enumerate (times):
        if y < i:
            col = cols[idx]
            break
        if y > 200604:
            col = 200604
            
    result_series = df_mps[(df_mps['edustajat_nimet'] == x)][col]
    party = result_series.to_list()[0]

    return party    


# Find religion references. X = sentence
def search_religion(x):
    
    # Add stopwords, keywords and keyword categories into lists
    df = pd.read_excel('lookups/stopwords.xlsx', sheet_name=0)
    s = list(df['SW']) 
    df = pd.read_excel('lookups/keywords.xlsx', sheet_name=0)
    k = list(df['KW'])
    df = pd.read_excel('lookups/keywords.xlsx', sheet_name=0)
    k_cat = list(df['KW_CLASS'])

    
    # If the sentence x contains stopword, replace that word with ""    
    for i in s:
        if i in x:
            x = x.replace(i, "")
    
    # If the sentence x contains keyword, return keyword and keyword category
    for i in k:
        if i in x:
            return i, k_cat[k.index(i)]