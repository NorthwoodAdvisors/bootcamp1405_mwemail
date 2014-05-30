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
msg_score = FOREACH msg_score GENERATE 
	messages::message_id, LOWER(from.address) AS address, buzzword, score;

word_score = GROUP msg_score BY buzzword;
word_score = FOREACH word_score GENERATE group, SUM(msg_score.score) as score;
word_score = ORDER word_score BY score DESC;
rmf ../data/word_score.json
STORE word_score INTO '../data/word_score.json' USING JsonStorage();

from_score = GROUP msg_score BY address;
from_score = FOREACH from_score GENERATE group as address, 
	SUM(msg_score.score) as score;
from_score = ORDER from_score BY score DESC;
from_score = LIMIT from_score 20;
rmf ../data/from_score.json
STORE from_score INTO '../data/from_score.json' USING JsonStorage();

from_word_score = GROUP msg_score BY (address, buzzword);
from_word_score = FOREACH from_word_score GENERATE FLATTEN(group) 
	as (address, buzzword), SUM(msg_score.score) as score;
from_word_score = JOIN from_word_score BY address, from_score BY address;
from_word_score = FOREACH from_word_score GENERATE from_word_score::address as address, 
	from_word_score::buzzword as buzzword, from_word_score::score as score, 
	from_score::score as total_score;
from_word_score = ORDER from_word_score BY total_score DESC, score DESC;
rmf ../data/from_word_score.json
STORE from_word_score INTO '../data/from_word_score.json' USING JsonStorage();
