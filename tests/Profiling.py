import pstats
import subprocess
import os

os.getcwd()

#Profile
subprocess.check_output(['python', '-m','cProfile','-o','output.txt', '../DeepMeerkat/Meerkat.py','--input','../DeepMeerkat/Hummingbird.avi'])
#subprocess.check_output(['python', '-m','cProfile','-o','output.txt', '../DeepMeerkat/Predict.py'])

p = pstats.Stats("output.txt")
p.sort_stats("tottime").strip_dirs().print_stats()

#gprof2dot -f pstats output.txt| dot -Tpng -o output.png

