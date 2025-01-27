#!/usr/bin/env python
# coding: utf-8

# This file will download the example files in the Semantic Scholar Open Research Corpus (S2ORC).  S2ORC is a general-purpose corpus for NLP and text mining research over scientific papers.  
# 
# S2ORC project is here:
# https://github.com/allenai/s2orc
# 
# Creates directory structure:
# 
# |-- metadata/
#     |-- raw/
#         |-- metadata_0.jsonl.gz      << input; deleted after processed
#     |-- medicine/
#         |-- metadata_0.jsonl         << output
# |-- pdf_parses/
#     |-- raw/
#         |-- pdf_parses_0.jsonl.gz    << input; deleted after processed
#     |-- medicine/
#         |-- pdf_parses_0.jsonl       << output
# 

# In[1]:


import os
import subprocess
import gzip
import io
import json
from tqdm import tqdm
import pandas as pd


os.chdir('../data')
os.getcwd()


# In[2]:


# define some programs

# process single batch
def process_batch(batch: dict):
    # this downloads both the metadata & full text files for a particular shard

    cmd = ["wget", "-O", batch['input_metadata_path'], batch['input_metadata_url']]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    cmd = ["wget", "-O", batch['input_pdf_parses_path'], batch['input_pdf_parses_url']]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


    #loop through all the pdf entries and save to pandas dataframe
    pdf_results=[]
    cols=['paper_id','full_text']

    # first, let's filter metadata JSONL to only papers with a particular field of study.
    # we also want to remember which paper IDs to keep, so that we can get their full text later.

    paper_ids_to_keep = set()
    with gzip.open(batch['input_metadata_path'], 'rb') as gz, open(batch['output_metadata_path'], 'wb') as f_out:
        f = io.BufferedReader(gz)
        for line in tqdm(f.readlines()):
            metadata_dict = json.loads(line)
            paper_id = metadata_dict['paper_id']
            mag_field_of_study = metadata_dict['mag_field_of_study']

            # if field is empty just replace with empty string
            if mag_field_of_study is None:
                mag_field_of_study=[" "]

            # we want only papers pdf text available
            if not metadata_dict['has_pdf_parse']:
                continue                
                    
            #if not all(x in mag_field_of_study for x in excluded_fields):    #exclude omitted fields
            
            paper_ids_to_keep.add(paper_id)
            f_out.write(line)

    # now, we get those papers' full text
    with gzip.open(batch['input_pdf_parses_path'], 'rb') as gz, open(batch['output_pdf_parses_path'], 'wb') as f_out:
        f = io.BufferedReader(gz)
        for line in tqdm(f.readlines()):
            pdf_dict = json.loads(line)
            paper_id = pdf_dict['paper_id']
            if paper_id in paper_ids_to_keep:
                f_out.write(line)

                paragraphs = pdf_dict['abstract'] + pdf_dict['body_text']
                # (3) loop over paragraphs, apply nlp to title and abstract
                full_text=""
                for paragraph in paragraphs:

                    # (4) loop over text in this paragraph and append together
                    
                    for text_span in paragraph['text']:
                        #append
                        full_text += " "
                        full_text += text_span
                    
                pdf_results.append([paper_id, full_text])
    
    nlp_pdf_df=pd.DataFrame(pdf_results, columns=cols)
    nlp_pdf_df.to_parquet(os.path.join(PDF_PARSES_PARQUET_DIR,f"pdf_text_{batch_num}.parquet"), engine='pyarrow')

    # now delete the raw files to clear up space for other shards
    os.remove(batch['input_metadata_path'])
    os.remove(batch['input_pdf_parses_path'])


# In[ ]:


