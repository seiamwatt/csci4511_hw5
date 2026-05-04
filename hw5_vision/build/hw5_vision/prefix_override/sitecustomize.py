import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/eiamw001/ros_hw5/hw5_vision/install/hw5_vision'
