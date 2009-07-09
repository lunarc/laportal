pleaseWaitTemplate = """
<table style="margin-left: auto; margin-right: auto; text-align: left;"
border="0" cellpadding="3" cellspacing="2">
<tbody>
<tr>
<td><img alt=""
src="images/wait1.gif"></td>
<td
style="vertical-align: middle; font-family: tahoma; font-weight: bold;">
<div style="margin-left: 40px;"><big>%(message)s</big></div>
</td>
</tr>
</tbody>
</table>
"""

messageBoxTemplate ="""
<table
style="background-color: rgb(%(tableBgColor)s); margin-left: auto; margin-right: auto; text-align: left; width: %(width)dpx; height: %(height)dpx;"
border="0" cellpadding="3" cellspacing="2">
<tbody>
<tr align="center">
<td
style="background-color: rgb(%(captionBgColor)s); text-align: center; vertical-align: top;"><small><span
style="font-family: tahoma; color: rgb(%(captionTextColor)s); font-weight: bold;">%(caption)s</span></small><br>
</td>
</tr>
<tr>
<td
style="background-color: rgb(%(textBgColor)s); vertical-align: top;"><small><span
style="font-family: tahoma; color: rgb(%(textColor)s)">
<br>
<center>
%(message)s
</center>
<br>
</span></small> </td>
</tr>
</tbody>
</table>
"""

messageBoxWithButtonTemplate ="""
<table
style="background-color: rgb(%(tableBgColor)s); margin-left: auto; margin-right: auto; text-align: left; width: %(width)dpx; height: %(height)dpx;"
border="0" cellpadding="3" cellspacing="2">
<tbody>
<tr align="center">
<td
style="background-color: rgb(%(captionBgColor)s); text-align: center; vertical-align: top;"><small><span
style="font-family: tahoma; color: rgb(%(captionTextColor)s); font-weight: bold;">%(caption)s</span></small><br>
</td>
</tr>
<tr>
<td
style="background-color: rgb(%(textBgColor)s); vertical-align: top;"><small><span
style="font-family: tahoma; color: rgb(%(textColor)s)">
<br>
<center>
%(message)s
</center>
<br>
</span></small>
<br>
<center>
<form method="Post" action="%(action)s">
<input type="submit" value="%(buttonCaption)s">
</form>
</center>
</td>
</tr>
</tbody>
</table>
"""

messageBoxYesNoTemplate ="""
<table
style="background-color: rgb(%(tableBgColor)s); margin-left: auto; margin-right: auto; text-align: left; width: %(width)dpx; height: %(height)dpx;"
border="0" cellpadding="3" cellspacing="2">
<tbody>
<tr align="center">
<td
style="background-color: rgb(%(captionBgColor)s); text-align: center; vertical-align: top;"><small><span
style="font-family: tahoma; color: rgb(%(captionTextColor)s); font-weight: bold;">%(caption)s</span></small><br>
</td>
</tr>
<tr>
<td
style="background-color: rgb(%(textBgColor)s); vertical-align: top;"><small><span
style="font-family: tahoma; color: rgb(%(textColor)s)">
<br>
<center>
%(message)s
</center>
<br>
</span></small>
<br>
<center>
<form method="post">
<input type="submit" value="Yes" name="%(yesMethod)s">
<input type="submit" value="No" name="%(noMethod)s">
</form>
</center>
</td>
</tr>
</tbody>
</table>
"""

