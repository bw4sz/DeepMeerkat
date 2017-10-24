import subprocess
from distutils.command.build import build as _build
import setuptools

class build(_build):
  sub_commands = _build.sub_commands + [('CustomCommands', None)]

class CustomCommands(setuptools.Command):

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def RunCustomCommand(self, command_list):
    print('Running command: %s' % command_list)
    p = subprocess.Popen(
        command_list,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_data, _ = p.communicate()
    print('Command output: %s' % stdout_data)
    if p.returncode != 0:
      raise RuntimeError(
          'Command %s failed: exit code: %s' % (command_list, p.returncode))

  def run(self):
    for command in CUSTOM_COMMANDS:
      self.RunCustomCommand(command)

CUSTOM_COMMANDS = [

  #Get cmake and git
  ['apt-get', 'update', '-y'],
  ['apt-get', 'install', '-y' ,'cmake',"unzip",'git','libgtk2.0-dev','pkg-config','libavcodec-dev','libavformat-dev','libswscale-dev'],
  ['git','clone', 'https://github.com/Itseez/opencv.git', '--depth', '1'],
  ['mkdir', 'opencv/build'],
  ['cmake','-Hopencv',"-Bopencv/build", "-DWITH_FFMPEG=ON"],
  ['make','-C', 'opencv/build','-j4'],
  ['make', '-C','opencv/build','install'],
  ['ldconfig']
]

REQUIRED_PACKAGES = ['numpy','tensorflow']

setuptools.setup(
    name='DeepMeerkat',
    version='0.0.1',
    description='Running DeepMeerkat in the Cloud',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
    cmdclass={
        # Command class instantiated and run during pip install scenarios.
          'build': build,
          'CustomCommands': CustomCommands,
      }
)
