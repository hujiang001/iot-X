import unittest
import test_user,test_accesskey,test_device,test_sensor,test_dataset,test_command

def suite():
    suite = unittest.TestSuite([test_user.suite(),
                                test_accesskey.suite(),
                                test_device.suite(),
                                test_sensor.suite(),
                                test_dataset.suite(),
                                test_command.suite()])
    return suite
if __name__=="__main__":
    unittest.main(defaultTest='suite')