# there are 100 shards with IDs 0 to 99. make sure these are paired correctly.
download_linkss = [
    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_0.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=gS%2FTwZyr2WmNMIyrakAoqNM%2FVSc%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_0.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=nJuSD314fSU9DujRJ70P09q2iuQ%3D&Expires=1647027264"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_1.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=mjAt8w%2Fn8fBmspuMer8ZwxwCAUM%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_1.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=eKJYLiyWQOzPHkwREJqnfZeefHM%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_10.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=2tL%2FazdFrtfGsEw%2Bbk3qR%2FnEGxg%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_10.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=sLSeRP02yp5eSKgFjEZ1cSkLMag%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_11.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=aIx8GkG5hD5Jcefg9McL6mXBtuA%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_11.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=UlBZ5xvTrf67VTz5ZXgsOwTma9c%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_12.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=aBKoOfXfzKxZBSqtYPRjTEogsTc%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_12.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=zZqyFPyqRM5wmCWVM8W9A33kDQs%3D&Expires=1647027264"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_13.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=zUVUx%2BCG0QZlKc6B7fC24yEQX6w%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_13.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=4OCLryWzrIcF3TSRky6Pus6K%2Fgw%3D&Expires=1647027264"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_14.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=lnzyXEr2xtoETj6lWhg3yUEzPJY%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_14.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=qHY9nxsxbXxEcZyk984nQjGQksc%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_15.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=0GNqDk%2BShpZ8MSqqRCJhztu3438%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_15.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=2nLcTKVp4sh9ItjOvKio44QsWCg%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_16.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=FOQglFYS7cc2z8QNBv02J6Sgw8w%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_16.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=kiG2xsiOLHp8f1UvP6KtNeLdACY%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_17.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=SPGKEkbZBumgXzJTEzv8hvLu4lU%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_17.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=kRDtlnjHjr%2FstGJiP2uA8YDQmps%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_18.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=UhM4u5LIn5MnUEmSO%2Fkh9pVOcTU%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_18.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=AEoR%2FSonk5GTnub4Gp3zYn71WMk%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_19.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=StIOpu8dFjMiUbjx3rxBBaWpOVw%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_19.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=iwsrclYM0D3uRf%2BTfTr64K2%2BA7k%3D&Expires=1647027264"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_2.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=VeWbdjC7ofI4sCmsOLyF8U%2FCFlY%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_2.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Q%2Bn21XBVIVoCQw9lYwQK9NBxeHE%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_20.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=mGXCCmtkJvxvl2IJjU1bppn%2BGcQ%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_20.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ddVVRSJMllsPvlGwgoD5jWnXPb4%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_21.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=IMa9xtr349xraKRcXopgfhfGyXA%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_21.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=6U5DEBojnfatZ1JbRnrdCP9%2FuyY%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_22.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=sb77Bqf32EpLRJsryEzmTDS11is%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_22.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=5Ah8940ukmee2qd60%2B5IBF6l20I%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_23.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=5ckU0s9kwjBszs4dvStKNdHovrY%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_23.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=BdstfkqNsTcwnrQa3eAPOxj%2Fh34%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_24.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ww2RlfjtKACROA0DIwdZwQJgaqE%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_24.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=9zANi%2BvKRbim5MK28m3kMmXL8tM%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_25.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=eouQZ8UoO5kU4KtT3%2BQdY%2F%2BCEDY%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_25.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=WF6a%2BOw5kq71nchRUt0NhqZeGZo%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_26.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=LHqkjwuzhkk8mjFdP5T7RRt6O08%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_26.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=YehbFmvrNfuJWlX0ZT1ZNU%2ByniQ%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_27.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Nvlh3o%2FzkO%2BFHlqItSGsljbyuTI%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_27.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=%2BEvi0UJA4GsmaCw7cxZELxX5EGE%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_28.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=6oe6xfEl897V2wcS5F4V8%2FmpXIw%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_28.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=p%2FwNzm9cFTW3w%2FPJlodsSO%2F5FLE%3D&Expires=1647027265"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_29.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=%2F0cDlhB5uznY4lN920Z6QHcLpI4%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_29.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=62KzJhCUZ%2F2NcnhWuDaVBDV%2Fg5g%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_3.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=e2D4OhubLKWKx14AgOI%2FMYxOhSE%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_3.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=whtjhdMfK0kwLKhhFoE3OqzuNK8%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_30.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Yi6zxcyevhGtgpJqK%2FyOOYSorMM%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_30.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=43M82JJLlqMC7SRh5esrFtCQhII%3D&Expires=1647027265"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_31.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=dMpvNa0yokuVZSCHFi%2Br%2FDxCkBY%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_31.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=74Ahx6z84N8J7nyq16P01Xta%2FWg%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_32.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=XJujlXnymr04wRMVKPlDQ%2Fb9QT8%3D&Expires=1647027261",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_32.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=5TKxIkaiZDJ%2FFgT2o4oz3kW%2FlpA%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_33.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=c0wMtLaLJYmW%2B29IkRzJrHe5Vak%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_33.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=IQ8HeXUJCri%2F60Uaanzf2kmkxXE%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_34.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=YKwsTvtB5SL5MX9%2BLmU%2F5SxkmMU%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_34.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=prm%2F7I9%2F%2F%2FObR0lqePnGi0zR9Vg%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_35.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=tqfUbGAMLO05jVpf34jvBw3tFxc%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_35.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=4oCEblLzAOKxueiDPe6bIxMk5MU%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_36.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=kA1VT9fcRPNa7nIVaLCFtJe8s18%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_36.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=tz42BPw69rgGVjyTZjnMEkZam7A%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_37.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=HToeA9rgUzl4ONkJZHSVx2n8%2B%2BE%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_37.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=vJrgC4HZ3LfsGjMrINzOMK%2FdFb4%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_38.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=DEmVjDjBsnZ1Vh0tFj0EHPPSbX4%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_38.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=HVR56D1vRiBFenPkVMoSo1Mzezs%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_39.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=3nxCdWo1kjp%2FQ42eQuCK35qy9ik%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_39.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=CVvTjXp1Ak8cNKPVB4IyDKmHmnA%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_4.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=UcZUrevDgNezTV54KG39aqg1Y0U%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_4.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=nRjmSfFX0YvU5mg6LxIb%2FcK6Af0%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_40.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=0kaTmADTFSk3uHtntt8M7JaB5w8%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_40.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=R3ko8Q8hqQdU6a2SpyjQiJqMJCE%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_41.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ZPAlwu7NtavTy8GEtteVUOAOZWo%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_41.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=a3XBtOq9d8bAF8tmXvJAUebVu0A%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_42.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=4uTnZgS7%2FAcpeX1skFPkxT0MjLk%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_42.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=teA4jBlaRhOsQ9efPZsAJRaWtYU%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_43.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ZmEQbXbnGCj61F%2B%2BNPEVTsGk0y8%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_43.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=d82rdlfPwWVTmJM3ypttfPveNoE%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_44.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=QPYYehvyqZ7%2BVNUBKlenYDPCD4Y%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_44.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=eo2dZQg6txCfAxm8ChQhx39MsMc%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_45.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=%2BcWwfszSukzAA1VjQS0HRhyUWfo%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_45.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Ed69saWgIvoU27XrUuVSoawCTBE%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_46.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=5mNzBQoeRSgCoxSMpnoyDp0OaXA%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_46.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=3c5KHPDWE9wQLJoW3bnYNc0VKVU%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_47.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=zqgjiul9OZGIlCuLsgoGcF0bilA%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_47.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=D1XgZusUYU2AKJisdS88J0KAKzM%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_48.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=DxqXWdG3huw5LXzXdLwrt6KJoRE%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_48.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Bh4JXunA8gQqWu1JVfEgSabkF44%3D&Expires=1647027265"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_49.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Z599ESNmYb8igLbTVHibMjO9aDI%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_49.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Bh5oM9NDXzd%2BqDlUhfPRQK39iZU%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_5.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=rlrnxZG9Vsg39nOQZEEXtNtysOY%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_5.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=2PPaTurU4U4D%2Bc%2B9PYn558sPFKs%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_50.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=5y9pr1RgvDg56RlrCFlZZV4i0Qs%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_50.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ZeHMO4Cy2Y5OInNZsQaOvd5I%2FJQ%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_51.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=D7kKKzvYFBUnmwJgMCiDeJCdqtg%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_51.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=MU28g81KXTIokHGzeIv0UcsalUg%3D&Expires=1647027266"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_52.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=%2BRCUsdZYKccm7sBSAU%2F%2FrFxVM%2BI%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_52.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=3IES7iS%2BhRXTdTk0Wv9wvP7Wxhw%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_53.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=KoKN2f0N8USZanOMGxYsSW0ptIw%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_53.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=qN67cprXpnIN366HzgNZonFivAU%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_54.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=hQhh3p7lRGzcQZaylQIGAuIBPBc%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_54.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=U0zDcP92CNJVp8AgReW8Ofi7t9E%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_55.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=3hb0fVKUvsUsM%2FP%2FB%2F%2Bwb2gNHGw%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_55.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=DpbngZfmqm3qTrt3QJP0GKeUDTE%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_56.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=aaTANdjyi8rNcIhZ21V%2FoA07xXY%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_56.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=gEzkQ72ZMM5JXY29DgcS%2FXzTYYo%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_57.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=%2BZ9iFNqeQo2mByGeBftDfcQCq%2Fs%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_57.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Yn2M5K4nwgjbl7%2FojEvrmM%2FuSTg%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_58.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=zqi660lMPOFSYxp7fCsJkpiVAa4%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_58.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=wLXyAZXvvhOzdLgNAhh%2BTTZgyLM%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_59.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=V1btCEu7JBmPD%2BTBqunqRK%2FGmCc%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_59.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=4zju91R2uma%2BHJtt360aGf46Cdw%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_6.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=qJ%2FDtzvLfUBZMLyjHtA5etxjBNA%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_6.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=O3XqIiF993HC%2BOyHTa0obiIEaZ4%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_60.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=UYJJHdUdgMkBOWpCNLCqrERRaZI%3D&Expires=1647027262",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_60.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=AWQ915aerE5T0a8r92EkfUh2UyM%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_61.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=BoGgFzwzBbSZe%2Bpgjhi530c4ibE%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_61.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=lLtAb0VISgy1vVBcjB8aBN1DgVU%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_62.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=mpOzRCS67qwk8Ox91s14lMw4Wj8%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_62.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=M6Z2E%2FVLJwUsv4EY8D5aBy%2B7XEo%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_63.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=vuXHPOzYLepbq8JW9o%2BQ4IGK0nw%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_63.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=yaqGZxIcTMKYU7WGYfQ6%2Fhu1AOo%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_64.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=6JnGsaS7vRz1oJaOPjkuXPgaNDI%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_64.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=q3iBOwymjT7ScZV8%2FjfFb7fN8BI%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_65.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=zurnyd2fH8SpJjT7kAItCvswP74%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_65.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=i%2FJpONvafh91uTqfm11%2BpFpfrNI%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_66.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=X1Mik3uIdqENrETLdl8w962Ya5s%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_66.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=3Oo43e3FSmilJaeITMVX8qoBdXQ%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_67.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Fp%2Fk5OHykCyGguImBy9o%2BJeVQh8%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_67.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=4QgTPl6cBfO1YxlXObXeQsSui9s%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_68.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=HfSzIL5UIJL%2F6lWufMxCLrxPork%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_68.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=YWVRMJ4nAA6UzjSu2%2FnWgUriiyY%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_69.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=b3KjO7z4%2FV3K6onoMhgLd2FVwB4%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_69.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=r3wJbDwcJEoaBmD8D9Ay1FZsAHU%3D&Expires=1647027266"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_7.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=WrIQ1xtZXaLflWhoV6ONn3iRews%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_7.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=abDO98woNEbJrU6jdogBEsrAEaY%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_70.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=xz1Q%2FR5EPyGR0TCKZHABxSf%2BiJ0%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_70.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=sNT3WBvr4XVF%2BIGrSYxxU70WAcw%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_71.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=QiNiAZ2hf%2Bn0nkak8KgvxbEHTTs%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_71.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=T8n4v3th%2B6P8qAdaXzqMnsQihDk%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_72.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=5%2FSGC0EDSfpecPfwW%2BCN9wYdjGw%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_72.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ZI97%2Bevc8up7VhzzyMXr%2BOf6c24%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_73.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=LT4kMQZenWn3xxYDJLasq7vR0V0%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_73.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=9nWfX5gUEpVMiMqDN5GgWM6NMhg%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_74.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=VFMzhWW097dwozuSzw8a9LXOJ2k%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_74.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Wv1gbMum9vaDiz8463ikcSl6y00%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_75.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=%2FizECYmc1e74PkWod9B5sUAUFwM%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_75.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=8UL9c0KHqAt%2FQurm%2BGtgy1yvpdI%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_76.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=%2Bb7pFAQjm26GyiBEsSnxqb73noU%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_76.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=aUVKsxtk%2FHpp4hKkuz4HY3mcpX0%3D&Expires=1647027266"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_77.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=FMPo2awxfxB9a3LgKo9iXh6vrRU%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_77.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=37uhggKQoWj%2F8l5Fi53kWO9fXF0%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_78.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=pUHtfUgdLGy8Q4hLzTwnoNShAlM%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_78.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=sAMF8YNT5yd4FUl2l4rlWFs3tAI%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_79.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=inZQ1%2B03LV3Ah7jSK%2FkveqI7pT4%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_79.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=xAhN5phSITASt7ZLN%2F98Ve%2BZUqI%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_8.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=zWF0MT50f5UCxBKOaTcPyrg%2FzPU%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_8.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=QGiCnNyD6Knz97XIaGSGI07ESyw%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_80.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=m1kIrQmZv85gNPFempqLVtN9OE4%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_80.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=a86ZTJOLC%2FG4T2ER%2BUV8QWzADWA%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_81.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=j4xVQhhvyUyjSFO0dyOVAw5PzEY%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_81.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=s616TQqVr1m6LVKlM%2B07Ixbyza0%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_82.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ZIH9bbJtkuYcsdr%2FHh0mNKNtr%2BA%3D&Expires=1647027263",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_82.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=j86OrePvCEMUQYIHvlBlDxExpU0%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_83.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=K1jInk%2FnAealtimgHFFgv9QXq%2BU%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_83.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ViF1vamwL6vU%2FCxstt16jLyUl%2BY%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_84.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=YI9l%2Bd8YUeMblX0s9WuT8QzNK%2B0%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_84.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=JlYiRugDSf5B6RXgq6eTr918XhI%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_85.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ZCOeBZQVMk7d8M3A1Bsu90YXiGA%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_85.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=SDt7cqy7rRc78aUF6qAwij0%2FJmI%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_86.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=eTe6F3mhKKLNEwz7d1cNOdpySXg%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_86.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=LlnRNajAdtynWFu8s657%2BR0aw5o%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_87.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=8YndQa9%2Fr9x3bkitFWbb4zk7fwg%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_87.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=JntW4iX23YwR8VmIt1PREOYuyho%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_88.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=j1UqVfK9oIf9PdlFmvPo5u%2B%2BWHo%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_88.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=k%2F6q3TegqhuwOUIv1JsjYfIncSk%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_89.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=99x4SQh7WcSbB360XjgyTSiMh7w%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_89.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=hMTILBG8sy%2FmlNs1dw7j2fgNdb0%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_9.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=s7Y6ssqP%2BubbDNfQrk0xIHXoBpo%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_9.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Oe0wiofVbmx0nK84BL00Gocykro%3D&Expires=1647027267"},

    {"metadata": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_90.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=DO%2B%2BqEgKjhp6PUOmk4jcT04NFe4%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_90.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=vtKKFE56YYIPUEJSPAlM7uzaE94%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_91.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=WhU2DD490oi3lutF6v183Rdeb%2Bs%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_91.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=MopiJGSJvgZFGRWsJi1K7q05M%2FA%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_92.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=8UXymf31KhgDjlcUFJzU7KqUmgQ%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_92.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=LRF5Hi%2F00JDXxNHhbX91UYJdddg%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_93.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=aXeeV%2Fi7WngwbQvo%2B77sG5rHxMs%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_93.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=C%2B%2FFMVeDLPBI8oNlYo628FaOnoA%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_94.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=CaoxUlAKz9w5MlDx9Gc3EZXnKpM%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_94.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=Xxtb0caVpiv3zVPaMXt5qs168gw%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_95.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=2215xP20fnYIvYHdnuX8tLBY54c%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_95.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=3%2F08iTHe%2BmiADLFWptOxxP4h0oQ%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_96.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=31AboqxrL0hzzXfPpNQAd%2F2vc8A%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_96.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ljKktcW9akOLDM27GWG4GW8vAOI%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_97.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=T1i4tAnQfl6VN4y%2BrvZLhXaNXLE%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_97.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=tbjLgWW8oPqBOq67pSvNUOUqTHo%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_98.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ABScp2UAGZhwzrYywr8Nfr6hmi4%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_98.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=ydeydVoPf%2FwZEj%2Bj0%2FMJHMEPwMA%3D&Expires=1647027267"},

    {"metadata":  "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_99.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=7eulLklZlDSCFcz1rgEP6tbyXJE%3D&Expires=1647027264",
    "pdf_parses": "https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/pdf_parses/pdf_parses_99.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=knJwBZC0HO362LvK%2B%2Br1n1fQBcM%3D&Expires=1647027267"},





]


