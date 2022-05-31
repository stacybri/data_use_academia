# s2orc_data_use
Data Use in Academia project based on S2ORC data

## Motivation

International donors have recognized the important role that national statistical systems play in producing high quality data related to development, such as in producing censuses, surveys, indicators, and in providing users data services. According to PARIS21, the international community funded around $2 billion in statistical development activities between 2016 and 2018 (Paris21 (2020)). The World Bank alone has funded $610 million for those activities in that period.  These investments are typically justified as a means to improve evidence-based policy making in low- and middle-income countries. 
Academia plays a key role in producing evidence-based policy recommendations and is a strong beneficiary of the existence of productive national statistical systems. High quality population censuses, for instance, are key for producing a representative sample in a survey that is part of a research study. Microdata produced by the national statistical system in the form of household income and expenditure surveys, agriculture surveys, or demographic and health surveys are routinely used as part of academic studies. A dysfunctional system that is not producing the key data sources or indicators, does not follow basic international classifications to make data comparable, or does not have the data services in place to connect users of the data to the products that are produced, may have less engagement by academia and consequently have a deficit in research on problems facing the country.

The World Bank recognized the importance of academia as a user of the national statistical system in the recently released Statistical Performance Indicators (SPI). The SPI framework assesses the maturity and performance of national statistical systems in five key areas referred to as pillars (Dang et al. (2021)). The first pillar is on data use. It considers the extent that a national statistical system produces products that are meeting the needs of users, and one of the dimensions of this pillar is on data use by academia. However, as acknowledged in the report, measures of data use by academia are in an embryonic stage. Without measures highlighting deficiencies in the usage of data, it is difficult to spotlight problem areas, and countries may lack the information needed to prioritize investments in statistics.

  Some previous academic research has highlighted gaps between countries in academic research output. For instance, Robinson, Hartley, and Scheider (2006), Das and Do (2013), and Porteous (2020) examine which countries are studied most by economists using the EconLit database. These studies note that the distribution of economic research is highly uneven across countries. Cameron, Mishra, and Brown (2016) and Sabet and Brown (2018) extend this to note that impact evaluations are highly uneven across countries as well. However, these studies are narrowly focused on publication in economics journals and the authors are not updating their rankings across countries on an annual basis. Another issue is the EconLit database contains data for only 74 countries.

Advances in Natural Language Processing, based on machine learning, and new data sources have opened up new approaches to measuring academic data use at low costs. Organizations such as CORE (COnnecting REpositories), have digitized millions of research papers produced around the world, including in fields other than economics, and opened up APIs for accessing the raw text of these documents. The CORE dataset also includes data from at least 149 countries, which is much greater than the 74 countries covered by EconLit. Natural Language Processing algorithms have been developed to efficiently parse millions of documents to classify documents. For instance, Hansen, McMahon, and Prat (2018), published in the Quarterly Journal of Economics, processed 149 transcripts from the Federal Reserve to study how Federal Reserve board members react to transparency in terms of topic coverage. 

Using these tools, we propose to develop a methodology for measuring data use by academia. These measures will then be used to study the relationship between products produced by the national statistical system and research output, 

Research questions 
The project seeks to answer the following questions: 
(i)	What is a feasible way to create a metric of data use by academia?
(ii)	What is the relationship between activities of the national statistical system and academic output?

### Output and impact 

The main output of the project will be a research paper documenting the methodological approach and empirical findings. This will be followed by a blog posts and conference presentations on the approach.

A second output will be the release of the data publicly for other researchers to use freely, subject that they appropriately cite our work. The data may also be featured as an indicator in the Statistical Performance Indicators (SPI) that are released annually by the World Bank.


## Organization


There are several subfolders in this repository.  Below is a list of the most important files.


  1. 01_raw_data contains the raw data for the project.  In general, files in this folder should be read in only, not saved over.  Inside rawdata, there are a few subdirectories.  classification_set contains some human coded classifications of data use and country of study using Amazon MTurk.  metadata contains metadata on the articles from s2orc including title, abstract, field of study.  pdf_parses contains the pdf text from the articles.  Articles are put into equally sized batches.  There are 100 such batches.  These can be found in the /included folder, which contains json files with the metadata or raw text.

  Mturk classification files are in the classification_set folder.  They include a set of csv files.  These csv files can be linked to the original articles by the title and abstract of the article.  They can be easily matched to the underlying article by matching based on the sample csv files in the 03_output/sample folder.  These csv files contain the randomly selected articles that were chosen for the Mturk classification.

  2. 02_programs contains various scripts for analysis.  

  3. 03_output_data.  This folder contains a number of final output files in either csv or other format.  The /sample folder contains a random selection of articles that was used in Mturk classification.  There will be multiple csv files in this folder, because the Mturk classification was done in batches.