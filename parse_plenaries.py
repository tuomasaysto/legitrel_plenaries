# -*- coding: utf-8 -*-
# @author: Tuomas Äystö

from transformations import (find_date, preprocessing, date_to_mplist_with_parties, 
                             check_speech_start, check_speech_end,
                             name_to_party, find_name, is_a_chair,
                             search_religion)
import pandas as pd
import os, time



# Lists for the collected information
dates, doc_names, speeches, sents, rsve = [], [], [], [], [] # general
cd, cp, nc, fp, spp, sd, br, la, gl = [], [], [], [], [], [], [], [], []   # parties (cd = Christian Democrats, etc)
r_date, r_doc, r_kw, r_kw_cat, r_party, r_speaker, r_sent = [], [], [], [], [], [], [] # religion-related


# Set year (documents are processed one year at the time)
# Only tested for 2010-2020
year = 2018


# Check the number of files in the data-directory
files = 0
dir = "data"
for path in os.listdir(dir):
    if os.path.isfile(os.path.join(dir, path)):
        files += 1


# Loop thru the documents in data-folder and process them sentence by sentence
current_file = 1
while current_file <= files:
    t = time.process_time()
    
    # Open a document as a string, lowercase
    # Files named "ptk_#_year.txt", where # is a consecutive number
    f = open('data/ptk_%s_%d.txt' % (current_file, year), encoding='utf-8')
    cur_doc_name = f.name[:-4]
    f = f.read().lower()
    print ("Processing " + cur_doc_name  + ("\n"))
    
    
    # Get document date
    pvm_flipped = find_date(f, year)
    
    
    # Preprocess and tokenize to sentences
    # Returns sentence list and the number of removed swedish sentences
    f, removed_swedish = (preprocessing(f, year))
    print ("The document has " + (str(len(f)))  + " sentences." + ("\n"))    
    print (str(removed_swedish) + " Swedish language sentences were removed." + ("\n"))
    
    
    # Get a list with MPs and their parties and the Ministers with their titles at this time
    mps_and_ministers = date_to_mplist_with_parties(pvm_flipped)
    
    
    # Keep count of the number of sentences per party
    cd_l = cp_l = nc_l = fp_l = spp_l = sd_l = br_l = la_l = gl_l = 0
    def cur_party_incrementer(x, y):
        global cd_l, cp_l, nc_l, fp_l, spp_l, sd_l, br_l, la_l, gl_l
        if x == "kd":
            cd_l += y
            return cd_l
        if x == "kok":            
            nc_l += y
            return nc_l
        if x == "kesk":
            cp_l += y
            return cp_l
        if x == "ps":            
            fp_l += y
            return fp_l
        if x == "r":            
            spp_l += y    
            return spp_l
        if x == "sd":            
            sd_l += y
            return sd_l
        if x == "sin":            
            br_l += y
            return br_l
        if x == "vas":            
            la_l += y
            return la_l
        if x == "vihr":            
            gl_l += y
            return gl_l
    
    
    # Iterate through the document sentences, and recognize individual speeches, 
    # speakers and parties. Search for religion-related keyword hits.
    # Save general sentence details and religion hit details.
    cur_party = ""
    cur_speaker = ""
    cur_speeches = 0
    cur_speech_starts = 0
    iteration = 0
    
    for idx, i in enumerate(f):
    
        cur_party_sentences = 0
        
        # check, if another beginning of a speech is recognized (whichs ends the current speech)     
        if cur_speech_starts == 1 and check_speech_start(i, mps_and_ministers) == True:
            cur_party_sentences = idx-iteration
            cur_speech_starts = 0    
            cur_party_incrementer(cur_party, cur_party_sentences)
       
        # find a beginning of a speech, and attibute the sentences in it to the
        # correct party, (until an end of the speech is found)    
        if cur_speech_starts == 0 and check_speech_start(i, mps_and_ministers) == True:
            
            # ignore Speaker and Deputy Speaker of the Parliament
            if is_a_chair(find_name(i), pvm_flipped) == False:
                cur_party = ""
                cur_speaker = find_name(i)
                cur_speech_starts = 1
                iteration = idx
                cur_party = name_to_party(find_name(i), pvm_flipped)
                cur_speeches += 1
       
        # recognize content-based end of the speech
        if cur_speech_starts == 1 and check_speech_end(i) == True:
            cur_party_sentences = idx-iteration
            cur_speech_starts = 0
            cur_party_incrementer(cur_party, cur_party_sentences)
    
        # check if the sentence has a religon reference
        # if yes, save related details. Ignore Speakers of the Parliament as above.
        if is_a_chair(find_name(i), pvm_flipped) == False:
           
            if search_religion(i) != None:
                a, b = search_religion(i)
                r_date.append(pvm_flipped)
                r_doc.append(cur_doc_name)
                r_kw.append(a)
                r_kw_cat.append(b)
                r_speaker.append(cur_speaker)
                r_party.append(cur_party)
                r_sent.append(i)
                
        
        print ("Sentence " + str(idx) + " out of " + str(len(f)) + " processed.")            
    
    print ("Document " + str(cur_doc_name) + " finnished in: " + str(time.process_time() - t) + " seconds."  + ("\n"))
    
    
    # Append the basic document details
    dates.append(pvm_flipped)
    doc_names.append(cur_doc_name)
    speeches.append(cur_speeches)
    sents.append(len(f))
    rsve.append(removed_swedish)
    cd.append(cd_l)
    cp.append(cp_l)
    nc.append(nc_l)
    fp.append(fp_l)
    spp.append(spp_l)
    sd.append(sd_l)
    br.append(br_l)
    la.append(la_l)
    gl.append(gl_l)
  
    current_file += 1


# Gather basic document details into dataframe. Row = document
sentences_df = pd.DataFrame (dates, columns = ['Date_(YYMMDD)'])
sentences_df = sentences_df.assign(Doc_name = doc_names) 
sentences_df = sentences_df.assign(Speeches = speeches)
sentences_df = sentences_df.assign(Sentences = sents)  
sentences_df = sentences_df.assign(Removed_Swedish = rsve)
sentences_df = sentences_df.assign(Christian_democrats = cd)
sentences_df = sentences_df.assign(Center_party = cp)
sentences_df = sentences_df.assign(National_coalition = nc)
sentences_df = sentences_df.assign(Finns_party = fp)
sentences_df = sentences_df.assign(Swedish_peoples_party = spp)
sentences_df = sentences_df.assign(Social_democrats = sd)
sentences_df = sentences_df.assign(Blue_reform = br)
sentences_df = sentences_df.assign(Left_alliance = la)
sentences_df = sentences_df.assign(Green_league = gl)


# Gather religon-related details into dataframe. Row = sentence with a religion hit
religion_df = pd.DataFrame (r_date, columns = ['Date_(YYMMDD)'])
religion_df = religion_df.assign(Doc_name = r_doc)
religion_df = religion_df.assign(Keyword = r_kw)
religion_df = religion_df.assign(Keyword_cat = r_kw_cat)  
religion_df = religion_df.assign(Speaker = r_speaker)
religion_df = religion_df.assign(Party = r_party)
religion_df = religion_df.assign(Sentence = r_sent)
  

# Output to excel
sentences_df.to_excel("output/sentences_%s.xlsx" % (year)) 
religion_df.to_excel("output/religion_%s.xlsx" % (year)) 

