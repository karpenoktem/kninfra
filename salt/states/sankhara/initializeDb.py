#!/usr/bin/env python

import os.path
import sys

import yaml
import bson
import pymongo

MONGO_DATABASE = 'kn'
MONGO_HOST = 'localhost'
DB_FILE = '/home/infra/initial-db.yaml'

yaml.SafeLoader.add_constructor('!id',
        lambda loader, node: bson.objectid.ObjectId(
                        loader.construct_scalar(node)))


def main():
    conn = pymongo.Connection(MONGO_HOST)
    db = conn[MONGO_DATABASE]
    with open(DB_FILE) as f:
        dump = yaml.safe_load(f)
    for collection in dump:
        db.drop_collection(collection)
        for d in dump[collection]:
            db[collection].insert(d)

if __name__ == '__main__':
    main()
