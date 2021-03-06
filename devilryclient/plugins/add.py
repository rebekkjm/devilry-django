#!/usr/bin/env python

from devilryclient.utils import findconffolder, get_config, get_metadata, get_metadata_from_path, save_metadata
from os.path import dirname, sep, join, exists
from os import getcwd


class DevilryClientAdd(object):
    """Mark a feedback as done and ready for upload"""

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())
        self.metadata = get_metadata()

    def set_and_save(self):
        metanode = get_metadata_from_path(getcwd(), self.metadata)
        metanode['.meta']['done'] = True
        save_metadata(self.metadata)

    def check_context(self):

        split_path = getcwd().replace(self.root_dir, '').split(sep)

        # 7 is the depth for deliveries:
        # <root_dir>/subject/period/assignment/assignmentgroup/deadline/delivery/
        # There should be a 'feedback.rst' at this depth
        if len(split_path) < 7:
            print "This directory is not a delivery directory.", "'" + sep.join(split_path) + "'"
            return

        feedback = join(self.root_dir, sep.join(split_path[1:7]), 'feedback')
        print feedback
        if exists(feedback):
            self.set_and_save()
            print "Added"
        else:
            print "feedback not found in:", dirname(feedback)

    def run(self):
        self.check_context()


if __name__ == '__main__':
    DevilryClientAdd().run()
