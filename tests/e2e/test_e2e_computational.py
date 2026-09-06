"""A clean installed wheel must reach Publication through explicit CPU workflows."""
import unittest

from tests.e2e.support import InstalledProject


class ComputationalReleaseTests(InstalledProject, unittest.TestCase):
    def test_e2e_computational_wheel_to_final_digest_publication(self):
        self.setup_installed_project()
        self.outer_workflows()
        self.computational_workflows()
        self.publish("empirical-computational", "The fixed CPU baseline MSE is 1.25.")
        self.assertEqual(self.invocations, [
            "research-charter", "research-literature", "research-gap", "research-idea",
            "research-novelty", "research-reflect", "design-experiment", "prepare-experiment",
            "run-experiment", "run-experiment", "analyze-experiment", "assess-result-to-claim",
            "design-experiment", "prepare-experiment",
        ])


if __name__ == "__main__":
    unittest.main()
