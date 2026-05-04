
from setuptools import find_packages, setup

package_name = 'hw5_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/hw5_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='eiamw001',
    maintainer_email='eiamw001@umn.edu',
    description='Color-based vision controller for HW5',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'video_publisher = hw5_vision.video_publisher:main',
            'perception_node = hw5_vision.perception_node:main',
            'control_node = hw5_vision.control_node:main',
        ],
    },
)