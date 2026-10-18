from .base import TestCases
from src.kinematics import LocalFrameBuilder
import numpy as np

class TestBuildLocalFrame(TestCases):
    def setup_method(self):
        self.base_vec =  [1,0,0]
        self.ref_vec = [0,1,0]
        
        self.expected_x = [1,0,0]
        self.expected_y = [0,1,0]
        self.expected_z = [0,0,1]

        self.shape_r = 3
        self.shape_c = 3

        self.R = LocalFrameBuilder(
            base_vec=self.base_vec,
            ref_vec=self.ref_vec
        ).process()

    def _shape_check(self):        
        assert self.R.shape == (self.shape_r, self.shape_c), (
            f"Shape Check: Not meet expected shape: \n"
            f"Expected Shape: {(self.shape_r, self.shape_c)} \n"
            f"Actual Shape: {self.R.shape}"
        )

    def _expected_run_check(self):
        expected_R = np.column_stack([self.expected_x, self.expected_y, self.expected_z])

        assert np.allclose(self.R, expected_R, atol=1e-6) , (
            f"Expected Result Check: result of R is not meet the expected result: \n"
            f"Expected Result: {expected_R} \n"
            f"Actual Result: {self.R}"
        )
        
    def run(self):
        self._shape_check()
        self._expected_run_check()
        print("[PASSED] TestBuildLocalFrame")

    def test_run(self):
        self.run()
