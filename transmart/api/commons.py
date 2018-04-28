from datetime import datetime

import arrow
from hashlib import sha1

INPUT_DATE_FORMATS = ['D-M-YYYY', 'YYYY-M-D']


def get_dict_identity(dictionary, fields=None):
    """ Calculate a single sha1 for a nested dictionary. """

    identity = sha1()

    def update(value):
        identity.update(str(value).encode())

    def recurse(d):
        for key, value in sorted(d.items()):
            if fields and key not in fields:
                continue

            elif isinstance(value, dict):
                update(key)
                update(get_dict_identity(value, fields))

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        update(get_dict_identity(item, fields))
                    else:
                        update(item)
            else:
                update(key)
                update(value)

    recurse(dictionary)
    return identity.hexdigest()


def date_to_timestamp(date):
    dt = arrow.get(date, INPUT_DATE_FORMATS).datetime
    d = datetime(dt.year, dt.month, dt.day)
    return d.timestamp() * 1000


def filter_tree(tree_dict, counts_per_study_and_concept):
    concepts = set()
    for k, v in counts_per_study_and_concept['countsPerStudy'].items():
        concepts.update(v)

    studies = counts_per_study_and_concept['countsPerStudy'].keys()

    return {k for k, v in tree_dict.items()
            if v.get('conceptCode') in concepts
            and v.get('studyId') in (*studies, None)
            }
