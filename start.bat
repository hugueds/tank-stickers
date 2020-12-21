if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit
    conda activate opencv & cd /D app & python main.py & cd ..
exit


Rem conda activate opencv & cd /D app & python main.py --video ../videos/1.mp4
