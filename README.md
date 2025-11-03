# hackathon-duck
This project consisted of making an alarm the shape of a duck. 
The original idea was to create a website UI to control the duck which is done in app.py + oldbackend.py.
This website would run on a Rasberry PI and would be attached on the side of the duck to set the alarm.

However, the website UI idea was scrapped due to hardware issues making the website slow.

backend.py is current working code with a GUI made with guizero. It allows users to set a timer and when it rings, will trigger a motor to open the duck mouth.
Speaker.ino is the code for the speaker of the duck which plays a noise after the alarm goes off. The mouth of the duck will close on the press of a button and stop the alarm.

