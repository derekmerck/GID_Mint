"""
GID_Mint
A library and Flask app to create 1-way hashes for study anonymization

[Derek Merck](derek_merck@brown.edu)
Spring 2015

<https://github.com/derekmerck/GID-Mint>

Dependencies: Flask

See README.md for usage, notes, and license info.

"""
import logging
import hashlib
import base64
import csv


__package__ = "GID_Mint"
__description__ = "Flask app to create 1-way hashes for study anonymization"
__url__ = "https://github.com/derekmerck/GID_Mint"
__author__ = 'Derek Merck'
__email__ = "derek_merck@brown.edu"
__license__ = "MIT"
__version_info__ = ('1', '3', '0')
__version__ = '.'.join(__version_info__)


# Setup logging
logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('version %s' % __version__)


# Salting the UID generator will make any id's specific to a particular instance of this script
salt = ''

# First 8 bytes of 32 = 64 bits = 2^64 values
bitspace = 64  # Keeping the id's short has some advantages for usability

# Name file should be definable separately
name_file = "shakespeare_names.csv"


names_dict = {}
with open(name_file, 'rU') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        names_dict[row['Base32']] = row


def get_pname_for_gid(args):
    # TODO: Need some better error checking
    gid = args.get('gid')
    if gid is not None:
        return'^'.join([
            names_dict[gid[0]]['Last'],
            names_dict[gid[1]]['First'],
            names_dict[gid[2]]['Middle'],
            names_dict[gid[3]]['Prefix'],
            names_dict[gid[4]]['Suffix']
            ])
    else:
        return "Request is malformed"


def get_yob_for_dob(args):
    # TODO: Need some better error checking
    dob = args.get('dob')
    if dob is not None:
        return dob[4:]
    else:
        return "Request is malformed"


def get_gid(args, reqs=None):

    # Parse 'pname' into 'fname' and 'lname' if it is declared in args
    if args.get('pname') is not None:
        args['lname'], args['fname'] = args['pname'].split('^')[:2]
        del args['pname']

    if reqs:
        values = check_vars(reqs, args)
    else:
        values = [args[key] for key in sorted(args)]

    if values is not None:
        return hash_it(values)
    else:
        return "Request is malformed"


def check_vars(reqs, args):
    reqs = sorted(reqs)
    # TODO: Should also check correct format for dob (i.e., xx-yy-zzzz), mrn (i.e., 10 digits at Lifespan), ssn, etc.
    values = []
    for key in reqs:
        if key not in args:
            # Failed completeness
            logger.warn("Failed completeness")
            return None
        else:
            values.append(args.get(key, ''))
    return values


def hash_it(values):
    # m = hashlib.md5()
    m = hashlib.sha256()
    for val in values:
        m.update(val.lower())
    m.update(salt)
    # byte slicing -- divide target bitspace by 8
    return base64.b32encode((m.digest()[:bitspace/8])).strip('=')



if __name__ == '__main__':

    args = {'name': 'Derek'}
    gid = get_gid(args)
    logger.info(args)
    logger.info(gid)
    logger.info(get_pname_for_gid({'gid': gid}))

    args = {'pname': 'Merck^Derek^L^^', 'dob': '01011999'}
    gid = get_gid(args)
    logger.info(args)
    logger.info(gid)
    logger.info(get_pname_for_gid({'gid': gid}))

    args = {'fname': 'Derek', 'lname': 'Merck', 'dob': '01011999'}
    gid = get_gid(args)
    logger.info(args)
    logger.info(gid)
    logger.info(get_pname_for_gid({'gid': gid}))

    logger.info(get_yob_for_dob(args))

    args = {'institution': 'RIH', 'record_id': '111222333'}
    gid = get_gid(args)
    logger.info(args)
    logger.info(gid)
