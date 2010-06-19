"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from models import Node, Subject, Period, Assignment, AssignmentGroup, Delivery



class TestBaseNode(TestCase):
    fixtures = ['testusers.json', 'testnodes.json', 'testsubjects.json']

    def setUp(self):
        self.thesuperuser= User.objects.get(username='thesuperuser')
        self.uioadmin = User.objects.get(username='uioadmin')
        self.uioadmin = User.objects.get(username='uioadmin')
        self.ifiadmin = User.objects.get(username='ifiadmin')
        self.uio = Node.objects.get(pk=1)
        self.ifi = Node.objects.get(pk=2)

    def test_is_admin(self):
        self.assertTrue(self.uio.is_admin(self.uioadmin))
        self.assertFalse(self.uio.is_admin(self.ifiadmin))
        self.assertTrue(self.ifi.is_admin(self.uioadmin))
        self.assertTrue(self.ifi.is_admin(self.ifiadmin))

    def test_get_admins(self):
        def split_and_sort(admins):
            l = admins.split(', ')
            l.sort()
            return ', '.join(l)
        self.assertEquals(self.uio.get_admins(), 'uioadmin')
        self.assertEquals(split_and_sort(self.ifi.get_admins()),
                'ifiadmin, ifitechsupport')

    def test_can_save(self):
        self.assertTrue(self.uio.can_save(self.uioadmin))
        self.assertFalse(self.uio.can_save(self.ifiadmin))
        self.assertTrue(self.ifi.can_save(self.ifiadmin))
        self.assertTrue(self.ifi.can_save(self.uioadmin))
        self.assertTrue(Node().can_save(self.thesuperuser))

    def test_can_save_id_none(self):
        deepdummy1 = Node.objects.get(pk=4)
        self.assertTrue(Subject(parentnode=deepdummy1).can_save(self.uioadmin))
        self.assertFalse(Subject(parentnode=deepdummy1).can_save(self.ifiadmin))



class TestNode(TestCase):
    fixtures = ['testusers.json', 'testnodes.json']

    def setUp(self):
        self.uioadmin = User.objects.get(username='uioadmin')
        self.ifiadmin = User.objects.get(username='ifiadmin')
        self.uio = Node.objects.get(pk=1)
        self.ifi = Node.objects.get(pk=2)
        self.deepdummy1 = Node.objects.get(pk=4)
        self.deepdummy3 = Node.objects.get(pk=6)

    def test_unique(self):
        n = Node(parentnode=self.deepdummy1, short_name='ifi', long_name='Ifi')
        n.save()
        n.parentnode = self.uio
        self.assertRaises(IntegrityError, n.save)

    def test_can_save(self):
        self.assertFalse(Node().can_save(self.ifiadmin))

    def test_unicode(self):
        self.assertEquals(unicode(self.deepdummy3),
                'uio.deepdummy1.deepdummy2.deepdummy3')

    def test_get_path(self):
        self.assertEquals(self.uio.get_path(), 'uio')
        self.assertEquals(self.ifi.get_path(), 'uio.ifi')
        self.assertEquals(self.deepdummy3.get_path(),
                'uio.deepdummy1.deepdummy2.deepdummy3')

    def test_iter_childnodes(self):
        self.assertEquals([n.short_name for n in self.deepdummy1.iter_childnodes()],
                [u'deepdummy2', u'deepdummy3'])

        s = set([n.short_name for n in self.uio.iter_childnodes()])
        self.assertEquals(s,
                set([u'deepdummy1', u'deepdummy2', u'deepdummy3', u'fys', u'ifi']))

    def test_clean_parent_is_child(self):
        """ Can not be child of it's own child. """
        self.uio.parentnode = self.ifi
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_parent_is_self(self):
        """ Can not be child of itself. """
        self.uio.parentnode = self.uio
        self.assertRaises(ValidationError, self.uio.clean)

    def test_clean_noerrors(self):
        self.ifi.clean()

    def test_create_multiple_roots(self):
        n = Node(short_name='test', long_name='Test', parentnode=None)
        n.clean()
        n.save()
        n2 = Node(short_name='test2', long_name='Test2', parentnode=None)
        n2.clean()
        n2.save()

    def test_where_is_admin(self):
        self.assertEquals(Node.where_is_admin(self.uioadmin).count(), 6)
        self.assertEquals(Node.where_is_admin(self.ifiadmin).count(), 1)

    def test_get_pathlist_kw(self):
        self.assertEquals(
                Node._get_pathlist_kw(['uio', 'deepdummy1', 'deepdummy2', 'deepdummy3']), {
                'short_name': 'deepdummy3',
                'parentnode__short_name': 'deepdummy2',
                'parentnode__parentnode__short_name': 'deepdummy1',
                'parentnode__parentnode__parentnode__short_name': 'uio'})

    def test_get_by_pathlist(self):
        self.assertEquals(
                Node.get_by_pathlist(['uio', 'deepdummy1', 'deepdummy2']).short_name,
                'deepdummy2')
        self.assertRaises(Node.DoesNotExist, Node.get_by_pathlist,
                ['uio', 'deepdummy1', 'nonode'])

    def test_get_by_path(self):
        self.assertEquals(Node.get_by_path('uio.deepdummy1.deepdummy2').short_name,
                'deepdummy2')
        self.assertRaises(Node.DoesNotExist, Node.get_by_path,
                'uio.deepdummy1.nonode')

    def test_create_by_pathlist(self):
        n = Node.create_by_pathlist(['this', 'is', 'a', 'test'])
        self.assertEquals(n.short_name, 'test')
        Node.get_by_path('this.is.a.test') # Tests if it has been saved

    def test_create_by_path(self):
        n = Node.create_by_path('this.is.a.test')
        self.assertEquals(n.short_name, 'test')
        Node.get_by_path('this.is.a.test') # Tests if it has been saved

    def test_get_nodepks_where_isadmin(self):
        uioadmin = User.objects.get(username='uioadmin')
        pks = Node._get_nodepks_where_isadmin(uioadmin)
        self.assertEquals(set(pks), set([1,2,3,4,5,6]))



