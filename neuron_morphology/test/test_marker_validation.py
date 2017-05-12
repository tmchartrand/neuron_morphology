from neuron_morphology import morphology
from neuron_morphology.test.data import test_marker
from neuron_morphology.test.data import test_node
from neuron_morphology.validation import marker_validation as mv
from neuron_morphology.test.validation_test_case import ValidationTestCase
from neuron_morphology.constants import *
import unittest
from mock import patch


class TestMarkerValidationFunctions(ValidationTestCase):
    """ Tests the functions in marker_validation.py """

    def test_validate_expected_name_valid(self):
        for marker_name in [CUT_DENDRITE, NO_RECONSTRUCTION, TYPE_30]:
            errors = mv.validate_expected_name([test_marker(name=marker_name)])
            self.assertEqual(len(errors), 0)

    def test_validate_expected_name_invalid(self):
        errors = mv.validate_expected_name([test_marker(name=5)])
        self.assertMarkerErrors(errors, "Marker name needs to be one of these values:", [test_marker(name=5)])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_cut_dendrite_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            test_morphology = morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                                    , test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
                                                    , strict_validation=False)
            mv.validate([test_marker(x=0, y=0, z=0, name=CUT_DENDRITE)], test_morphology)

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_cut_dendrite_invalid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            test_morphology = morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                                    , test_node(id=2, type=dendrite_type, x=0, y=0, z=0
                                                                , parent_node_id=1)]
                                                    , strict_validation=False)
            errors = mv.validate([test_marker(x=1, y=0, z=0, name=10)], test_morphology)

            self.assertMarkerErrors(errors, "Coordinates for each dendrite (type 10) needs to correspond to a tip of a"
                                            " dendrite type (type 3 or 4) in the related morphology", [test_marker(x=1
                                                                                                    , y=0, z=0
                                                                                                    , name=CUT_DENDRITE)])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_type_20_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            test_morphology = morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                                    , test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
                                                    , strict_validation=False)
            mv.validate([test_marker(x=1, y=0, z=0, name=NO_RECONSTRUCTION)], test_morphology)

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_type_30_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            test_morphology = morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                                    , test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
                                                    , strict_validation=False)
            mv.validate([test_marker(x=1, y=0, z=0, name=TYPE_30)], test_morphology)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMarkerValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
