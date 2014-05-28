REGISTER /usr/local/pig-0.12.1/build/ivy/lib/Pig/avro-1.7.4.jar
REGISTER /usr/local/pig-0.12.1/build/ivy/lib/Pig/json-simple-1.1.jar
REGISTER /usr/local/pig-0.12.1/contrib/piggybank/java/piggybank.jar
REGISTER 'bootcamp_udf.py' using jython as udf;

DEFINE AvroStorage org.apache.pig.piggybank.storage.avro.AvroStorage();

buzzwords = LOAD 'buzzwords.txt' using TextLoader() AS (buzzword:chararray);

messages = LOAD '../data/emails.avro' USING AvroStorage();

msgs_words = CROSS messages, buzzwords;
msg_score = FOREACH msgs_words GENERATE message_id, buzzword, 
	udf.count_buzzword(CONCAT(CONCAT(subject, ' '), body), buzzword) as score;
msg_score = JOIN messages BY message_id, msg_score BY message_id;

word_score = GROUP msg_score BY buzzword;
word_score = FOREACH word_score GENERATE group, SUM(msg_score.score) as score;
word_score = ORDER word_score BY score DESC;

from_score = GROUP msg_score BY LOWER(from.address);
from_score = FOREACH from_score GENERATE group, SUM(msg_score.score) as score;
from_score = ORDER from_score BY score DESC;

\d word_score;
\d from_score;
