# help_desk_service
System for help desk with telegram bot and web access for working with tickets.
User use telegram bot for send a ticket to help desk with text or image info and then this ticke load to database.
Support employe see all open (or closed) tickets in web interface and may be working with them.

## Content
- bot_telebot.py - this scipt for start telegram bot
- sheduler_for_response_bot.py - this script for start sender for answewr when ticket is closed support employe
- webapp.py - this python script for start web application for view recived tichets
- bot_support.sql - script for create database 

  For start service you need start all this three python script.
  And also you must create database for service whene will be save all data this service.

  
