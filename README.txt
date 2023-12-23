How to use our search engine

Use command "python main.py" or "python3 main.py" to launch program

It will then ask if you already have an inverted index and will prompt you to enter 'y' or 'n'. 
If you enter 'n', it will run the indexer first and then the search engine.
If you enter 'y', it will just run the search engine. 

In order to just run the search engine with 'n', you need to already have the files "storage.csv", "dids.csv", and "index.csv" in your directory
Note: These files are created by the indexer.

Please make sure you have the base_directory variable on line 11 of index.py set to your directory path that contains the "DEV" folder

If you choose 'n', it will take ~50 minutes to index the DEV folder and create the csv files needed. Then you will be prompted to search.
If you choose 'y', it will take a brief moment to load the index of index and document ID's into memory. Then you will be prompted to search.

Once you are prompted to search, you can enter your queries. The top 5 urls, amount of total matching results, and the retrieval time will be displayed.

Enter "exit*" to end the program

