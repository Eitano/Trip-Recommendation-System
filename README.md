# Trip-Recommendation-System

A worldwide trip planning recommendation system which considers weather forecast, available flights and optional visit locations.

The system was built to create an easy-to-use experience. The user is asked to select the destination and approximate flight dates. The system will query weather data and possible flights to optimize the itinerary. The system presents ranked best fits including maps, flight details and weather info.

This system uniqueness is that it considers weather as part of the itinerary optimization.

The system query weather data from https://www.weatherbit.io/ using standard API, web-scraping on KAYAK website for the available flights and maps using folium.

The data is stored in an SQL data base( MySQL, uses Panda for visualization. 
The user interface to present the recommendations includes maps of the itinerary and uses pop-up-windows to overlay the weather information on the map. 
It should be noted that the web-scraping on KAYAK website includes handling of bot-checks, advertainment pop-up windows and exceptions.



https://nbviewer.org/github/Eitano/Trip-Recommendation-System/blob/main/jupyter%20trust%20notebook-Forcast%26Fly.ipynb%20.ipynb



file:///C:/Users/user/Desktop/Final%20Project,%20207024878,315681767,314977596%20(1)%20(3)/Final%20Project,%20207024878,315681767,314977596/Q1.html
