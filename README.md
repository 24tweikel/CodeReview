# CodeReview
Code Review Workflow for IT Programming at BCTC West

## Abstract 
### Flow 
Through this web interface, students will be able to request a code reviews and enter them into a bounty-like system. Seniors will then be notified of this post and a senior can claim a review.  After the review has concluded the senior then fills out a rubric and enters their addional notes/comments. Finally the instructor will then be able to take that data and enter the grades into another grading system accordingly.
### UI
Basic material design layout and UI with primary, secandary, and accent colors. 

## Technical 
Using active directory, users will login to post request for reviews, on posting an email will be sent to seniors and the instructor.  Once a senior accepts the review, the instructor will receive an email. Upon completion of the code review, the instructor will get a final email with the notes the senior has given.

### Services Used 
- [Python](https://www.python.org/) 
- [Django](https://www.djangoproject.com/) 
- [ActiveDirectory](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)
- [lapd3](https://pypi.org/project/ldap3/)
- [Jquery](https://jquery.com/)

## Running  
### Development  
Set the env variable DEV_HOST to the host you want to host in development  
Then, simply run the django run command:  
``` python manage.py runserver YOUR_HOST:8080 ``` 
Development is insecure and inefficient, only use when testing
### Production
Will require an SQL server to connect to, an ActiveDirectory server, an email to send notifications from, and a webserver to run the django code on.  
Setup your webserver and then point it to ``` CodeReview/wsgi.py ```  