# Social Checkin Policies
Learn from other people and decide checkin policy for different locations and companions
  
### To Run the program  
I have tested the command on UBUNTU 16.04. Run these commands before running the program   
``` sudo apt-get update   
sudo apt-get install python3    
sudo apt-get install python-pip   
pip install requests   
pip install numpy   
pip install sklearn   
```   
Run the program using `python checkin.py`  
API for data of user check-ins and other information is [this](http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp)   
I have hardcoded the `user = 16` in the code. Since I have assumed that this program is just for this user. Change it to test accordingly. Use numbers everywhere instead of words/names.   
The program will prompt necessary inputs.   
`Ctrl+C` to exit from the program.   
   
### Check-In Policy  
    
**Goals:**   
Stakeholders: (Assigned in order of importance)   
Primary:   	
1. Safety   
2. Privacy   
3. Fame   
Secondary:	
1. Safety   
2. Privacy   
3. Not Spoil Fun   		
  
**Plans:**   
Primary:	1. Safety -> Share with friends
			2. Privacy -> share with companions/ share with no one
			3. Fame -> Share with all
Secondary:	 
|    Primary plans:     |    Share with friends    |    share with no one    |    Share with companions    |    Share with all    |
|-----------------------|--------------------------|-------------------------|-----------------------------|----------------------|
|    Safety             |    Positive              |    Very Negative        |    Neutral                  |    Very Positive     |
|    Privacy            |    Negative              |    Very Positive        |    Positive                 |    Very Negative     |
|    Fame               |    Positive              |    Very Negative        |    Neutral                  |    Very Positive     |
		
		
**Contexts:**
1.	Airport at Night, traveling alone 
-> Share with friends
2.	Bar with fake ID. You wouldn’t want people to know for privacy reasons, also sharing with friends may not be liked by people present at the party 
-> Share with no one
3.	Graduation, no safety or privacy concern. Sharing with everyone makes you famous 
-> Share with all
4.	Library during the day, no safety issue. Depends on companions
->	Share with companions
5.	Hurricane, safety issue
->	Share with all
6.	Hiking on a Mountain
->	Share with friends
7.	Presenting a paper
->	Share with all
  
**Commitments:**  
C(Jeangray; companions; always; share with ‘no one’ OR ‘companions’ is the same)   
C(Jeangray; friends; context = safe but not something to publicize; share = no one) over
C(Jeangray; parents; context = always; share = parents)   
   
**Sanctions:**
If Jeangray is a part of the event and another person shares the event like:
Safety>privacy>fame   
   

|                      | Share All     | Share with Companions | Share with Friend | Share with no one |
|----------------------|---------------|-----------------------|-------------------|-------------------|
| Airport at Night     | Positive      | Neutral               | Very Positive     | Negative          |
| Bar with fake ID     | Very Negative | Positive              | Very Negative     | Very Positive     |
| Graduation           | Very Positive | Positive              | Very Positive     | Neutral           |
| Library during day   | Negative      | Positive              | Neutral           | Very Positive     |
| Hurricane            | Very Positive | Positive              | Positive          | Neutral           |
| Hiking on a Mountain | Positive      | Neutral               | Very Positive     | Negative          |
| Presenting a paper   | Very Positive | Neutral               | Positive          | Neutral           |
