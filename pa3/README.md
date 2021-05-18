# install anaconda dependencies into proper environment
`conda install nltk`

# navigate to implementation-indexing folder when running any of the following programs

# run boostrap.py program that downloads nltk data before running any other programs
`python bootstrap.py`

# run indexing
`python run-indexing.py`

# run search
- search with sqlite index (need to run indexing first): `python run-sqlite-search.py "QUERY"`
- search without index: `python run-basic-search.py "QUERY"`

# number of results
To change number of results, change `NUM_RESULTS` constant in processing module.