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
  ['apt-get', 'install', '-y', 'cmake', 'git'],
  ['git','clone', 'clone https://github.com/Itseez/opencv.git', '--depth', '1'],
  ['git','clone', 'https://github.com/Itseez/opencv_contrib.git', '--depth', '1'],
  ['cd', 'opencv'],
  ['mkdir', 'build'],
  ['cd', 'build'], 
  ['cmake','..'],
  ['make', '-j4'],
  ['make', 'install'], 
  ['ldconfig']]      

#Install tensorflow
  
REQUIRED_PACKAGES = ['numpy','opencv-python','tensorflow']

setuptools.setup(
    name='DeepMeerkat',
    version='0.0.1',
    description='Running MotionMeerkat in the Cloud',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
    cmdclass={'build': build, 'CustomCommands': CustomCommands})
