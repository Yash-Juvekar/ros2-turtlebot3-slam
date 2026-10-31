from setuptools import find_packages, setup

package_name = 'my_first_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yash-Juvekar',
    maintainer_email='yashjuvekar13@gmail.com',
    description='TurtleBot3 simulation nodes: velocity publisher, odometry subscriber and LiDAR obstacle avoider',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'circle_driver = my_first_pkg.circle_driver:main',
            'odom_listener = my_first_pkg.odom_listener:main',
            'obstacle_avoider = my_first_pkg.obstacle_avoider:main',
        ],
    },
)
