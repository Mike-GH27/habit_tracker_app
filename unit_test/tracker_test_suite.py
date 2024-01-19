import unittest
import test_tracker
import test_analytics
import test_databaseSQL
import test_util


def suite():
    my_suite = unittest.TestSuite()
    my_suite.addTest(unittest.TestLoader().loadTestsFromModule(test_tracker))
    my_suite.addTest(unittest.TestLoader().loadTestsFromModule(test_analytics))
    my_suite.addTest(unittest.TestLoader().loadTestsFromModule(test_databaseSQL))
    my_suite.addTest(unittest.TestLoader().loadTestsFromModule(test_util))
    return my_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
