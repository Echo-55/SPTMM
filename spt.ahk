#NoEnv
#SingleInstance, Force
SendMode, Input
SetBatchLines, -1
SetWorkingDir, F:\aaSPTMM\SPTMM

Menu, Tray, Icon, I:\Radial menu v4\Icons\SPT.png
Menu, Tray, Tip, SPT Launcher

Run %ComSpec% /c "J:\aaSPTMM\SPTMM\.sptmenu\Scripts\python.exe J:\aaSPTMM\SPTMM\spt.py",,Hide

ExitApp
