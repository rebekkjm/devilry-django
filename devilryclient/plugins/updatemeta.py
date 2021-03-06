#!/usr/bin/env python
from devilryclient.utils import findconffolder, get_config, get_metadata, deadline_unformat, is_late
from os.path import dirname, join, sep, exists, basename
from os import listdir, getcwd
import time
from datetime import datetime


class DevilryClientUpdateMeta(object):
    """
    Traverse meta tree and make various counts and add to .meta dicts
    .meta info is stored in the same level as the corresponding nodes. So metadata[subject]['.meta']
    holds the counters for a given subject
    """

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())
        self.metadata = get_metadata()
        self.num_groups = 0
        self.num_subjects = 0
        self.num_deliveries = 0
        self.num_feedbacks = 0
        groups_subject = 0
        groups_period = 0
        groups_assignment = 0

        #TODO somehow reset all metadata counters to 0

        #assignment_group.candidate list
        #antall deliveries i hvert nivaa
        #antall assignmentgroups i hvert nivaa
        #antall feedbacks
        #antall late deliveries

    def depth(self, path):
        return len(path.split(sep))

    def run(self):

        methods = {
            1: self.subject_meta,
            2: self.period_meta,
            3: self.assignment_meta,
            4: self.group_meta,
            5: self.deadline_meta,
            6: self.delivery_meta
            }

        # sort the keys by increasing depth
        for key in sorted(self.metadata.keys(), key=lambda path: len(path.split(sep))):
            if key == '.meta':
                continue
            print key
            methods[self.depth(key)](key)

    def subject_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]['.meta']
        try:
            meta['num_subjects'] += 1
        except KeyError:
            meta['num_subjects'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['num_periods'] = 0
        meta['num_corrected'] = 0
        meta['num_groups'] = 0
        meta['num_assignments'] = 0

    def period_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]['.meta']
        meta['num_groups'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['num_assignments'] = 0

    def assignment_meta(self, path):
        meta = self.metadata[path]['.meta']
        meta['num_groups'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0

        # update upwards
        while dirname(path) != '':
            path = dirname(path)
            self.metadata[path]['.meta']['num_assignments'] += 1

    def group_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]['.meta']
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0

        # update upwards
        while dirname(path) != '':
            path = dirname(path)
            self.metadata[path]['.meta']['num_groups'] += 1

        # subject = path_dict['subject']
        # period = path_dict['period']
        # assignment = path_dict['assignment']
        # groups = self.metadata[subject][period][assignment]
        # groups['.meta']['num_assignmentgroups'] = 0 #for assignment
        # for group in groups.keys():
        #     if group[0] != '.':
        #         path_dict['group'] = group
        #         self.metadata['.meta']['num_assignmentgroups'] += 1
        #         self.metadata[subject]['.meta']['num_assignmentgroups'] += 1
        #         self.metadata[subject][period]['.meta']['num_assignmentgroups'] += 1
        #         self.metadata[subject][period][assignment]['.meta']['num_assignmentgroups'] += 1
        #         self.deadline_meta(path_dict)

    def deadline_meta(self, path):
        self.metadata[path]['deadline'] = deadline_unformat(basename(path)[2:])

    def delivery_meta(self, path):
        # subject = path_dict['subject']
        # period = path_dict['period']
        # assignment = path_dict['assignment']
        # group = path_dict['group']
        # deadline = path_dict['deadline']
        # deliveries = self.metadata[subject][period][assignment][group][deadline]
        # for delivery in deliveries.keys():
        #     if delivery[0] != '.':
        #         path_dict['delivery'] = delivery
        #         self.file_meta(path_dict)
        # alias to something short
        meta = self.metadata[path]['.meta']
        meta['done'] = "TODO: noooo, we shouldnt overwrite this variable if it existed before sync"
        # meta['deliver_time'] = 
        #is_late(self.metadata[dirname(path)]['deadline'])

    def file_meta(self, path_dict):
        subject = path_dict['subject']
        period = path_dict['period']
        assignment = path_dict['assignment']
        group = path_dict['group']
        deadline = path_dict['deadline']
        delivery = path_dict['delivery']
        files = self.metadata[subject][period][assignment][group][deadline][delivery]
        for f in files['files']:
            print f
            print path_dict
        print self.metadata
            #if deadline[0] != '.':
            #    print deadline
            #    self.count_deliveries(deadlines[deadline])

                            #self.num_periods += 1


if __name__ == '__main__':
    DevilryClientUpdateMeta().run()
