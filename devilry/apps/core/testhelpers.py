from datetime import datetime, timedelta
import unittest
import os

from django.contrib.auth.models import User
from django.conf import settings

import gradeplugin
from models import Node, Subject, Period, Assignment, AssignmentGroup, \
        Delivery, FileMeta, Candidate
from deliverystore import FileNotFoundError
from testhelper import TestHelper


def create_from_path(path, grade_plugin_key=None, gradeplugin_maxpoints=0):
    """ Create a Node, Subject, Period, Assignment or AssignmentGroup from
    ``path``.

    :param grade_plugin_key: Key of the grade plugin to use on assignments.
        This defaults to the default grade plugin.
    :param gradeplugin_maxpoints: The ``points`` parameter sent to
        :meth:`gradeplugin.GradeModel.init_example` if creating a
        assignment.
    
    Examples::

        assignmentgroup = create_from_path(
                'ifi:inf1100.spring05.oblig1.student1,student2')
        oblig1 = create_from_path(
                'ifi:inf1100.spring05.oblig1')
    """
    split = path.split(':', 1)
    nodes = split[0].split('.')
    for nodename in nodes:
        node = Node(short_name=nodename, long_name=nodename.capitalize())
        try:
            node.clean()
            node.save()
        except:
            node = Node.objects.get(short_name=nodename)
        last = node

    if len(split) != 2:
        return last
    pathsplit = split[1].split('.')

    # Subject
    subjectname = pathsplit[0]
    subject = Subject(parentnode=node, short_name=subjectname,
            long_name=subjectname.capitalize())
    try:
        subject.clean()
        subject.save()
    except:
        subject = Subject.objects.get(short_name=subjectname)
    last = subject

    # Period
    if len(pathsplit) > 1:
        periodname = pathsplit[1]
        period = Period(parentnode=subject, short_name=periodname,
                long_name=periodname.capitalize(), start_time=datetime.now(),
                end_time=datetime.now() + timedelta(10))
        try:
            period.clean()
            period.save()
        except:
            period = Period.objects.get(parentnode=subject,
                    short_name=periodname)
        last = period

    # Assignment
    if len(pathsplit) > 2:
        assignmentname = pathsplit[2]
        assignment = Assignment(parentnode=period, short_name=assignmentname,
                long_name=assignmentname.capitalize(), publishing_time=datetime.now())
        gp = grade_plugin_key or gradeplugin.registry.getdefaultkey()
        assignment.grade_plugin = gp
        
        assignment.clean()
        try:
            assignment.save()
        except:
            assignment = Assignment.objects.get(parentnode=period,
                    short_name=assignmentname)
        last = assignment

    # Candidates
    if len(pathsplit) > 3:
        usernames = pathsplit[3].split(',')
        users = []
        for u in usernames:
            user = User(username=u)
            try:
                user.save()
            except:
                user = User.objects.get(username=u)
            users.append(user)
        assignment_group = AssignmentGroup(parentnode=assignment)
        assignment_group.clean()
        assignment_group.save()
        for user in users:
            assignment_group.candidates.add(Candidate(student=user))
        last = assignment_group
    return last


class TestDeliveryStoreMixin(TestHelper):
    """ Mixin-class that tests if
    :class:`devilry.core.deliverystore.DeliveryStoreInterface` is
    implemented correctly.

    You only need to override
    :meth:`get_storageobj`, and maybe :meth:`setUp` and :meth:`tearDown`,
    but make sure you call ``super(..., self).setUp()`` if you override it.
    
    You **must** mixin this class before :class:`django.test.TestCase` like
    so::

        class TestMyDeliveryStore(TestDeliveryStoreMixin, django.test.TestCase):
            ...
    """

    def get_storageobj(self):
        """ Return a object implementing
        :class:`devilry.core.deliverystore.DeliveryStoreInterface` """
        raise NotImplementedError()

    def setUp(self):
        """ Make sure to call this if you override it in subclasses, or the
        tests **will fail**. """
        self.add(nodes="uio.ifi",
                 subjects=["inf1100"],
                 periods=["period"],
                 assignments=["assignment1"],
                 assignmentgroups=["g1:candidate(student1)"])
        # file and verdict
        self.goodFile = {"good.py": "print awesome"}
        d = self.add_delivery("inf1100.period.assignment1.g1", self.goodFile)
        self.filemeta = FileMeta()
        self.filemeta.delivery = d
        self.filemeta.size = 0
        self.filemeta.filename = 'test.txt'

    def test_writemany(self):
        store = self.get_storageobj()
        w = store.write_open(self.filemeta)
        w.write('hello')
        w.write(' world')
        w.write('!')
        w.close()
        r = store.read_open(self.filemeta)
        self.assertEquals(r.read(), 'hello world!')

    def test_readwrite(self):
        store = self.get_storageobj()
        self.assertFalse(store.exists(self.filemeta))
        self.assertRaises(FileNotFoundError, store.read_open, self.filemeta)
        w = store.write_open(self.filemeta)
        w.write('hello')
        w.close()
        self.assertTrue(store.exists(self.filemeta))
        store.remove(self.filemeta)
        self.assertFalse(store.exists(self.filemeta))
        self.assertRaises(FileNotFoundError, store.remove, self.filemeta)


class SeleniumTestBase(unittest.TestCase):
    fixtures = []

    def clear_testdb(self):
        os.system('git checkout deliverystore.dbm.dat')
        os.system('git checkout deliverystore.dbm.dir')
        if os.path.exists(settings.DATABASE_NAME):
            os.remove(settings.DATABASE_NAME)
        os.system('python manage.py syncdb --noinput')

    def load_fixtures(self):
        if not self.fixtures:
            raise ValueError("No fixtures in testcase: %s." %
                    self.__class__.__name__)
        self.clear_testdb()
        os.system('python manage.py loaddata -v0 %s' % \
                ' '.join(self.fixtures))

    def assert403(self, f, *args, **kw):
        try:
            f(*args, **kw)
        except Exception, e:
            self.assertTrue("403" in str(e))
            self.assertTrue("FORBIDDEN" in str(e))
        else:
            self.fail("403 not raised for %s, %s, %s" % (f, args, kw))



