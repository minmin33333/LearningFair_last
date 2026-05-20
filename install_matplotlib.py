import sys
import subprocess

subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])

import matplotlib
print("matplotlib version:", matplotlib.__version__) 
# 최종적으로 matplotlib 버전이 출력되면 정상 설치 완료