bootcamp1405_mwemail
====================

This is a sample project for the Big Data Bootcamp.
This is NOT enterprise-ready software. 

Software Used:
+ Python 2.7
+ Avro 1.7.6
+ Pig 0.12.0
+ Jython 2.5.3

	
1. Avro
-------
In order to demonstrate some methods for handling unstructured/semi-structured data, I am processing some emails. I am using a set of my own emails, which I am excluding from this project for privacy. While it's fairly straightforward to stream emails from POP or IMAP, I chose to keep this project simple and repeatable by using a static set of emails in text files - specifically a folder of wdseml files from the Thunderbird email client.

To run ./1avro/emails.py as-is, you need to put some Thunderbird wdseml email files in ./data/emails/ relative to the project root folder. If you are using emails from a different source or format, you will need to modify ./1avro/emails.py accordingly. When it runs, it should serialize your emails to ./data/emails.avro

2. Pig
------
To have a little fun with the emails once they are serialized with Avro, I use Pig to count "big data buzzwords" occurring in the email subject and body, then aggregate the counts. This includes a python UDF to count the buzzwords.


3. D3.JS
--------
I created some very simple visualizations using the D3.JS javascript library.
