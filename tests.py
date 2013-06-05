import unittest


class InstallSDKTestCase(unittest.TestCase):
    def test_install_sdk(self):
        from appengine import install_sdk

        install_sdk(filename, dest=dest)


if __name__ == "__main__":
    unittest.main()
