from setuptools import find_packages, setup

package_name = 'nn_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/nn_bot_launch.py',
             'launch/collect_data_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='username',
    maintainer_email='username@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'nn_controller_node = nn_controller.nn_controller_node:main',
            'data_collector_node = nn_controller.data_collector_node:main',
        ],
    },
)
