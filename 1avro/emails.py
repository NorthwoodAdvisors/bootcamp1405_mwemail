import email
import email.utils
from HTMLParser import HTMLParser
import time
import avro.schema, avro.datafile, avro.io
import pprint

INPUT_DIR = '../data/emails'
SCHEMA = './email.avsc'
OUTPUT = '../data/emails.avro'

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class AvroMail(object):
    def __init__(self, schema_file, output_file):
        self.output_file = output_file
        schema = avro.schema.parse(open(schema_file).read())
        io_writer = avro.io.DatumWriter(schema)
        self.data_writer = avro.datafile.DataFileWriter(
                open(output_file, 'wb'),
                io_writer,
                schema
                )

    def write_message(self, msg_hash):
        try:
            self.data_writer.append(msg_hash)
            print 'SUCCESS'
        except Exception as e:
            print str(e)
            raise

    def read_back(self):
        self.data_writer.close()
        io_reader = avro.io.DatumReader()
        data_reader = avro.datafile.DataFileReader(
                open(self.output_file),
                io_reader
                )
        pp = pprint.PrettyPrinter()
        for record in data_reader:
            pp.pprint(record)
        data_reader.close()

def main():
    avro_mail_handler = AvroMail(SCHEMA, OUTPUT)
    process_mails(avro_mail_handler)
    avro_mail_handler.read_back()

def process_mails(avro_mail_handler):
    import os
    path = INPUT_DIR
    for dir_entry in os.listdir(path):
        dir_entry_path = os.path.join(path, dir_entry)
        if os.path.isfile(dir_entry_path):
            with open(dir_entry_path, 'r') as my_file:
                #print dir_entry_path
                msg_hash = handle_mail(my_file.read())
                avro_mail_handler.write_message(msg_hash)

def handle_mail(mail):
    msg_hash = hash_message(mail)
    return msg_hash

def hash_message(mail):
    msg_hash = {}
    msg = email.message_from_string(mail)

    msg_subject = msg['Subject']

    msg_from = clean_address(msg.get_all('from', []))

    msg_to = clean_addresses(msg.get_all('to', []))

    msg_cc = clean_addresses(msg.get_all('cc', []))

    msg_date = clean_date(msg['Date'])

    msg_received = msg['Received']

    msg_content_type = msg.get_content_type()
    msg_charset = msg.get_content_charset()
    msg_payload = clean_payload(msg.get_payload(), msg_content_type, msg_charset)

    msg_hash = dict()
    msg_hash['subject'] =  msg_subject
    msg_hash['date'] = msg_date
    msg_hash['tos'] = msg_to
    msg_hash['ccs'] = msg_cc
    msg_hash['from'] = msg_from
    msg_hash['body'] = msg_payload
    return msg_hash

def clean_addresses(addresses):
    retval = []
    addr_list  =  email.utils.getaddresses(addresses)
    for address in addr_list:
        retval.append(address_scrub(address))
    return retval

def clean_address(address):
    retval = {}
    address  =  email.utils.getaddresses(address)
    if len(address) > 0:
        retval = address_scrub(address[0])
    return retval

def address_scrub(address):
    real_name = ''
    email_address = address[1]
    if address[0] != address[1]:
        real_name = address[0]
    t = {'real_name' : real_name, 'address' : email_address}
    return t

def clean_date(date_string):
    tuple_time = email.utils.parsedate(date_string)
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S", tuple_time)
    return iso_time

def clean_payload(payload, content_type, charset):
    if(charset):
        pass
    else:
        charset = 'us-ascii'
    body = payload.decode(charset)
    if content_type == 'text/html':
        body = strip_tags(body)
    return body

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

if __name__ == "__main__":
    main()
