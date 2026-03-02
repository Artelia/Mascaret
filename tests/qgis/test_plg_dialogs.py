# -*- coding: utf-8 -*-

from qgis.testing import start_app, unittest

from Mascaret.MascPlugDialog import MascPlugDialog

start_app()


class DialogsTest(unittest.TestCase):
    def test_culvert_manager_dialog(self):
        dlg = MascPlugDialog(self.iface)
        dlg.show()



# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
