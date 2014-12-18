from datetime import datetime
from email.message import Message

import os
import tempfile

from tests import BaseTestClasses

class TestBasic(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(TestBasic, self).setUp()
        self.msg = Message()

    def test_dontPrintBody(self):
        (rc, output, error) = self.invokeEmail2PDF(extraParams=['--no-body'])
        self.assertEqual(1, rc)
        self.assertFalse(self.existsByTime())
        self.assertRegex(error, "body.*or.*attachments")

    def test_noheaders(self):
        (rc, output, error) = self.invokeEmail2PDF()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())

    def test_simple(self):
        self.addHeaders()
        (rc, output, error) = self.invokeEmail2PDF()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())

    def test_simple_withinputfile(self):
        self.addHeaders()
        (rc, output, error) = self.invokeEmail2PDF(inputFile=True)
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())

    def test_nosubject(self):
        self.addHeaders("from@example.org", "to@example.org", None)
        (rc, output, error) = self.invokeEmail2PDF()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())

    def test_plaincontent(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())

    def test_plaincontent_poundsign_iso88591(self):
        self.addHeaders()
        path = os.path.join(self.examineDir, "plaincontent_poundsign_iso88591.pdf")
        self.setPlainContent("Hello - this email costs \xa35!", charset="ISO-8859-1")
        (rc, output, error) = self.invokeEmail2PDF(outputFile=path)
        self.assertEqual(0, rc)
        self.assertTrue(os.path.exists(path))

    def test_plaincontent_metadata(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_metadata.pdf")
        (rc, output, error) = self.invokeEmail2PDF(outputFile=path)
        self.assertEqual(0, rc)
        self.assertTrue(os.path.exists(path))
        self.assertEqual("from@example.org", self.getMetadataField(path, "Author"))
        self.assertEqual("to@example.org", self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual("Subject of the email", self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))

    def test_plaincontent_metadata_differentmount(self):
        self.addHeaders("from@example.org")
        self.setPlainContent("Hello!")
        mountPoint2 = tempfile.mkdtemp(dir='/var/tmp')
        if(self.find_mount_point(mountPoint2) != self.find_mount_point(tempfile.tempdir)):
            path = os.path.join(mountPoint2, "plaincontent_metadata_differentmount.pdf")
            (rc, output, error) = self.invokeEmail2PDF(outputFile=path)
            self.assertEqual(0, rc)
            self.assertTrue(os.path.exists(path))
            self.assertEqual("from@example.org", self.getMetadataField(path, "Author"))
        else:
            self.skipTest(mountPoint2 + " and " + tempfile.tempdir + " are on the same mountpoint, test not relevant.")

    def test_noheaders_metadata(self):
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_noheaders_metadata.pdf")
        (rc, output, error) = self.invokeEmail2PDF(outputFile=path)
        self.assertEqual(0, rc)
        self.assertTrue(os.path.exists(path))
        self.assertIsNone(self.getMetadataField(path, "Author"))
        self.assertIsNone(self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual('', self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))

    def test_plaincontent_headers(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF(extraParams=['--headers'])
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())

    def test_plaincontent_notrailingslash(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF(outputDirectory="/tmp")
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime("/tmp"))

    def test_plaincontent_trailingslash(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF(outputDirectory="/tmp")
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime("/tmp/"))

    def test_plaincontent_outputfileoverrides(self):
        filename = os.path.join(self.examineDir, "outputFileOverrides.pdf")
        pathname = tempfile.mkdtemp(dir='/tmp')
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF(outputDirectory=pathname, outputFile=filename)
        self.assertEqual(0, rc)
        self.assertFalse(self.existsByTime(pathname))
        self.assertTrue(os.path.exists(filename))

    def test_plaincontent_dirnotexist(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF(outputDirectory="/notexist/")
        self.assertEqual(2, rc)
        self.assertRegex(error, "(?i)directory.*exist")

    def test_plaincontent_fileexist(self):
        self.setPlainContent("Hello!")
        unused_f_handle, f_path = tempfile.mkstemp()
        try:
            (rc, output, error) = self.invokeEmail2PDF(outputFile=f_path)
            self.assertEqual(2, rc)
            self.assertRegex(error, "file.*exist")
        finally:
            os.unlink(f_path)

    def test_plaincontent_timedfileexist(self):
        self.setPlainContent("Hello!")
        filename1 = self.getTimeStamp(datetime.now()) + ".pdf"
        filename2 = self.getTimeStamp(datetime.now()) + "_1.pdf"
        self.touch(os.path.join(self.workingDir, filename1))
        (rc, output, error) = self.invokeEmail2PDF()
        self.assertEqual(0, rc)
        self.assertTrue(os.path.join(self.workingDir, filename1))
        self.assertTrue(os.path.join(self.workingDir, filename2))

    def test_verbose(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF(extraParams=['-v'])
        self.assertEqual(0, rc)
        self.assertNotEqual('', error)

    def test_veryverbose(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeEmail2PDF(extraParams=['-vv'])
        self.assertEqual(0, rc)
        self.assertNotEqual('', error)
