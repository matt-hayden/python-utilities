#! env python
"""
http://msdn.microsoft.com/en-us/library/windows/desktop/ms646360%28v=vs.85%29.aspx
"""
import win32con, win32gui
# SC_MONITORPOWER = 0xF170

def ChangeMonitorPower(state = "OFF"):
	MonitorPower_param = { "ON": -1, "LOW": 1, "OFF": 2 }
	win32gui.SendMessage(win32con.HWND_BROADCAST, 
						 win32con.WM_SYSCOMMAND, 
						 win32con.SC_MONITORPOWER, 
						 MonitorPower_param[state.upper()])
ChangeMonitorPower("off")