class TestSubject(TestCase):
    fixtures = ['testusers.json', 'testnodes.json', 'testsubjects.json']

    def test_unique(self):
        s = Subject(parentnode=Node.objects.get(short_name='ifi'),
                short_name='inf1060', long_name='INF1060')
        self.assertRaises(IntegrityError, s.save)

    def test_unique2(self):
        s = Subject(parentnode=Node.objects.get(short_name='uio'),
                short_name='inf1060', long_name='INF1060')
        self.assertRaises(IntegrityError, s.save)

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(Subject.where_is_admin(teacher1).count(), 1)
        self.assertEquals(Subject.where_is_admin(uioadmin).count(), 2)



class TestPeriod(TestCase):
    fixtures = ['testusers.json', 'testnodes.json', 'testsubjects.json',
            'testperiods.json']

    def test_unique(self):
        n = Period(parentnode=Subject.objects.get(short_name='inf1100'),
                short_name='old', long_name='Old',
                start_time=datetime.now(),
                end_time=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def test_where_is_admin(self):
        uioadmin = User.objects.get(username='uioadmin')
        self.assertEquals(Period.where_is_admin(uioadmin).count(), 2)


class TestAssignment(TestCase):
    fixtures = ['testusers.json', 'testnodes.json', 'testsubjects.json',
            'testperiods.json', 'testassignments.json',
            'testassignmentgroups.json']

    def test_unique(self):
        n = Assignment(parentnode=Period.objects.get(short_name='looong'),
                short_name='oblig1', long_name='O1',
                publishing_time=datetime.now(),
                deadline=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def test_where_is_admin(self):
        ifiadmin = User.objects.get(username='ifiadmin')
        self.assertEquals(Assignment.where_is_admin(ifiadmin).count(), 3)

    def test_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Assignment.where_is_examiner(examiner1)
        self.assertEquals(q[0].short_name, 'oblig1')
        self.assertEquals(q.count(), 1)

    def test_assignment_groups_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(3,
                oblig1.assignment_groups_where_is_examiner(examiner2)[0].id)
        self.assertEquals(2,
                oblig1.assignment_groups_where_is_examiner(examiner1).count())


class TestAssignmentGroup(TestCase):
    fixtures = ['testusers.json', 'testnodes.json', 'testsubjects.json',
            'testperiods.json', 'testassignments.json',
            'testassignmentgroups.json', 'testcandidates.json']

    def test_where_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        self.assertEquals(5, AssignmentGroup.where_is_admin(teacher1).count())

    def test_where_is_student(self):
        student2 = User.objects.get(username='student2')
        student1 = User.objects.get(username='student1')
        self.assertEquals(1, AssignmentGroup.where_is_student(student2).count())
        self.assertEquals(3, AssignmentGroup.where_is_student(student1).count())

    def test_published_where_is_student(self):
        student2 = User.objects.get(username='student2')
        student3 = User.objects.get(username='student3')
        self.assertEquals(1,
                AssignmentGroup.published_where_is_student(student2).count())
        self.assertEquals(2,
                AssignmentGroup.published_where_is_student(student3).count())

    def test_active_where_is_student(self):
        student2 = User.objects.get(username='student2')
        student3 = User.objects.get(username='student3')
        self.assertEquals(1,
                AssignmentGroup.active_where_is_student(student2).count())
        self.assertEquals(2,
                AssignmentGroup.active_where_is_student(student3).count())

    def test_old_where_is_student(self):
        student1 = User.objects.get(username='student1')
        student4 = User.objects.get(username='student4')
        self.assertEquals(2,
                AssignmentGroup.old_where_is_student(student1).count())
        self.assertEquals(1,
                AssignmentGroup.old_where_is_student(student4).count())


    def test_where_is_examiner(self):
        examiner2 = User.objects.get(username='examiner2')
        examiner4 = User.objects.get(username='examiner4')
        self.assertEquals(1,
                AssignmentGroup.where_is_examiner(examiner2).count())
        self.assertEquals(2,
                AssignmentGroup.where_is_examiner(examiner4).count())

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        self.assertEquals(1,
                AssignmentGroup.published_where_is_examiner(examiner2).count())
        self.assertEquals(2,
                AssignmentGroup.published_where_is_examiner(examiner1).count())

    def test_active_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        self.assertEquals(1,
                AssignmentGroup.active_where_is_examiner(examiner2).count())
        self.assertEquals(2,
                AssignmentGroup.active_where_is_examiner(examiner1).count())

    def test_old_where_is_examiner(self):
        examiner3 = User.objects.get(username='examiner3')
        examiner4 = User.objects.get(username='examiner4')
        self.assertEquals(1,
                AssignmentGroup.old_where_is_examiner(examiner4).count())
        self.assertEquals(2,
                AssignmentGroup.old_where_is_examiner(examiner3).count())


    def test_get_students(self):
        a = AssignmentGroup.objects.get(id=5)
        self.assertEquals('student1, student4', a.get_students())

    def test_get_examiners(self):
        a = AssignmentGroup.objects.get(id=5)
        self.assertEquals('examiner3, examiner4', a.get_examiners())

    def test_is_admin(self):
        teacher1 = User.objects.get(username='teacher1')
        student1 = User.objects.get(username='student1')
        uioadmin = User.objects.get(username='uioadmin')
        a = AssignmentGroup.objects.get(id=1)
        self.assertTrue(a.is_admin(teacher1))
        self.assertFalse(a.is_admin(student1))
        self.assertTrue(a.is_admin(uioadmin))

    def test_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        a = AssignmentGroup.objects.get(id=1)
        self.assertTrue(a.is_examiner(examiner1))
        self.assertFalse(a.is_examiner(examiner2))

    def test_is_student(self):
        student1 = User.objects.get(username='student1')
        student2 = User.objects.get(username='student2')
        a = AssignmentGroup.objects.get(id=1)
        self.assertTrue(a.is_student(student1))
        self.assertFalse(a.is_student(student2))


class TestCandidate(TestCase):
    fixtures = ['testusers.json', 'testnodes.json', 'testsubjects.json',
            'testperiods.json', 'testassignments.json',
            'testassignmentgroups.json', 'testcandidates.json']
    


#class TestDelivery(TestCase):
    #fixtures = ['testusers.json', 'testdata.json']

    #def test_where_is_admin(self):
        #uioadmin = User.objects.get(username='uioadmin')
        #self.assertEquals(Delivery.where_is_admin(uioadmin).count(), 3)

    #def test_where_is_student(self):
        #student2 = User.objects.get(username='student2')
        #self.assertEquals(Delivery.where_is_student(student2).count(), 3)

    #def test_where_is_examiner(self):
        #teacher2 = User.objects.get(username='teacher2')
        #self.assertEquals(Delivery.where_is_examiner(teacher2).count(), 3)