# In[ ]:


#list of excluded academic fields (mostly hard science fields and art)
#excluded_fields = [ 'Biology','Chemistry', 'Engineering', 'Physics','Material Sciency', 'Geology', 'Art']
excluded_fields = [ ]

if __name__ == '__main__':

    METADATA_INPUT_DIR = 'metadata/raw/'
    METADATA_OUTPUT_DIR = 'metadata/included/'
    PDF_PARSES_INPUT_DIR = 'pdf_parses/raw/'
    PDF_PARSES_OUTPUT_DIR = 'pdf_parses/included/'
    PDF_PARSES_PARQUET_DIR = 'pdf_parses/parquet/'

    os.makedirs(METADATA_INPUT_DIR, exist_ok=True)
    os.makedirs(METADATA_OUTPUT_DIR, exist_ok=True)
    os.makedirs(PDF_PARSES_INPUT_DIR, exist_ok=True)
    os.makedirs(PDF_PARSES_OUTPUT_DIR, exist_ok=True)
    os.makedirs(PDF_PARSES_PARQUET_DIR, exist_ok=True)



    # turn these into batches of work
    # TODO: feel free to come up with your own naming convention for 'input_{metadata|pdf_parses}_path'
    batches = [{
        'input_metadata_url': download_links['metadata'],
        'input_metadata_path': os.path.join(METADATA_INPUT_DIR,
                                            os.path.basename(download_links['metadata'].split('?')[0])),
        'output_metadata_path': os.path.join(METADATA_OUTPUT_DIR,
                                             os.path.basename(download_links['metadata'].split('?')[0])),
        'input_pdf_parses_url': download_links['pdf_parses'],
        'input_pdf_parses_path': os.path.join(PDF_PARSES_INPUT_DIR,
                                              os.path.basename(download_links['pdf_parses'].split('?')[0])),
        'output_pdf_parses_path': os.path.join(PDF_PARSES_OUTPUT_DIR,
                                               os.path.basename(download_links['pdf_parses'].split('?')[0])),                             
    } for download_links in download_linkss]
    batch_num=0
    for batch in tqdm(batches):
        process_batch(batch=batch)
        batch_num += 1


