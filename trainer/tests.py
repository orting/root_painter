"""
Run tests

Copyright (C) 2020 Abraham George Smith

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import pytest
import pathlib

test_dir = pathlib.Path.cwd() / 'tests'
os.chdir(test_dir)

# example showing how to run an individual test
# import sys
# sys.path.insert(1, 'tests')
# from test_segment import test_CNN_segment_classes_3D
# test_CNN_segment_classes_3D()

pytest.main()
