from IPython.core.display import display, HTML
display(HTML("<style>div.output_scroll { height: 400em; }</style>"))
display(HTML("<style>.container { width:90% !important; }</style>"))


```python
# import
import datetime
from datetime import timedelta, date
from datetime import datetime

def cast_date(dt):
    """
    casting function
    :return: return date i format of date
    """
    date_str = datetime.strptime(dt, "%d.%m.%Y").strftime("%Y-%m-%d")
    return date(*map(int, date_str.split('-')))


def all_ticket_options():
    """
    function receives input from the user and checks for correctness and adds to the dates 4 days
    ahead and four days later if possible and returns a list of optional days
    :return: list
    """
    departure_from = input("Departure from: ")
    destination = input("Destination: ")
    chosen_day = cast_date(input("Chose day to fly: "))
    return_day = cast_date(input("Chose day to return: "))
    # check if date insert to fly is'nt passed
    today_date = date.today()

    if chosen_day > today_date and return_day > chosen_day and (return_day - chosen_day).days < 16:
        days_travel = (return_day - chosen_day).days
        Max_date_available = today_date + timedelta(days=16)
        optional_days = [departure_from, destination, (str(chosen_day), str(return_day))]

        # calculating end date by adding 4 days
        if (chosen_day - today_date).days < 16:
            days_before = (chosen_day - today_date).days
            if days_before >= 4:
                days_before = 4
            for i in range(1, days_before):
                new_tuple = chosen_day - timedelta(days=i)
                optional_days.append((str(new_tuple), str(new_tuple + timedelta(days=days_travel))))

        if (Max_date_available - chosen_day).days < 16:
            days_after = (Max_date_available - chosen_day).days
            if days_after >= 4:
                days_after = 4
            for i in range(1, days_after):
                new_tuple = chosen_day + timedelta(days=i)
                if new_tuple + timedelta(days=days_travel) > Max_date_available:
                    continue
                else:
                    optional_days.append((str(new_tuple), str(new_tuple + timedelta(days=days_travel))))
        return optional_days
    
```

# import
import requests
from datetime import timedelta, datetime, date
import time
import json
import os
import pandas as pd
from IPython.core.display import display, HTML


class forecast:
    # class forecast process api requests for an estimation the best date for a start the trip 
    
    def __init__(self):
        self.api = '9a136cd7531d4f90b4fc6d074a123b35'
 
    # convert your links to html tags
    @staticmethod
    def path_to_image_html(path):
        return '<img src="' + path + '" width="60" >'

    def avalute(self, list_coord, ls_info):
        """
        function avalutes the best t-map for user to drop markers based on place intended to sleep during trip
        :param list_coord: list of cordinates which are the lan and lon cordinates of markers using draw_on_map function
        :param ls_info: fly ticket information
        :return: best_result- dictionary 
        """
        
        flight_days = sorted(ls_info[2:])
        new_list = []
        '''
        adding and subtracting a day from the dates of the flights
        under the assumption that it takes a day to get to the starting compound and another day to a field field.
        '''
        for elem in range(len(flight_days)):
            fly_start = time.strptime(flight_days[elem][0], '%Y-%m-%d')
            hike_start = date(fly_start.tm_year, fly_start.tm_mon, fly_start.tm_mday) + timedelta(days=1)
            fly_start = str(date(fly_start.tm_year, fly_start.tm_mon, fly_start.tm_mday))

            return_fly = time.strptime(flight_days[elem][1], '%Y-%m-%d')
            hike_end = date(return_fly.tm_year, return_fly.tm_mon, return_fly.tm_mday) - timedelta(days=1)
            return_fly = str(date(return_fly.tm_year, return_fly.tm_mon, return_fly.tm_mday))

            if hike_start + timedelta(days=len(list_coord)) < hike_end:
                new_list.append((str(hike_start), (fly_start, return_fly)))
            else:
                print("User chose too many stations in between dates of the ticket")
                return

        for i in range(len(list_coord)):
            try:
                url = 'https://api.weatherbit.io/v2.0/forecast/daily?&lat={}&lon={}&key={}'.format(list_coord[0][0],
                                                                                                   list_coord[0][1],
                                                                                                   self.api)
                res = requests.get(url)
                self.dict_api = res.json()
                smart_dict = {}

                for event in range(len(new_list)):
                    if event == 0:
                        for index in range(len(self.dict_api['data'])):
                            if self.dict_api['data'][index]['datetime'] == new_list[event][0]:
                                break
                    else:
                        index += 1
                    # setting counter for rain and clouds
                    sum_raining = 0
                    sum_clouds = 0
                    for day_plus in range(len(list_coord)):
                        keys = ['pop', 'precip'] 
                        # add precent and precip values
                        sum_raining = sum_raining + sum(
                            [self.dict_api['data'][index + day_plus].get(key) for key in keys])
                        
                        # add clouds values
                        sum_clouds = sum_clouds + self.dict_api['data'][index + day_plus]['clouds']
                    smart_dict[new_list[event]] = (new_list[event][0], index, sum_raining/len(list_coord),
                                                   sum_clouds/len(list_coord), new_list[event][1]) 
                    # calculate average sum clouds and sum_rain
                    
                # dictionary is sorted by 3 keys: 
                # (first) amount of precipitation (second) clouds (last) earliest date
                best_result = sorted(smart_dict.values(), key=lambda val: (val[2], val[3], val[0]))

            except Exception as e:
                print(e)
                
        return best_result # return a גictionary

    
    def df_forecast(self, lon, lat, index):
        """
        function returns dataframe using the api of the weather forecast for the required period of time
        :param lon: longitude 
        :param lat: latitude
        :param index: center day???????????????????
        :return: first row of df and df.to_html
        """
        try:
            url = 'https://api.weatherbit.io/v2.0/forecast/daily?&lat={}&lon={}&key={}'.format(lon, lat, self.api)
            res = requests.get(url)
            self.dict_api = res.json()
            j = 0
            ls_forecast = []
            for i in range(index, index + 3): #???????????????????????
                self.dict_api['data'][i]['date'] = datetime.strptime(self.dict_api['data'][i]['datetime'],
                                                                     '%Y-%m-%d').date().strftime('%d.%m.%Y')
                self.dict_api['data'][i]['Temp'] = str(self.dict_api['data'][i]['temp']) + "\u00b0"
                self.dict_api['data'][i]['Clouds'] = str(self.dict_api['data'][i]['clouds']) + ' %'
                self.dict_api['data'][i]['Rain Chance'] = str(self.dict_api['data'][i]['pop']) + ' %'
                self.dict_api['data'][i]['Precipitation'] = str(self.dict_api['data'][i]['precip']) + ' mm/hr'

                copy_row = self.dict_api['data'][i]
                wanted_keys = ('date', 'Clouds', 'Temp', 'Rain Chance', 'Precipitation')
                ls_forecast.append(dict(zip(wanted_keys, [copy_row[k] for k in wanted_keys])))

                ls_forecast[j]['Description'] = self.dict_api['data'][i]['weather'].get('description')
                ls_forecast[j]['Status'] = 'https://www.weatherbit.io/static/img/icons/{}.png'.format(
                    self.dict_api['data'][i]['weather'].get('icon'))
                j += 1
                #     min(dict_api['data'], key=lambda x: x['clouds']+ x['pop'] + x['precip'])
                df = pd.DataFrame(ls_forecast)

                df.columns = df.columns.str.title()
                df = df.reindex(['Date', 'Temp', 'Clouds', 'Rain Chance', 'Precipitation', 'Description', 'Status'], axis=1)

                # for i in range(len(ls_forecast)):
                #     df['Description'].values[i] = df['Description'].values[i].title()

                pd.set_option('display.max_colwidth', None)
                pd.set_option('colheader_justify', 'center')
        except Exception as e:
            print(e)

        return df['Date'][0],  df.to_html(escape=False, formatters=dict(Status=self.path_to_image_html))



```python
# import
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import mysql.connector
from dateutil.parser import parse
import pandas as pd
import numpy as np
from time import sleep
from IPython.display import display


class sql_ticket:
    def __init__(self):
        # create connection with database
        DB = mysql.connector.connect(
            host='localhost',
            user='root',
            password='gdwY8RrWw8r',
            port='3306',
            database='python_sql'
        )
        self.db = DB
        self.cursor = DB.cursor()
        # open web driver
        self.chromedriver_path = "C:/Users/user/OneDrive - post.bgu.ac.il/FLY_Project/drivers/chromedriver_win32_92/chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=self.chromedriver_path)

    def isExist(self, values):
        """
        function allows us to know whether to use updating sentence or inserting sentence
        by checking if there is an instance in the db that corresponds to the primary keys
        :param values: primary keys are date and time of fly ticket
        :return: boolean (if appears)
        """
        cursor = self.db.cursor()
        flag = False
        select_query = """ SELECT * 
                           FROM flight_tickets
                           WHERE Depart_Date = %s AND Depart_Time = %s 
                           AND Return_Date = %s AND Return_Time = %s """
        try:
            cursor.execute(select_query, values)
            if len(cursor.fetchall()) != 0:  # Not empty means already exist
                flag = True

        except mysql.connector.Error as err:
            print(err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            self.db.rollback()

        finally:
            return flag

    def sql_to_df(self, query):
        """
        function converts sql to dataframe using pandas and changes the Durations columns from float to str
        :param query: sql query sentence
        :return: display dataframe
        """
        values = self.departure_date, self.return_date, self.flight_from+'%', '%'+self.destination # parms for query are date of fly ticket
        self.cursor.execute(query, values)
        results = self.cursor.fetchall()

        if len(results) != 0:  # if not empty convert

            df = pd.DataFrame.from_records(results, columns=[desc[0] for desc in self.cursor.description])

            df["Duration_1"] = df["Duration_1"].astype(int).astype(str) + 'h ' + round(
                (df["Duration_1"] - np.fix(df["Duration_1"])) * 100).astype(int).astype(str)

            df["Duration_2"] = df["Duration_2"].astype(int).astype(str) + 'h ' + round(
                (df["Duration_2"] - np.fix(df["Duration_2"])) * 100).astype(int).astype(str)

            return display(df)

        else:  # maens there is not match result then no df to display
            print('- No match was found')
            return

    def checkTableExists(self):
        try:
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM flight_tickets 
                """)
            if len(self.cursor.fetchall()) != 0:  # means there are rows which return at fetchall
                return

        except mysql.connector.ProgrammingError as err:  # in case table dosen't exist so create
            self.cursor.execute("""
                  CREATE TABLE `python_sql`.`flight_tickets` (
                  `Depart_Date`DATE NOT NULL,
                  `Depart_Time` VARCHAR(100) NOT NULL,
                  `AirPorts_1` VARCHAR(100) NULL,
                  `Stops_1` VARCHAR(100) NULL,
                  `Duration_1` FLOAT NULL,
                  `Return_Date` DATE NOT NULL,
                  `Return_Time` VARCHAR(100) NOT NULL,
                  `AirPorts_2` VARCHAR(100) NULL,
                  `Stops_2` VARCHAR(100) NULL,
                  `Duration_2` FLOAT NULL,
                  `Price` INTEGER NULL,
                  PRIMARY KEY (`Depart_Date`, `Depart_Time`, `Return_Date`, `Return_Time`));
                """)

        except mysql.connector.Error as err:  # in case of somtiong wrong in cursor or connection
            print(err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            pass
        return

    def run_sky_scanner(self, args):
        self.driver.maximize_window()  # open tab at bigger window
        # set parameters about flight tickets
        self.flight_from = args[0]
        self.destination = args[1]
        self.departure_date = args[2]
        self.return_date = args[3]
        sleep(2)
        try:
            self.driver.get(
                "https://www.kayak.com/flights/{}-{}/{}/{}?sort=bestflight_a".format(self.flight_from, self.destination,
                                                                                     self.departure_date,
                                                                                     self.return_date))
            flag = True  # since element is displayed when page is loaded break while loop when appear
            while flag:
                try:
                    if not self.driver.find_element_by_class_name('prediction-info ').text == '':
                        flag = False
                    else:
                        sleep(2)
                except Exception as e:
                    print(e)
                    print("An exception occurred")
                    self.driver.quit()  # if something went wrong quit page

            # for clicking on load more results -first need to search for button using expected_conditions
            for j in range(3):
                try:
                    timeout = 60  # large amount of seconds for breaking expected_conditions
                    element_visible = EC.visibility_of_element_located((By.CLASS_NAME, 'resultsPaginator'))
                    WebDriverWait(self.driver, timeout).until(element_visible)
                    self.driver.find_element_by_class_name("resultsPaginator").click()
                    sleep(2)
                except Exception as e:
                    print("Timed out waiting for page to load")
                    pass

            # to get more results, click on the button and scroll through the site up and down
            all_tickets = self.driver.find_elements_by_class_name("mainInfo")  # tickets elements
            all_prices = self.driver.find_elements_by_class_name("multibook-dropdown")  # prices elements
            i = 3  # start index at 3 ignore (cheapest, best, quickest)

            self.checkTableExists()  # check for table
            while i < len(all_tickets):
                ticket = all_tickets[i].text.split('\n')  # split text
                ticket_price = all_prices[i].text

                pk_Dep_Date = parse(self.departure_date).date()
                pk_Ret_Date = parse(self.return_date).date()
                pk_Dep_Time = ticket[0]

                if ticket[2] == 'nonstop':
                    index = 0
                    AirPorts_1 = ticket[4] + ' - ' + ticket[6]
                elif ticket[2] == '1 stop':
                    index = 1
                    AirPorts_1 = ticket[4+index] + ' - ' + ticket[2+index] + ' - ' + ticket[6+index]
                elif ticket[2] == '2 stops':
                    index = 1
                    AirPorts_1 = ticket[4 + index] + ' - ' + ticket[2 + index].replace(',', ' - ') + ' - ' + ticket[6 + index]

                Duration_1 = float(ticket[3 + index].replace('h', '.').replace(' ', '').replace('m', ''))
                Stops_1 = ticket[2]
                pk_Ret_Time = ticket[7 + index]
                Stops_2 = ticket[9 + index]

                if ticket[9 + index] == 'nonstop':
                    AirPorts_2 = ticket[11 + index] + ' - ' + ticket[13 + index]
                elif ticket[9 + index] == '1 stop':
                    index += 1
                    AirPorts_2 = ticket[11 + index] + ' - ' + ticket[9 + index] + ' - ' + ticket[13 + index]
                elif ticket[9 + index] == '2 stops':
                    index += 1
                    AirPorts_2 = ticket[11 + index] + ' - ' + ticket[9 + index].replace(',', ' - ') + ' - ' + ticket[13 + index]

                Duration_2 = float(ticket[10 + index].replace('h', '.').replace(' ', '').replace('m', ''))

                pKeys = (pk_Dep_Date, pk_Dep_Time, pk_Ret_Date, pk_Ret_Time)  # primary keys
                Price = ticket_price[ticket_price.find("$") + 1 : ticket_price.find("\n")]
                if ',' in Price:
                    Price = Price.replace(',', '')

                try:
                    # if exist then update / else then insert
                    if not sql_ticket.isExist(self, pKeys):
                        # Preparing SQL query to INSERT a record into the database.
                        insert_state = """INSERT INTO flight_tickets
                                       (Depart_Date, Depart_Time, AirPorts_1, Stops_1, Duration_1,
                                       Return_Date, Return_Time, AirPorts_2, Stops_2, Duration_2,
                                       Price)
                                       VALUES (%s, %s, %s, %s, %s,
                                        %s, %s, %s, %s, %s,
                                        %s)"""

                        all_values = [pk_Dep_Date, pk_Dep_Time, AirPorts_1, Stops_1, Duration_1,
                                      pk_Ret_Date, pk_Ret_Time, AirPorts_2, Stops_2, Duration_2, Price]

                        self.cursor.execute(insert_state, tuple(all_values))
                        self.db.commit()  # commit to db

                    else:
                        # Preparing SQL query to UPDATE a record into the database.
                        update_state = """UPDATE flight_tickets
                                       SET Price = %s
                                       WHERE Depart_Date = %s AND Depart_Time = %s
                                       AND Return_Date = %s AND Return_Time = %s"""

                        up_values = [Price] + list(pKeys)  # add price val
                        self.cursor.execute(update_state, up_values)
                        self.db.commit()  # commit to db

                except mysql.connector.Error as err:
                    # self.db.rollback()  # in case there has been error do roll back
                    # print(err)
                    print("Error Code:", err.errno)
                    print("SQLSTATE", err.sqlstate)
                    print("Message", err.msg)
                    pass
                i += 1

        except Exception as e:
            print(e)
            print("An exception occurred")
            self.driver.quit()

        try:
            # -- Cheapest : return the 4 cheapest flight
            Cheapest_query = """SELECT *
                             FROM flight_tickets
                             WHERE Depart_Date = %s AND Return_Date = %s 
                             AND AirPorts_1 LIKE %s AND AirPorts_1 LIKE %s
                             ORDER BY Price ASC LIMIT 5;"""

            print('\nCheapest_df')
            Cheapest_df = self.sql_to_df(Cheapest_query)

            # -- Quickest : return the 4 quickest flight
            Quickest_query = """SELECT *
                             FROM flight_tickets
                             WHERE Depart_Date = %s AND Return_Date = %s
                             AND AirPorts_1 LIKE %s AND AirPorts_1 LIKE %s
                             ORDER BY(Duration_1 + Duration_2) ASC LIMIT 5;"""

            print('\nQuickest_query')
            Quickest_df = self.sql_to_df(Quickest_query)

            # -- Early_Arrival : return the flight where you do not add a day
            # and the flight lands the earliest and returns to the country at the latest time
            Early_Arrival_query = """SELECT Depart_Date, Depart_Time, Return_Date, Return_Time, AirPorts_1, Duration_1, Stops_1, AirPorts_2, Duration_2, Stops_2, Price
                                    FROM (SELECT * ,CONVERT(SUBSTRING(Depart_Time, 7), TIME) as Arrival_At, CONVERT(SUBSTRING(Return_Time,1,5), TIME) as Leaving_At
                                            FROM flight_tickets
                                            WHERE Depart_Date = %s AND Return_Date = %s
                                            AND AirPorts_1 LIKE %s AND AirPorts_1 LIKE %s
                                            ORDER BY Arrival_At ASC, Leaving_At DESC LIMIT 5) as Early_Late_opt;"""
            print('\nEarly_Arrival_df')
            Early_Arrival_df = self.sql_to_df(Early_Arrival_query)

        except mysql.connector.Error as err:
            self.db.rollback()  # in case there has been error do roll back
            print(err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            pass

        finally:
            self.driver.close()
            return
```


```python
# import
from geopy.geocoders import Nominatim
from folium import plugins
import geocoder
import geopy
import io
from PIL import Image
from IPython.core.display import display, HTML
import datetime
from datetime import timedelta, datetime, date

def draw_on_map(user_info):
    """
    function display a topo-map for user to drop markers based on place intended to sleep during trip
    :param user_info: information on fly ticket 
    :return: map
    """
    
    # setting a map using name of Air-port (not necessarily has to be port)
    geolocator = Nominatim(user_agent="application")
    location = geolocator.geocode(user_info[1])

    map_with_mini = folium.Map(location=(location.latitude, location.longitude), zoom_start=12,
                               width=1250, height=550, control_scale=True,
                               tiles='Stamen Terrain',
                               tooltip='This tooltip will appear on hover')
    
    # add mini map at the buttom of map
    minimap = plugins.MiniMap(toggle_display=True)
    map_with_mini.add_child(minimap)
    plugins.Fullscreen(position='topright').add_to(map_with_mini) # choosing map type
    #add measures 
    measure_control = plugins.MeasureControl(position='topleft',
                                             active_color='purple',
                                             completed_color='purpule',
                                             primary_length_unit='kilometers')
    map_with_mini.add_child(measure_control)
    
    # add tools and export=True exports the drawn shapes as a geojson file
    draw = plugins.Draw(filename='MyMap', export= True)
    draw.add_to(map_with_mini)
    
    # save map
    map_with_mini.save('MyMap.html')

    return map_with_mini
```


```python
# import
import folium
from folium import plugins
from IPython.core.display import display, HTML
import json
import os
from termcolor import colored
import datetime
from datetime import timedelta, datetime, date


def trip_Map(path, ls_info, options=3, show_=False):
    """
    function loads the downloaded coordinates and processes data to find the best time window to travel
    based on the number of days and available dates from all_ticket_options function.
    
    :param path: directory where export map using draw_on_map function 
    :param ls_info: user_info using function all_ticket_options
    :param options: default 
    :param show_: show the dictionary, how the algorithm was selected the best value 
    :return: based on options return the amount of maps represent the route along with pop-ups 
     which are dataframe for the forecast each day
    """
    
    try:
        # load and open  from directory
        files = os.listdir(path)
        paths = [os.path.join(path, basename) for basename in files]
        new_file = max(paths, key=os.path.getctime).replace('\\', '/')
        with open(new_file) as f:
            data = json.load(f)
        ls_coord = []
        for i in range(len(data['features'])):
            if data['features'][0]['geometry']['type'] == 'Point':
                ls_coord.append(
                    data['features'][i]['geometry']['coordinates'][1:] + data['features'][i]['geometry']['coordinates'][
                                                                         :1])
        # creat a map usinf first coordinate
        mayMap = folium.Map(location=ls_coord[0], zoom_start=10,
                           width=1250, height=550, control_scale=True,
                            tiles='Stamen Terrain',
                            tooltip='This tooltip will appear on hover')

        # setting for a map
        minimap = plugins.MiniMap(toggle_display=True)
        mayMap.add_child(minimap)
        plugins.Fullscreen(position='topright').add_to(mayMap)

        
        # call avalute function to return dictionary arranged according to the sequence of days
        # appropriate for the trip 
        get_best_day = forecast().avalute(ls_coord, ls_info)
        if show_: # show the dictionary
            print(get_best_day)
        get_best_day = get_best_day[:options]  # get amount of result from dictionary

        print(colored("\nDisplay maps as option 1 is the rank the heights\n", 'green', attrs=['bold'])) # title
        opt_num = 1
        for opt in get_best_day:
            day_index = 1
            for i in range(len(ls_coord)):
                elem_cord = forecast().df_forecast(ls_coord[i][0], ls_coord[i][1], opt[1] + i)
                html = f"""
                    <body style="background-color:#ccccff;">
                        <h3>Option {opt_num}</h3>
                        <h2>Day {day_index} : {elem_cord[0]} </h2>
                        <p>{elem_cord[1]}</p>
                    </body>
                    """
                # add marker on the map with dataframe of forecast 
                iframe = folium.IFrame(html=html, width=540, height=360)
                popup = folium.Popup(iframe, max_width=600)
                folium.Marker(
                    location=ls_coord[i],
                    tooltip="Day {}".format(day_index),
                    popup=popup,
                    icon=folium.Icon(color='purple')).add_to(mayMap)
                day_index += 1

            mayMap.save('Map_Option_{} , {}.html'.format(opt[4][0], opt[4][1])) # save map
            result_Dict = {"Start": opt[4][0], "End": opt[4][1],  "Avg_Rain": opt[2], "Avg_Clouds": opt[3]}
            
            # print info about the sequence of days suitable for the trip
            print(colored('\nTravel info', attrs=['bold']))
            print(colored('_'*100, attrs=['bold']))
            print(colored 
                  ("Option {}\nStarts at {}\nReturn at {}\nIn average:\n - Rain chance per day is {}%\n - Coluds chance per day {}%\n"
                  .format(opt_num, result_Dict.get('Start'), result_Dict.get('End'), result_Dict.get('Avg_Rain'),
                         result_Dict.get('Avg_Clouds')),
                  attrs=['bold']))
            display(mayMap) # show map
            
            # using sql query retrieve information on tickets based on querys implement at run_sky_scanner function
            print(colored('Fly ticket info', attrs=['bold']))
            print(colored('_'*100, attrs=['bold']))
            print(colored(ls_info[:2] + [result_Dict.get('Start') ,result_Dict.get('End')], 'blue'))
            sql_ticket().run_sky_scanner(ls_info[:2] + [result_Dict.get('Start') ,result_Dict.get('End')])
            opt_num += 1
    except Exception as e:
        print(e)

    finally:
        return
```


```python
def run_app():
#     print("Departure from: TLV\n"
#           "Destination: valbona\n"
#           "Chose day to fly: 24.09.2021\n"
#           "Chose day to return: 03.10.2021\n")
    
    user_info = all_ticket_options()

    return draw_on_map(user_info), user_info

results = run_app()

```

    Departure from: TLV
    Destination: CDG
    Chose day to fly: 20.11.2021
    Chose day to return: 27.11.2021
    


```python
results[0]
```




<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;"><span style="color:#565656">Make this Notebook Trusted to load map: File -> Trust Notebook</span><iframe src="about:blank" style="position:absolute;width:100%;height:100%;left:0;top:0;border:none !important;" data-html=%3C%21DOCTYPE%20html%3E%0A%3Chead%3E%20%20%20%20%0A%20%20%20%20%3Cmeta%20http-equiv%3D%22content-type%22%20content%3D%22text/html%3B%20charset%3DUTF-8%22%20/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%3Cscript%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20L_NO_TOUCH%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L_DISABLE_3D%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%3C/script%3E%0A%20%20%20%20%0A%20%20%20%20%3Cstyle%3Ehtml%2C%20body%20%7Bwidth%3A%20100%25%3Bheight%3A%20100%25%3Bmargin%3A%200%3Bpadding%3A%200%3B%7D%3C/style%3E%0A%20%20%20%20%3Cstyle%3E%23map%20%7Bposition%3Aabsolute%3Btop%3A0%3Bbottom%3A0%3Bright%3A0%3Bleft%3A0%3B%7D%3C/style%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//code.jquery.com/jquery-1.12.4.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css%22/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cmeta%20name%3D%22viewport%22%20content%3D%22width%3Ddevice-width%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20initial-scale%3D1.0%2C%20maximum-scale%3D1.0%2C%20user-scalable%3Dno%22%20/%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cstyle%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23map_9171c1e6a6364c7d8995162aada1ec16%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20position%3A%20relative%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20width%3A%201250.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20height%3A%20550.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20left%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20top%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%3C/style%3E%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.css%22/%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.css%22/%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdn.jsdelivr.net/gh/ljagis/leaflet-measure%402.1.7/dist/leaflet-measure.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/gh/ljagis/leaflet-measure%402.1.7/dist/leaflet-measure.min.css%22/%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.css%22/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cstyle%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23export%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20position%3A%20absolute%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20top%3A%205px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20right%3A%2010px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20z-index%3A%20999%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20background%3A%20white%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20color%3A%20black%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20padding%3A%206px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20border-radius%3A%204px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20font-family%3A%20%27Helvetica%20Neue%27%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20cursor%3A%20pointer%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20font-size%3A%2012px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20text-decoration%3A%20none%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20top%3A%2090px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%3C/style%3E%0A%20%20%20%20%20%20%20%20%0A%3C/head%3E%0A%3Cbody%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cdiv%20class%3D%22folium-map%22%20id%3D%22map_9171c1e6a6364c7d8995162aada1ec16%22%20%3E%3C/div%3E%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%3Ca%20href%3D%27%23%27%20id%3D%27export%27%3EExport%3C/a%3E%0A%3C/body%3E%0A%3Cscript%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20map_9171c1e6a6364c7d8995162aada1ec16%20%3D%20L.map%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22map_9171c1e6a6364c7d8995162aada1ec16%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20center%3A%20%5B49.00687505%2C%202.5710604233025913%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20crs%3A%20L.CRS.EPSG3857%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoom%3A%2012%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoomControl%3A%20true%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20preferCanvas%3A%20false%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tooltip%3A%20%22This%20tooltip%20will%20appear%20on%20hover%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.scale%28%29.addTo%28map_9171c1e6a6364c7d8995162aada1ec16%29%3B%0A%0A%20%20%20%20%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_a57552ec6f094fef89dbe4366b057cae%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//stamen-tiles-%7Bs%7D.a.ssl.fastly.net/terrain/%7Bz%7D/%7Bx%7D/%7By%7D.jpg%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Map%20tiles%20by%20%5Cu003ca%20href%3D%5C%22http%3A//stamen.com%5C%22%5Cu003eStamen%20Design%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by/3.0%5C%22%5Cu003eCC%20BY%203.0%5Cu003c/a%5Cu003e.%20Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by-sa/3.0%5C%22%5Cu003eCC%20BY%20SA%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_9171c1e6a6364c7d8995162aada1ec16%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_4f3e7dc39c044f75b41de072775453d5%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//%7Bs%7D.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//www.openstreetmap.org/copyright%5C%22%5Cu003eODbL%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20mini_map_136a9aeecf864715bc781dcbf19da13e%20%3D%20new%20L.Control.MiniMap%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tile_layer_4f3e7dc39c044f75b41de072775453d5%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22autoToggleDisplay%22%3A%20false%2C%20%22centerFixed%22%3A%20false%2C%20%22collapsedHeight%22%3A%2025%2C%20%22collapsedWidth%22%3A%2025%2C%20%22height%22%3A%20150%2C%20%22minimized%22%3A%20false%2C%20%22position%22%3A%20%22bottomright%22%2C%20%22toggleDisplay%22%3A%20true%2C%20%22width%22%3A%20150%2C%20%22zoomAnimation%22%3A%20false%2C%20%22zoomLevelOffset%22%3A%20-5%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20map_9171c1e6a6364c7d8995162aada1ec16.addControl%28mini_map_136a9aeecf864715bc781dcbf19da13e%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.fullscreen%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22forceSeparateButton%22%3A%20false%2C%20%22position%22%3A%20%22topright%22%2C%20%22title%22%3A%20%22Full%20Screen%22%2C%20%22titleCancel%22%3A%20%22Exit%20Full%20Screen%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_9171c1e6a6364c7d8995162aada1ec16%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20measure_control_28d7c55640e044caba085acb6d40a4fb%20%3D%20new%20L.Control.Measure%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22activeColor%22%3A%20%22purple%22%2C%20%22completedColor%22%3A%20%22purpule%22%2C%20%22position%22%3A%20%22topleft%22%2C%20%22primaryAreaUnit%22%3A%20%22sqmeters%22%2C%20%22primaryLengthUnit%22%3A%20%22kilometers%22%2C%20%22secondaryAreaUnit%22%3A%20%22acres%22%2C%20%22secondaryLengthUnit%22%3A%20%22miles%22%7D%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20map_9171c1e6a6364c7d8995162aada1ec16.addControl%28measure_control_28d7c55640e044caba085acb6d40a4fb%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20options%20%3D%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20position%3A%20%22topleft%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20draw%3A%20%7B%7D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20edit%3A%20%7B%7D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20//%20FeatureGroup%20is%20to%20store%20editable%20layers.%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20drawnItems%20%3D%20new%20L.featureGroup%28%29.addTo%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20map_9171c1e6a6364c7d8995162aada1ec16%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20options.edit.featureGroup%20%3D%20drawnItems%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20draw_control_48df7e993e57464cbbdbd3ea8379eacc%20%3D%20new%20L.Control.Draw%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20options%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28%20map_9171c1e6a6364c7d8995162aada1ec16%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20map_9171c1e6a6364c7d8995162aada1ec16.on%28L.Draw.Event.CREATED%2C%20function%28e%29%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20var%20layer%20%3D%20e.layer%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20type%20%3D%20e.layerType%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20var%20coords%20%3D%20JSON.stringify%28layer.toGeoJSON%28%29%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20layer.on%28%27click%27%2C%20function%28%29%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20alert%28coords%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20console.log%28coords%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20drawnItems.addLayer%28layer%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20map_9171c1e6a6364c7d8995162aada1ec16.on%28%27draw%3Acreated%27%2C%20function%28e%29%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20drawnItems.addLayer%28e.layer%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20document.getElementById%28%27export%27%29.onclick%20%3D%20function%28e%29%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20var%20data%20%3D%20drawnItems.toGeoJSON%28%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20var%20convertedData%20%3D%20%27text/json%3Bcharset%3Dutf-8%2C%27%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%2B%20encodeURIComponent%28JSON.stringify%28data%29%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20document.getElementById%28%27export%27%29.setAttribute%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%27href%27%2C%20%27data%3A%27%20%2B%20convertedData%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20document.getElementById%28%27export%27%29.setAttribute%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%27download%27%2C%20%22MyMap%22%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%0A%3C/script%3E onload="this.contentDocument.open();this.contentDocument.write(    decodeURIComponent(this.getAttribute('data-html')));this.contentDocument.close();" allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe></div></div>




```python
trip_Map('C:/Users/user/Downloads', results[1], show_=True)

```

    [('2021-11-23', 8, 0.0, 37.25, ('2021-11-22', '2021-11-29')), ('2021-11-18', 3, 11.34375, 76.5, ('2021-11-17', '2021-11-24')), ('2021-11-24', 9, 16.734375, 58.25, ('2021-11-23', '2021-11-30')), ('2021-11-22', 7, 21.0625, 33.0, ('2021-11-21', '2021-11-28')), ('2021-11-21', 6, 27.390625, 39.25, ('2021-11-20', '2021-11-27')), ('2021-11-20', 5, 32.40625, 47.5, ('2021-11-19', '2021-11-26')), ('2021-11-19', 4, 32.40625, 66.0, ('2021-11-18', '2021-11-25'))]
    [1m[32m
    Display maps as option 1 is the rank the heights
    [0m
    [1m
    Travel info[0m
    [1m____________________________________________________________________________________________________[0m
    [1mOption 1
    Starts at 2021-11-22
    Return at 2021-11-29
    In average:
     - Rain chance per day is 0.0%
     - Coluds chance per day 37.25%
    [0m
    


<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;"><span style="color:#565656">Make this Notebook Trusted to load map: File -> Trust Notebook</span><iframe src="about:blank" style="position:absolute;width:100%;height:100%;left:0;top:0;border:none !important;" data-html=%3C%21DOCTYPE%20html%3E%0A%3Chead%3E%20%20%20%20%0A%20%20%20%20%3Cmeta%20http-equiv%3D%22content-type%22%20content%3D%22text/html%3B%20charset%3DUTF-8%22%20/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%3Cscript%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20L_NO_TOUCH%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L_DISABLE_3D%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%3C/script%3E%0A%20%20%20%20%0A%20%20%20%20%3Cstyle%3Ehtml%2C%20body%20%7Bwidth%3A%20100%25%3Bheight%3A%20100%25%3Bmargin%3A%200%3Bpadding%3A%200%3B%7D%3C/style%3E%0A%20%20%20%20%3Cstyle%3E%23map%20%7Bposition%3Aabsolute%3Btop%3A0%3Bbottom%3A0%3Bright%3A0%3Bleft%3A0%3B%7D%3C/style%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//code.jquery.com/jquery-1.12.4.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css%22/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cmeta%20name%3D%22viewport%22%20content%3D%22width%3Ddevice-width%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20initial-scale%3D1.0%2C%20maximum-scale%3D1.0%2C%20user-scalable%3Dno%22%20/%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cstyle%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23map_cabcf3a57837415097e72f91298b6522%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20position%3A%20relative%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20width%3A%201250.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20height%3A%20550.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20left%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20top%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%3C/style%3E%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.css%22/%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.css%22/%3E%0A%3C/head%3E%0A%3Cbody%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cdiv%20class%3D%22folium-map%22%20id%3D%22map_cabcf3a57837415097e72f91298b6522%22%20%3E%3C/div%3E%0A%20%20%20%20%20%20%20%20%0A%3C/body%3E%0A%3Cscript%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20map_cabcf3a57837415097e72f91298b6522%20%3D%20L.map%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22map_cabcf3a57837415097e72f91298b6522%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20center%3A%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20crs%3A%20L.CRS.EPSG3857%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoom%3A%2010%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoomControl%3A%20true%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20preferCanvas%3A%20false%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tooltip%3A%20%22This%20tooltip%20will%20appear%20on%20hover%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.scale%28%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%0A%20%20%20%20%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_98f2a930a4014c428a2155810441cb22%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//stamen-tiles-%7Bs%7D.a.ssl.fastly.net/terrain/%7Bz%7D/%7Bx%7D/%7By%7D.jpg%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Map%20tiles%20by%20%5Cu003ca%20href%3D%5C%22http%3A//stamen.com%5C%22%5Cu003eStamen%20Design%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by/3.0%5C%22%5Cu003eCC%20BY%203.0%5Cu003c/a%5Cu003e.%20Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by-sa/3.0%5C%22%5Cu003eCC%20BY%20SA%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_3d95c93c87d041479cca10054438a22e%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//%7Bs%7D.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//www.openstreetmap.org/copyright%5C%22%5Cu003eODbL%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20mini_map_86e26474cb1b4cc8b2728a500137e9b5%20%3D%20new%20L.Control.MiniMap%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tile_layer_3d95c93c87d041479cca10054438a22e%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22autoToggleDisplay%22%3A%20false%2C%20%22centerFixed%22%3A%20false%2C%20%22collapsedHeight%22%3A%2025%2C%20%22collapsedWidth%22%3A%2025%2C%20%22height%22%3A%20150%2C%20%22minimized%22%3A%20false%2C%20%22position%22%3A%20%22bottomright%22%2C%20%22toggleDisplay%22%3A%20true%2C%20%22width%22%3A%20150%2C%20%22zoomAnimation%22%3A%20false%2C%20%22zoomLevelOffset%22%3A%20-5%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20map_cabcf3a57837415097e72f91298b6522.addControl%28mini_map_86e26474cb1b4cc8b2728a500137e9b5%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.fullscreen%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22forceSeparateButton%22%3A%20false%2C%20%22position%22%3A%20%22topright%22%2C%20%22title%22%3A%20%22Full%20Screen%22%2C%20%22titleCancel%22%3A%20%22Exit%20Full%20Screen%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_e0b1c9af2dac4786b54901d972fa394f%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_bd53012a09384222a90ee5aa53a2b91d%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.setIcon%28icon_bd53012a09384222a90ee5aa53a2b91d%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_9e71da34b58b4e2f98ffecee3a03f73d%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_891d2379eb1d401f82a53483e502bb77%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMSA6IDIzLjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjIzLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNC4ywrA8L3RkPgogICAgICA8dGQ%2BMTYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5GZXcgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNC4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjcuMsKwPC90ZD4KICAgICAgPHRkPjY3ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjUuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjHCsDwvdGQ%2BCiAgICAgIDx0ZD4xMiAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkZldyBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDJkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_9e71da34b58b4e2f98ffecee3a03f73d.setContent%28i_frame_891d2379eb1d401f82a53483e502bb77%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.bindPopup%28popup_9e71da34b58b4e2f98ffecee3a03f73d%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%201%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_5257a3bd8c8848f5bc3548deaf88ce84%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.853167%2C%202.369163%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_ec987ca973a94b7ba816fd83be50bcf6%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.setIcon%28icon_ec987ca973a94b7ba816fd83be50bcf6%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_725b7571f9b04075a37443e9abaf8430%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_bea84eda0fc045d8bdfd5e4f760b5ab7%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMiA6IDI0LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI0LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNy41wrA8L3RkPgogICAgICA8dGQ%2BNjMgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNS4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjYuMsKwPC90ZD4KICAgICAgPHRkPjI1ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BU2NhdHRlcmVkIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwMmQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjYuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD42wrA8L3RkPgogICAgICA8dGQ%2BNjggJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_725b7571f9b04075a37443e9abaf8430.setContent%28i_frame_bea84eda0fc045d8bdfd5e4f760b5ab7%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.bindPopup%28popup_725b7571f9b04075a37443e9abaf8430%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%202%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_eb3e1b0dee3941b28ae92880c18178b5%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.858521%2C%202.381748%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_a50ecbc4ee194148abfe2625232d3d4a%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.setIcon%28icon_a50ecbc4ee194148abfe2625232d3d4a%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_2ddb09102d284bc3b4a2248403bbc924%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_6899eac92caf47908367498430bfe736%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMyA6IDI1LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI1LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNi4zwrA8L3RkPgogICAgICA8dGQ%2BMzYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjUuOMKwPC90ZD4KICAgICAgPHRkPjYxICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjcuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjjCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD43NSAlPC90ZD4KICAgICAgPHRkPjIuNzUgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_2ddb09102d284bc3b4a2248403bbc924.setContent%28i_frame_6899eac92caf47908367498430bfe736%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.bindPopup%28popup_2ddb09102d284bc3b4a2248403bbc924%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%203%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.831108%2C%202.288868%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_38d21e3bf8d549a9984d0c4fb3de4aae%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.setIcon%28icon_38d21e3bf8d549a9984d0c4fb3de4aae%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_201766eb8afb4353847cecde0b658082%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_8da2526bb33243ffa842db6b987841a2%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgNCA6IDI2LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI2LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNsKwPC90ZD4KICAgICAgPHRkPjY4ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjE8L3RoPgogICAgICA8dGQ%2BMjcuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjjCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD43NSAlPC90ZD4KICAgICAgPHRkPjIuODc1IG1tL2hyPC90ZD4KICAgICAgPHRkPk92ZXJjYXN0IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwNGQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjguMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjnCsDwvdGQ%2BCiAgICAgIDx0ZD40NyAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkJyb2tlbiBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDNkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_201766eb8afb4353847cecde0b658082.setContent%28i_frame_8da2526bb33243ffa842db6b987841a2%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.bindPopup%28popup_201766eb8afb4353847cecde0b658082%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%204%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%3C/script%3E onload="this.contentDocument.open();this.contentDocument.write(    decodeURIComponent(this.getAttribute('data-html')));this.contentDocument.close();" allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe></div></div>


    [1mFly ticket info[0m
    [1m____________________________________________________________________________________________________[0m
    [34m['TLV', 'CDG', '2021-11-22', '2021-11-29'][0m
    
    Cheapest_df
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>AirPorts_1</th>
      <th>Stops_1</th>
      <th>Duration_1</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_2</th>
      <th>Stops_2</th>
      <th>Duration_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-22</td>
      <td>8:30 pm – 8:05 am +1</td>
      <td>TLV - MXP - CDG</td>
      <td>1 stop</td>
      <td>12h 35</td>
      <td>2021-11-29</td>
      <td>11:00 am – 7:30 pm</td>
      <td>CDG - MXP - TLV</td>
      <td>1 stop</td>
      <td>7h 30</td>
      <td>209</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-22</td>
      <td>8:30 pm – 8:05 am +1</td>
      <td>TLV - MXP - CDG</td>
      <td>1 stop</td>
      <td>12h 35</td>
      <td>2021-11-29</td>
      <td>7:30 am – 4:10 pm</td>
      <td>CDG - BGY - TLV</td>
      <td>1 stop</td>
      <td>7h 40</td>
      <td>230</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-22</td>
      <td>5:30 pm – 8:30 am +1</td>
      <td>TLV - BGY-LIN - CDG</td>
      <td>1 stop</td>
      <td>16h 0</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 35</td>
      <td>254</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-22</td>
      <td>5:30 pm – 8:05 am +1</td>
      <td>TLV - BGY-MXP - CDG</td>
      <td>1 stop</td>
      <td>15h 35</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 35</td>
      <td>260</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-22</td>
      <td>10:55 am – 6:10 pm</td>
      <td>TLV - KRK - CDG</td>
      <td>1 stop</td>
      <td>8h 15</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 35</td>
      <td>266</td>
    </tr>
  </tbody>
</table>
</div>


    
    Quickest_query
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>AirPorts_1</th>
      <th>Stops_1</th>
      <th>Duration_1</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_2</th>
      <th>Stops_2</th>
      <th>Duration_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-22</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>4h 40</td>
      <td>2021-11-29</td>
      <td>8:55 am – 2:05 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 10</td>
      <td>578</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-22</td>
      <td>4:50 pm – 8:55 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 5</td>
      <td>2021-11-29</td>
      <td>2:45 pm – 8:00 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 15</td>
      <td>739</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-22</td>
      <td>4:50 pm – 8:55 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 5</td>
      <td>2021-11-29</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 25</td>
      <td>740</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-22</td>
      <td>6:50 pm – 11:10 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 20</td>
      <td>2021-11-29</td>
      <td>2:45 pm – 8:00 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 15</td>
      <td>533</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-22</td>
      <td>4:50 pm – 8:55 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 5</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 35</td>
      <td>560</td>
    </tr>
  </tbody>
</table>
</div>


    
    Early_Arrival_df
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_1</th>
      <th>Duration_1</th>
      <th>Stops_1</th>
      <th>AirPorts_2</th>
      <th>Duration_2</th>
      <th>Stops_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-22</td>
      <td>1:00 am – 3:30 pm</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>TLV - IST-SAW - CDG</td>
      <td>15h 30</td>
      <td>1 stop</td>
      <td>CDG - TLV</td>
      <td>4h 35</td>
      <td>nonstop</td>
      <td>383</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-22</td>
      <td>10:55 am – 6:10 pm</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>TLV - KRK - CDG</td>
      <td>8h 15</td>
      <td>1 stop</td>
      <td>CDG - TLV</td>
      <td>4h 35</td>
      <td>nonstop</td>
      <td>266</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-22</td>
      <td>4:50 pm – 8:55 pm</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>TLV - CDG</td>
      <td>5h 5</td>
      <td>nonstop</td>
      <td>CDG - TLV</td>
      <td>4h 35</td>
      <td>nonstop</td>
      <td>560</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-22</td>
      <td>11:30 pm – 11:00 am +1</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>TLV - OTP - CDG</td>
      <td>12h 30</td>
      <td>1 stop</td>
      <td>CDG - TLV</td>
      <td>4h 35</td>
      <td>nonstop</td>
      <td>341</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-22</td>
      <td>2:15 pm – 10:35 pm</td>
      <td>2021-11-29</td>
      <td>12:10 pm – 5:45 pm</td>
      <td>TLV - BER - CDG</td>
      <td>9h 20</td>
      <td>1 stop</td>
      <td>CDG - TLV</td>
      <td>4h 35</td>
      <td>nonstop</td>
      <td>375</td>
    </tr>
  </tbody>
</table>
</div>


    [1m
    Travel info[0m
    [1m____________________________________________________________________________________________________[0m
    [1mOption 2
    Starts at 2021-11-17
    Return at 2021-11-24
    In average:
     - Rain chance per day is 11.34375%
     - Coluds chance per day 76.5%
    [0m
    


<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;"><span style="color:#565656">Make this Notebook Trusted to load map: File -> Trust Notebook</span><iframe src="about:blank" style="position:absolute;width:100%;height:100%;left:0;top:0;border:none !important;" data-html=%3C%21DOCTYPE%20html%3E%0A%3Chead%3E%20%20%20%20%0A%20%20%20%20%3Cmeta%20http-equiv%3D%22content-type%22%20content%3D%22text/html%3B%20charset%3DUTF-8%22%20/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%3Cscript%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20L_NO_TOUCH%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L_DISABLE_3D%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%3C/script%3E%0A%20%20%20%20%0A%20%20%20%20%3Cstyle%3Ehtml%2C%20body%20%7Bwidth%3A%20100%25%3Bheight%3A%20100%25%3Bmargin%3A%200%3Bpadding%3A%200%3B%7D%3C/style%3E%0A%20%20%20%20%3Cstyle%3E%23map%20%7Bposition%3Aabsolute%3Btop%3A0%3Bbottom%3A0%3Bright%3A0%3Bleft%3A0%3B%7D%3C/style%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//code.jquery.com/jquery-1.12.4.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css%22/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cmeta%20name%3D%22viewport%22%20content%3D%22width%3Ddevice-width%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20initial-scale%3D1.0%2C%20maximum-scale%3D1.0%2C%20user-scalable%3Dno%22%20/%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cstyle%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23map_cabcf3a57837415097e72f91298b6522%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20position%3A%20relative%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20width%3A%201250.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20height%3A%20550.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20left%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20top%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%3C/style%3E%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.css%22/%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.css%22/%3E%0A%3C/head%3E%0A%3Cbody%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cdiv%20class%3D%22folium-map%22%20id%3D%22map_cabcf3a57837415097e72f91298b6522%22%20%3E%3C/div%3E%0A%20%20%20%20%20%20%20%20%0A%3C/body%3E%0A%3Cscript%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20map_cabcf3a57837415097e72f91298b6522%20%3D%20L.map%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22map_cabcf3a57837415097e72f91298b6522%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20center%3A%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20crs%3A%20L.CRS.EPSG3857%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoom%3A%2010%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoomControl%3A%20true%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20preferCanvas%3A%20false%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tooltip%3A%20%22This%20tooltip%20will%20appear%20on%20hover%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.scale%28%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%0A%20%20%20%20%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_98f2a930a4014c428a2155810441cb22%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//stamen-tiles-%7Bs%7D.a.ssl.fastly.net/terrain/%7Bz%7D/%7Bx%7D/%7By%7D.jpg%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Map%20tiles%20by%20%5Cu003ca%20href%3D%5C%22http%3A//stamen.com%5C%22%5Cu003eStamen%20Design%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by/3.0%5C%22%5Cu003eCC%20BY%203.0%5Cu003c/a%5Cu003e.%20Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by-sa/3.0%5C%22%5Cu003eCC%20BY%20SA%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_3d95c93c87d041479cca10054438a22e%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//%7Bs%7D.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//www.openstreetmap.org/copyright%5C%22%5Cu003eODbL%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20mini_map_86e26474cb1b4cc8b2728a500137e9b5%20%3D%20new%20L.Control.MiniMap%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tile_layer_3d95c93c87d041479cca10054438a22e%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22autoToggleDisplay%22%3A%20false%2C%20%22centerFixed%22%3A%20false%2C%20%22collapsedHeight%22%3A%2025%2C%20%22collapsedWidth%22%3A%2025%2C%20%22height%22%3A%20150%2C%20%22minimized%22%3A%20false%2C%20%22position%22%3A%20%22bottomright%22%2C%20%22toggleDisplay%22%3A%20true%2C%20%22width%22%3A%20150%2C%20%22zoomAnimation%22%3A%20false%2C%20%22zoomLevelOffset%22%3A%20-5%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20map_cabcf3a57837415097e72f91298b6522.addControl%28mini_map_86e26474cb1b4cc8b2728a500137e9b5%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.fullscreen%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22forceSeparateButton%22%3A%20false%2C%20%22position%22%3A%20%22topright%22%2C%20%22title%22%3A%20%22Full%20Screen%22%2C%20%22titleCancel%22%3A%20%22Exit%20Full%20Screen%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_e0b1c9af2dac4786b54901d972fa394f%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_bd53012a09384222a90ee5aa53a2b91d%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.setIcon%28icon_bd53012a09384222a90ee5aa53a2b91d%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_9e71da34b58b4e2f98ffecee3a03f73d%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_891d2379eb1d401f82a53483e502bb77%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMSA6IDIzLjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjIzLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNC4ywrA8L3RkPgogICAgICA8dGQ%2BMTYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5GZXcgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNC4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjcuMsKwPC90ZD4KICAgICAgPHRkPjY3ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjUuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjHCsDwvdGQ%2BCiAgICAgIDx0ZD4xMiAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkZldyBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDJkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_9e71da34b58b4e2f98ffecee3a03f73d.setContent%28i_frame_891d2379eb1d401f82a53483e502bb77%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.bindPopup%28popup_9e71da34b58b4e2f98ffecee3a03f73d%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%201%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_5257a3bd8c8848f5bc3548deaf88ce84%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.853167%2C%202.369163%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_ec987ca973a94b7ba816fd83be50bcf6%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.setIcon%28icon_ec987ca973a94b7ba816fd83be50bcf6%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_725b7571f9b04075a37443e9abaf8430%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_bea84eda0fc045d8bdfd5e4f760b5ab7%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMiA6IDI0LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI0LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNy41wrA8L3RkPgogICAgICA8dGQ%2BNjMgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNS4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjYuMsKwPC90ZD4KICAgICAgPHRkPjI1ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BU2NhdHRlcmVkIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwMmQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjYuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD42wrA8L3RkPgogICAgICA8dGQ%2BNjggJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_725b7571f9b04075a37443e9abaf8430.setContent%28i_frame_bea84eda0fc045d8bdfd5e4f760b5ab7%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.bindPopup%28popup_725b7571f9b04075a37443e9abaf8430%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%202%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_eb3e1b0dee3941b28ae92880c18178b5%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.858521%2C%202.381748%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_a50ecbc4ee194148abfe2625232d3d4a%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.setIcon%28icon_a50ecbc4ee194148abfe2625232d3d4a%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_2ddb09102d284bc3b4a2248403bbc924%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_6899eac92caf47908367498430bfe736%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMyA6IDI1LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI1LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNi4zwrA8L3RkPgogICAgICA8dGQ%2BMzYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjUuOMKwPC90ZD4KICAgICAgPHRkPjYxICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjcuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjjCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD43NSAlPC90ZD4KICAgICAgPHRkPjIuNzUgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_2ddb09102d284bc3b4a2248403bbc924.setContent%28i_frame_6899eac92caf47908367498430bfe736%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.bindPopup%28popup_2ddb09102d284bc3b4a2248403bbc924%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%203%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.831108%2C%202.288868%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_38d21e3bf8d549a9984d0c4fb3de4aae%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.setIcon%28icon_38d21e3bf8d549a9984d0c4fb3de4aae%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_201766eb8afb4353847cecde0b658082%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_8da2526bb33243ffa842db6b987841a2%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgNCA6IDI2LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI2LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNsKwPC90ZD4KICAgICAgPHRkPjY4ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjE8L3RoPgogICAgICA8dGQ%2BMjcuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjjCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD43NSAlPC90ZD4KICAgICAgPHRkPjIuODc1IG1tL2hyPC90ZD4KICAgICAgPHRkPk92ZXJjYXN0IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwNGQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjguMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjnCsDwvdGQ%2BCiAgICAgIDx0ZD40NyAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkJyb2tlbiBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDNkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_201766eb8afb4353847cecde0b658082.setContent%28i_frame_8da2526bb33243ffa842db6b987841a2%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.bindPopup%28popup_201766eb8afb4353847cecde0b658082%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%204%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_65de7cf812c449c0974e12196c28a456%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_8da58a8bcdfd4170a04a07f235896e1f%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_65de7cf812c449c0974e12196c28a456.setIcon%28icon_8da58a8bcdfd4170a04a07f235896e1f%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_46fd1515d3d44bae989e48e587a6e190%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_26671622bad947ec9bae10f5766d09d6%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMSA6IDE4LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjE4LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BOcKwPC90ZD4KICAgICAgPHRkPjc5ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4xOS4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjExLjnCsDwvdGQ%2BCiAgICAgIDx0ZD45MCAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPk92ZXJjYXN0IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwNGQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjAuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD4xMS45wrA8L3RkPgogICAgICA8dGQ%2BMTAwICU8L3RkPgogICAgICA8dGQ%2BMjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wLjA2MjUgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_46fd1515d3d44bae989e48e587a6e190.setContent%28i_frame_26671622bad947ec9bae10f5766d09d6%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_65de7cf812c449c0974e12196c28a456.bindPopup%28popup_46fd1515d3d44bae989e48e587a6e190%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_65de7cf812c449c0974e12196c28a456.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%201%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_24f01e61cda04f5baef11c0e074b38b3%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.853167%2C%202.369163%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_6bb8987340ac4ec0bd6979bbe5c1dc56%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_24f01e61cda04f5baef11c0e074b38b3.setIcon%28icon_6bb8987340ac4ec0bd6979bbe5c1dc56%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_95ba3f173ac3402086ff421b88fa7bed%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_43d62cfa6c444da99e0c3be476cab01c%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMiA6IDE5LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjE5LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BMTIuMcKwPC90ZD4KICAgICAgPHRkPjkxICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yMC4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjEyLjbCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5PdmVyY2FzdCBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDRkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4yPC90aD4KICAgICAgPHRkPjIxLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BOS4ywrA8L3RkPgogICAgICA8dGQ%2BMjUgJTwvdGQ%2BCiAgICAgIDx0ZD4yNSAlPC90ZD4KICAgICAgPHRkPjAuMzEyNSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_95ba3f173ac3402086ff421b88fa7bed.setContent%28i_frame_43d62cfa6c444da99e0c3be476cab01c%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_24f01e61cda04f5baef11c0e074b38b3.bindPopup%28popup_95ba3f173ac3402086ff421b88fa7bed%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_24f01e61cda04f5baef11c0e074b38b3.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%202%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_e45c768c32004e9aaa46e2d5f87dff00%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.858521%2C%202.381748%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_fbdc966f34444309a60da2f86cdf36dc%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e45c768c32004e9aaa46e2d5f87dff00.setIcon%28icon_fbdc966f34444309a60da2f86cdf36dc%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_70a7ecb314734dc1bd4b86099eaabc73%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_0da18f19a18b4231a384e9331cb64343%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMyA6IDIwLjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjIwLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BMTIuNMKwPC90ZD4KICAgICAgPHRkPjEwMCAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPk92ZXJjYXN0IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwNGQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjE8L3RoPgogICAgICA8dGQ%2BMjEuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD45LjTCsDwvdGQ%2BCiAgICAgIDx0ZD4yMyAlPC90ZD4KICAgICAgPHRkPjIwICU8L3RkPgogICAgICA8dGQ%2BMC4yNSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMjwvdGg%2BCiAgICAgIDx0ZD4yMi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjbCsDwvdGQ%2BCiAgICAgIDx0ZD40MCAlPC90ZD4KICAgICAgPHRkPjg1ICU8L3RkPgogICAgICA8dGQ%2BNC44MTI1IG1tL2hyPC90ZD4KICAgICAgPHRkPkxpZ2h0IHNob3dlciByYWluPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvcjA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_70a7ecb314734dc1bd4b86099eaabc73.setContent%28i_frame_0da18f19a18b4231a384e9331cb64343%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_e45c768c32004e9aaa46e2d5f87dff00.bindPopup%28popup_70a7ecb314734dc1bd4b86099eaabc73%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e45c768c32004e9aaa46e2d5f87dff00.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%203%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_cbb61130800a45a9bd05be5b9171577b%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.831108%2C%202.288868%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_3b6933b250a549f69f968fbe2f493127%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_cbb61130800a45a9bd05be5b9171577b.setIcon%28icon_3b6933b250a549f69f968fbe2f493127%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_baa16335fc2f40ffb34c86b0065eb357%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_8f7d438f4b4e4037af1fa366bf7b575a%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgNCA6IDIxLjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjIxLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BOS4ywrA8L3RkPgogICAgICA8dGQ%2BMjUgJTwvdGQ%2BCiAgICAgIDx0ZD4yNSAlPC90ZD4KICAgICAgPHRkPjAuMzEyNSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yMi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjYuMcKwPC90ZD4KICAgICAgPHRkPjQyICU8L3RkPgogICAgICA8dGQ%2BNzUgJTwvdGQ%2BCiAgICAgIDx0ZD4zIG1tL2hyPC90ZD4KICAgICAgPHRkPkJyb2tlbiBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDNkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4yPC90aD4KICAgICAgPHRkPjIzLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNS4xwrA8L3RkPgogICAgICA8dGQ%2BMTYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5GZXcgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_baa16335fc2f40ffb34c86b0065eb357.setContent%28i_frame_8f7d438f4b4e4037af1fa366bf7b575a%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_cbb61130800a45a9bd05be5b9171577b.bindPopup%28popup_baa16335fc2f40ffb34c86b0065eb357%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_cbb61130800a45a9bd05be5b9171577b.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%204%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%3C/script%3E onload="this.contentDocument.open();this.contentDocument.write(    decodeURIComponent(this.getAttribute('data-html')));this.contentDocument.close();" allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe></div></div>


    [1mFly ticket info[0m
    [1m____________________________________________________________________________________________________[0m
    [34m['TLV', 'CDG', '2021-11-17', '2021-11-24'][0m
    
    Cheapest_df
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>AirPorts_1</th>
      <th>Stops_1</th>
      <th>Duration_1</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_2</th>
      <th>Stops_2</th>
      <th>Duration_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-17</td>
      <td>8:30 pm – 9:10 am +1</td>
      <td>TLV - MLA - CDG</td>
      <td>1 stop</td>
      <td>13h 40</td>
      <td>2021-11-24</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 25</td>
      <td>317</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-17</td>
      <td>8:30 pm – 9:10 am +1</td>
      <td>TLV - MLA - CDG</td>
      <td>1 stop</td>
      <td>13h 40</td>
      <td>2021-11-24</td>
      <td>7:45 pm – 3:35 am +1</td>
      <td>CDG - WAW - TLV</td>
      <td>1 stop</td>
      <td>6h 50</td>
      <td>331</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-17</td>
      <td>8:30 pm – 9:10 am +1</td>
      <td>TLV - MLA - CDG</td>
      <td>1 stop</td>
      <td>13h 40</td>
      <td>2021-11-24</td>
      <td>2:45 pm – 8:00 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 15</td>
      <td>334</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-17</td>
      <td>8:30 pm – 9:10 am +1</td>
      <td>TLV - MLA - CDG</td>
      <td>1 stop</td>
      <td>13h 40</td>
      <td>2021-11-24</td>
      <td>7:55 pm – 2:50 am +1</td>
      <td>CDG - MUC - TLV</td>
      <td>1 stop</td>
      <td>5h 55</td>
      <td>347</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-17</td>
      <td>8:30 pm – 9:10 am +1</td>
      <td>TLV - MLA - CDG</td>
      <td>1 stop</td>
      <td>13h 40</td>
      <td>2021-11-24</td>
      <td>12:05 pm – 7:20 pm</td>
      <td>CDG - ATH - TLV</td>
      <td>1 stop</td>
      <td>6h 15</td>
      <td>350</td>
    </tr>
  </tbody>
</table>
</div>


    
    Quickest_query
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>AirPorts_1</th>
      <th>Stops_1</th>
      <th>Duration_1</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_2</th>
      <th>Stops_2</th>
      <th>Duration_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>4h 40</td>
      <td>2021-11-24</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 25</td>
      <td>495</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>4h 40</td>
      <td>2021-11-24</td>
      <td>7:55 pm – 2:50 am +1</td>
      <td>CDG - MUC - TLV</td>
      <td>1 stop</td>
      <td>5h 55</td>
      <td>506</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>4h 40</td>
      <td>2021-11-24</td>
      <td>8:10 pm – 3:30 am +1</td>
      <td>CDG - ZRH - TLV</td>
      <td>1 stop</td>
      <td>6h 20</td>
      <td>524</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>4h 40</td>
      <td>2021-11-24</td>
      <td>9:55 am – 5:25 pm</td>
      <td>CDG - ZRH - TLV</td>
      <td>1 stop</td>
      <td>6h 30</td>
      <td>524</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>4h 40</td>
      <td>2021-11-24</td>
      <td>7:45 pm – 3:35 am +1</td>
      <td>CDG - WAW - TLV</td>
      <td>1 stop</td>
      <td>6h 50</td>
      <td>493</td>
    </tr>
  </tbody>
</table>
</div>


    
    Early_Arrival_df
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_1</th>
      <th>Duration_1</th>
      <th>Stops_1</th>
      <th>AirPorts_2</th>
      <th>Duration_2</th>
      <th>Stops_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>2021-11-24</td>
      <td>12:05 pm – 12:55 am +1</td>
      <td>TLV - CDG</td>
      <td>4h 40</td>
      <td>nonstop</td>
      <td>CDG - ATH - TLV</td>
      <td>11h 50</td>
      <td>1 stop</td>
      <td>482</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-17</td>
      <td>5:30 am – 12:10 pm</td>
      <td>2021-11-24</td>
      <td>12:05 pm – 7:20 pm</td>
      <td>TLV - KBP - CDG</td>
      <td>7h 40</td>
      <td>1 stop</td>
      <td>CDG - ATH - TLV</td>
      <td>6h 15</td>
      <td>1 stop</td>
      <td>352</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-17</td>
      <td>8:30 pm – 9:10 am +1</td>
      <td>2021-11-24</td>
      <td>12:05 pm – 7:20 pm</td>
      <td>TLV - MLA - CDG</td>
      <td>13h 40</td>
      <td>1 stop</td>
      <td>CDG - ATH - TLV</td>
      <td>6h 15</td>
      <td>1 stop</td>
      <td>350</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>2021-11-24</td>
      <td>10:50 am – 2:50 am +1</td>
      <td>TLV - CDG</td>
      <td>4h 40</td>
      <td>nonstop</td>
      <td>CDG - MUC - TLV</td>
      <td>15h 0</td>
      <td>1 stop</td>
      <td>506</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-17</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>2021-11-24</td>
      <td>10:45 am – 3:35 am +1</td>
      <td>TLV - CDG</td>
      <td>4h 40</td>
      <td>nonstop</td>
      <td>CDG - WAW - TLV</td>
      <td>15h 50</td>
      <td>1 stop</td>
      <td>493</td>
    </tr>
  </tbody>
</table>
</div>


    [1m
    Travel info[0m
    [1m____________________________________________________________________________________________________[0m
    [1mOption 3
    Starts at 2021-11-23
    Return at 2021-11-30
    In average:
     - Rain chance per day is 16.734375%
     - Coluds chance per day 58.25%
    [0m
    


<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;"><span style="color:#565656">Make this Notebook Trusted to load map: File -> Trust Notebook</span><iframe src="about:blank" style="position:absolute;width:100%;height:100%;left:0;top:0;border:none !important;" data-html=%3C%21DOCTYPE%20html%3E%0A%3Chead%3E%20%20%20%20%0A%20%20%20%20%3Cmeta%20http-equiv%3D%22content-type%22%20content%3D%22text/html%3B%20charset%3DUTF-8%22%20/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%3Cscript%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20L_NO_TOUCH%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L_DISABLE_3D%20%3D%20false%3B%0A%20%20%20%20%20%20%20%20%3C/script%3E%0A%20%20%20%20%0A%20%20%20%20%3Cstyle%3Ehtml%2C%20body%20%7Bwidth%3A%20100%25%3Bheight%3A%20100%25%3Bmargin%3A%200%3Bpadding%3A%200%3B%7D%3C/style%3E%0A%20%20%20%20%3Cstyle%3E%23map%20%7Bposition%3Aabsolute%3Btop%3A0%3Bbottom%3A0%3Bright%3A0%3Bleft%3A0%3B%7D%3C/style%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//code.jquery.com/jquery-1.12.4.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/npm/leaflet%401.6.0/dist/leaflet.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css%22/%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css%22/%3E%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cmeta%20name%3D%22viewport%22%20content%3D%22width%3Ddevice-width%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20initial-scale%3D1.0%2C%20maximum-scale%3D1.0%2C%20user-scalable%3Dno%22%20/%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cstyle%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23map_cabcf3a57837415097e72f91298b6522%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20position%3A%20relative%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20width%3A%201250.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20height%3A%20550.0px%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20left%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20top%3A%200.0%25%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%3C/style%3E%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.css%22/%3E%0A%20%20%20%20%3Cscript%20src%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.js%22%3E%3C/script%3E%0A%20%20%20%20%3Clink%20rel%3D%22stylesheet%22%20href%3D%22https%3A//cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.css%22/%3E%0A%3C/head%3E%0A%3Cbody%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cdiv%20class%3D%22folium-map%22%20id%3D%22map_cabcf3a57837415097e72f91298b6522%22%20%3E%3C/div%3E%0A%20%20%20%20%20%20%20%20%0A%3C/body%3E%0A%3Cscript%3E%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20map_cabcf3a57837415097e72f91298b6522%20%3D%20L.map%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22map_cabcf3a57837415097e72f91298b6522%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20center%3A%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20crs%3A%20L.CRS.EPSG3857%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoom%3A%2010%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20zoomControl%3A%20true%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20preferCanvas%3A%20false%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tooltip%3A%20%22This%20tooltip%20will%20appear%20on%20hover%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.scale%28%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%0A%20%20%20%20%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_98f2a930a4014c428a2155810441cb22%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//stamen-tiles-%7Bs%7D.a.ssl.fastly.net/terrain/%7Bz%7D/%7Bx%7D/%7By%7D.jpg%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Map%20tiles%20by%20%5Cu003ca%20href%3D%5C%22http%3A//stamen.com%5C%22%5Cu003eStamen%20Design%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by/3.0%5C%22%5Cu003eCC%20BY%203.0%5Cu003c/a%5Cu003e.%20Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//creativecommons.org/licenses/by-sa/3.0%5C%22%5Cu003eCC%20BY%20SA%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20tile_layer_3d95c93c87d041479cca10054438a22e%20%3D%20L.tileLayer%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22https%3A//%7Bs%7D.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png%22%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22attribution%22%3A%20%22Data%20by%20%5Cu0026copy%3B%20%5Cu003ca%20href%3D%5C%22http%3A//openstreetmap.org%5C%22%5Cu003eOpenStreetMap%5Cu003c/a%5Cu003e%2C%20under%20%5Cu003ca%20href%3D%5C%22http%3A//www.openstreetmap.org/copyright%5C%22%5Cu003eODbL%5Cu003c/a%5Cu003e.%22%2C%20%22detectRetina%22%3A%20false%2C%20%22maxNativeZoom%22%3A%2018%2C%20%22maxZoom%22%3A%2018%2C%20%22minZoom%22%3A%200%2C%20%22noWrap%22%3A%20false%2C%20%22opacity%22%3A%201%2C%20%22subdomains%22%3A%20%22abc%22%2C%20%22tms%22%3A%20false%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20mini_map_86e26474cb1b4cc8b2728a500137e9b5%20%3D%20new%20L.Control.MiniMap%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20tile_layer_3d95c93c87d041479cca10054438a22e%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22autoToggleDisplay%22%3A%20false%2C%20%22centerFixed%22%3A%20false%2C%20%22collapsedHeight%22%3A%2025%2C%20%22collapsedWidth%22%3A%2025%2C%20%22height%22%3A%20150%2C%20%22minimized%22%3A%20false%2C%20%22position%22%3A%20%22bottomright%22%2C%20%22toggleDisplay%22%3A%20true%2C%20%22width%22%3A%20150%2C%20%22zoomAnimation%22%3A%20false%2C%20%22zoomLevelOffset%22%3A%20-5%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20map_cabcf3a57837415097e72f91298b6522.addControl%28mini_map_86e26474cb1b4cc8b2728a500137e9b5%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20L.control.fullscreen%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22forceSeparateButton%22%3A%20false%2C%20%22position%22%3A%20%22topright%22%2C%20%22title%22%3A%20%22Full%20Screen%22%2C%20%22titleCancel%22%3A%20%22Exit%20Full%20Screen%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_e0b1c9af2dac4786b54901d972fa394f%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_bd53012a09384222a90ee5aa53a2b91d%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.setIcon%28icon_bd53012a09384222a90ee5aa53a2b91d%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_9e71da34b58b4e2f98ffecee3a03f73d%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_891d2379eb1d401f82a53483e502bb77%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMSA6IDIzLjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjIzLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNC4ywrA8L3RkPgogICAgICA8dGQ%2BMTYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5GZXcgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNC4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjcuMsKwPC90ZD4KICAgICAgPHRkPjY3ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjUuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjHCsDwvdGQ%2BCiAgICAgIDx0ZD4xMiAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkZldyBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDJkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_9e71da34b58b4e2f98ffecee3a03f73d.setContent%28i_frame_891d2379eb1d401f82a53483e502bb77%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.bindPopup%28popup_9e71da34b58b4e2f98ffecee3a03f73d%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e0b1c9af2dac4786b54901d972fa394f.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%201%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_5257a3bd8c8848f5bc3548deaf88ce84%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.853167%2C%202.369163%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_ec987ca973a94b7ba816fd83be50bcf6%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.setIcon%28icon_ec987ca973a94b7ba816fd83be50bcf6%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_725b7571f9b04075a37443e9abaf8430%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_bea84eda0fc045d8bdfd5e4f760b5ab7%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMiA6IDI0LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI0LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNy41wrA8L3RkPgogICAgICA8dGQ%2BNjMgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNS4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjYuMsKwPC90ZD4KICAgICAgPHRkPjI1ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BU2NhdHRlcmVkIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwMmQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjYuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD42wrA8L3RkPgogICAgICA8dGQ%2BNjggJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_725b7571f9b04075a37443e9abaf8430.setContent%28i_frame_bea84eda0fc045d8bdfd5e4f760b5ab7%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.bindPopup%28popup_725b7571f9b04075a37443e9abaf8430%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_5257a3bd8c8848f5bc3548deaf88ce84.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%202%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_eb3e1b0dee3941b28ae92880c18178b5%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.858521%2C%202.381748%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_a50ecbc4ee194148abfe2625232d3d4a%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.setIcon%28icon_a50ecbc4ee194148abfe2625232d3d4a%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_2ddb09102d284bc3b4a2248403bbc924%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_6899eac92caf47908367498430bfe736%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMyA6IDI1LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI1LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNi4zwrA8L3RkPgogICAgICA8dGQ%2BMzYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjUuOMKwPC90ZD4KICAgICAgPHRkPjYxICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjcuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjjCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD43NSAlPC90ZD4KICAgICAgPHRkPjIuNzUgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_2ddb09102d284bc3b4a2248403bbc924.setContent%28i_frame_6899eac92caf47908367498430bfe736%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.bindPopup%28popup_2ddb09102d284bc3b4a2248403bbc924%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_eb3e1b0dee3941b28ae92880c18178b5.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%203%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.831108%2C%202.288868%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_38d21e3bf8d549a9984d0c4fb3de4aae%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.setIcon%28icon_38d21e3bf8d549a9984d0c4fb3de4aae%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_201766eb8afb4353847cecde0b658082%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_8da2526bb33243ffa842db6b987841a2%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMTwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgNCA6IDI2LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI2LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNsKwPC90ZD4KICAgICAgPHRkPjY4ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjE8L3RoPgogICAgICA8dGQ%2BMjcuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjjCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD43NSAlPC90ZD4KICAgICAgPHRkPjIuODc1IG1tL2hyPC90ZD4KICAgICAgPHRkPk92ZXJjYXN0IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwNGQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjguMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjnCsDwvdGQ%2BCiAgICAgIDx0ZD40NyAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkJyb2tlbiBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDNkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_201766eb8afb4353847cecde0b658082.setContent%28i_frame_8da2526bb33243ffa842db6b987841a2%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.bindPopup%28popup_201766eb8afb4353847cecde0b658082%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_6e9e9ab18bac4aa3a25ae1a7a2dba355.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%204%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_65de7cf812c449c0974e12196c28a456%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_8da58a8bcdfd4170a04a07f235896e1f%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_65de7cf812c449c0974e12196c28a456.setIcon%28icon_8da58a8bcdfd4170a04a07f235896e1f%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_46fd1515d3d44bae989e48e587a6e190%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_26671622bad947ec9bae10f5766d09d6%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMSA6IDE4LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjE4LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BOcKwPC90ZD4KICAgICAgPHRkPjc5ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4xOS4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjExLjnCsDwvdGQ%2BCiAgICAgIDx0ZD45MCAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPk92ZXJjYXN0IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwNGQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjAuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD4xMS45wrA8L3RkPgogICAgICA8dGQ%2BMTAwICU8L3RkPgogICAgICA8dGQ%2BMjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wLjA2MjUgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_46fd1515d3d44bae989e48e587a6e190.setContent%28i_frame_26671622bad947ec9bae10f5766d09d6%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_65de7cf812c449c0974e12196c28a456.bindPopup%28popup_46fd1515d3d44bae989e48e587a6e190%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_65de7cf812c449c0974e12196c28a456.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%201%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_24f01e61cda04f5baef11c0e074b38b3%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.853167%2C%202.369163%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_6bb8987340ac4ec0bd6979bbe5c1dc56%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_24f01e61cda04f5baef11c0e074b38b3.setIcon%28icon_6bb8987340ac4ec0bd6979bbe5c1dc56%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_95ba3f173ac3402086ff421b88fa7bed%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_43d62cfa6c444da99e0c3be476cab01c%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMiA6IDE5LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjE5LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BMTIuMcKwPC90ZD4KICAgICAgPHRkPjkxICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BT3ZlcmNhc3QgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yMC4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjEyLjbCsDwvdGQ%2BCiAgICAgIDx0ZD4xMDAgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5PdmVyY2FzdCBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDRkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4yPC90aD4KICAgICAgPHRkPjIxLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BOS4ywrA8L3RkPgogICAgICA8dGQ%2BMjUgJTwvdGQ%2BCiAgICAgIDx0ZD4yNSAlPC90ZD4KICAgICAgPHRkPjAuMzEyNSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_95ba3f173ac3402086ff421b88fa7bed.setContent%28i_frame_43d62cfa6c444da99e0c3be476cab01c%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_24f01e61cda04f5baef11c0e074b38b3.bindPopup%28popup_95ba3f173ac3402086ff421b88fa7bed%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_24f01e61cda04f5baef11c0e074b38b3.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%202%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_e45c768c32004e9aaa46e2d5f87dff00%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.858521%2C%202.381748%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_fbdc966f34444309a60da2f86cdf36dc%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e45c768c32004e9aaa46e2d5f87dff00.setIcon%28icon_fbdc966f34444309a60da2f86cdf36dc%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_70a7ecb314734dc1bd4b86099eaabc73%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_0da18f19a18b4231a384e9331cb64343%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMyA6IDIwLjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjIwLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BMTIuNMKwPC90ZD4KICAgICAgPHRkPjEwMCAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPk92ZXJjYXN0IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwNGQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjE8L3RoPgogICAgICA8dGQ%2BMjEuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD45LjTCsDwvdGQ%2BCiAgICAgIDx0ZD4yMyAlPC90ZD4KICAgICAgPHRkPjIwICU8L3RkPgogICAgICA8dGQ%2BMC4yNSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMjwvdGg%2BCiAgICAgIDx0ZD4yMi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjbCsDwvdGQ%2BCiAgICAgIDx0ZD40MCAlPC90ZD4KICAgICAgPHRkPjg1ICU8L3RkPgogICAgICA8dGQ%2BNC44MTI1IG1tL2hyPC90ZD4KICAgICAgPHRkPkxpZ2h0IHNob3dlciByYWluPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvcjA0ZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_70a7ecb314734dc1bd4b86099eaabc73.setContent%28i_frame_0da18f19a18b4231a384e9331cb64343%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_e45c768c32004e9aaa46e2d5f87dff00.bindPopup%28popup_70a7ecb314734dc1bd4b86099eaabc73%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_e45c768c32004e9aaa46e2d5f87dff00.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%203%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_cbb61130800a45a9bd05be5b9171577b%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.831108%2C%202.288868%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_3b6933b250a549f69f968fbe2f493127%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_cbb61130800a45a9bd05be5b9171577b.setIcon%28icon_3b6933b250a549f69f968fbe2f493127%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_baa16335fc2f40ffb34c86b0065eb357%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_8f7d438f4b4e4037af1fa366bf7b575a%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMjwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgNCA6IDIxLjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjIxLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BOS4ywrA8L3RkPgogICAgICA8dGQ%2BMjUgJTwvdGQ%2BCiAgICAgIDx0ZD4yNSAlPC90ZD4KICAgICAgPHRkPjAuMzEyNSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yMi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjYuMcKwPC90ZD4KICAgICAgPHRkPjQyICU8L3RkPgogICAgICA8dGQ%2BNzUgJTwvdGQ%2BCiAgICAgIDx0ZD4zIG1tL2hyPC90ZD4KICAgICAgPHRkPkJyb2tlbiBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDNkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4yPC90aD4KICAgICAgPHRkPjIzLjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNS4xwrA8L3RkPgogICAgICA8dGQ%2BMTYgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5GZXcgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_baa16335fc2f40ffb34c86b0065eb357.setContent%28i_frame_8f7d438f4b4e4037af1fa366bf7b575a%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_cbb61130800a45a9bd05be5b9171577b.bindPopup%28popup_baa16335fc2f40ffb34c86b0065eb357%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_cbb61130800a45a9bd05be5b9171577b.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%204%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_1a1b70566ba7400990ff54c274a83bb5%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B49.01423%2C%202.521019%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_a6bbd036326e4fdb917a8eaf35fc535b%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_1a1b70566ba7400990ff54c274a83bb5.setIcon%28icon_a6bbd036326e4fdb917a8eaf35fc535b%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_c16bc2536d70454584ff2c8376f440af%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_68d070a8888b4e2581587521ec4867cd%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMzwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMSA6IDI0LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI0LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNy4ywrA8L3RkPgogICAgICA8dGQ%2BNjcgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNS4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjUuMcKwPC90ZD4KICAgICAgPHRkPjEyICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BRmV3IGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwMmQucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICAgIDx0cj4KICAgICAgPHRoPjI8L3RoPgogICAgICA8dGQ%2BMjYuMTEuMjAyMTwvdGQ%2BCiAgICAgIDx0ZD41LjHCsDwvdGQ%2BCiAgICAgIDx0ZD41NCAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkJyb2tlbiBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDNkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_c16bc2536d70454584ff2c8376f440af.setContent%28i_frame_68d070a8888b4e2581587521ec4867cd%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_1a1b70566ba7400990ff54c274a83bb5.bindPopup%28popup_c16bc2536d70454584ff2c8376f440af%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_1a1b70566ba7400990ff54c274a83bb5.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%201%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_cd511172a34d47cfbc39b276183f7548%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.853167%2C%202.369163%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_11e745333ddd46c78430d03b2b1a0e6e%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_cd511172a34d47cfbc39b276183f7548.setIcon%28icon_11e745333ddd46c78430d03b2b1a0e6e%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_685e093343fe4a2ba9035280ba1d422a%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_f794ba1b889c432f8ed42a7632189ba8%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMzwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMiA6IDI1LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI1LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNi4ywrA8L3RkPgogICAgICA8dGQ%2BMjUgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNi4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjbCsDwvdGQ%2BCiAgICAgIDx0ZD42OCAlPC90ZD4KICAgICAgPHRkPjAgJTwvdGQ%2BCiAgICAgIDx0ZD4wIG1tL2hyPC90ZD4KICAgICAgPHRkPkJyb2tlbiBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDNkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4yPC90aD4KICAgICAgPHRkPjI3LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNS44wrA8L3RkPgogICAgICA8dGQ%2BMTAwICU8L3RkPgogICAgICA8dGQ%2BNzUgJTwvdGQ%2BCiAgICAgIDx0ZD4yLjg3NSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5PdmVyY2FzdCBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDRkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgPC90Ym9keT4KPC90YWJsZT48L3A%2BCiAgICAgICAgICAgICAgICAgICAgPC9ib2R5PgogICAgICAgICAgICAgICAgICAgIA%3D%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_685e093343fe4a2ba9035280ba1d422a.setContent%28i_frame_f794ba1b889c432f8ed42a7632189ba8%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_cd511172a34d47cfbc39b276183f7548.bindPopup%28popup_685e093343fe4a2ba9035280ba1d422a%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_cd511172a34d47cfbc39b276183f7548.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%202%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_0e6d7c54b9a34621be04600abed48f35%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.858521%2C%202.381748%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_840894b41351485daefe2ef0f13af54f%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_0e6d7c54b9a34621be04600abed48f35.setIcon%28icon_840894b41351485daefe2ef0f13af54f%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_2c246ef43da84fd0ad75dc48a9679963%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_13c165a049484f3d99cd7769b47367f1%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMzwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgMyA6IDI2LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI2LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNS44wrA8L3RkPgogICAgICA8dGQ%2BNjEgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMTwvdGg%2BCiAgICAgIDx0ZD4yNy4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjUuOMKwPC90ZD4KICAgICAgPHRkPjEwMCAlPC90ZD4KICAgICAgPHRkPjc1ICU8L3RkPgogICAgICA8dGQ%2BMi43NSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5PdmVyY2FzdCBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDRkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4yPC90aD4KICAgICAgPHRkPjI4LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNS44wrA8L3RkPgogICAgICA8dGQ%2BMzEgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5TY2F0dGVyZWQgY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAyZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogIDwvdGJvZHk%2BCjwvdGFibGU%2BPC9wPgogICAgICAgICAgICAgICAgICAgIDwvYm9keT4KICAgICAgICAgICAgICAgICAgICA%3D%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_2c246ef43da84fd0ad75dc48a9679963.setContent%28i_frame_13c165a049484f3d99cd7769b47367f1%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_0e6d7c54b9a34621be04600abed48f35.bindPopup%28popup_2c246ef43da84fd0ad75dc48a9679963%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_0e6d7c54b9a34621be04600abed48f35.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%203%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20marker_373dd3ad248040f586e2d178f2f293d7%20%3D%20L.marker%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%5B48.831108%2C%202.288868%5D%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29.addTo%28map_cabcf3a57837415097e72f91298b6522%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20icon_fb39482b7dbe48a796ec97d8d7cea574%20%3D%20L.AwesomeMarkers.icon%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22extraClasses%22%3A%20%22fa-rotate-0%22%2C%20%22icon%22%3A%20%22info-sign%22%2C%20%22iconColor%22%3A%20%22white%22%2C%20%22markerColor%22%3A%20%22purple%22%2C%20%22prefix%22%3A%20%22glyphicon%22%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_373dd3ad248040f586e2d178f2f293d7.setIcon%28icon_fb39482b7dbe48a796ec97d8d7cea574%29%3B%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20var%20popup_48f4bbf969234582b3824530dee63ed1%20%3D%20L.popup%28%7B%22maxWidth%22%3A%20600%7D%29%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20var%20i_frame_66c1e2895fd14234b821a087e21e69ce%20%3D%20%24%28%60%3Ciframe%20src%3D%22data%3Atext/html%3Bcharset%3Dutf-8%3Bbase64%2CCiAgICAKICAgICAgICAgICAgICAgICAgICA8Ym9keSBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjojY2NjY2ZmOyI%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5PcHRpb24gMzwvaDM%2BCiAgICAgICAgICAgICAgICAgICAgICAgIDxoMj5EYXkgNCA6IDI3LjExLjIwMjEgPC9oMj4KICAgICAgICAgICAgICAgICAgICAgICAgPHA%2BPHRhYmxlIGJvcmRlcj0iMSIgY2xhc3M9ImRhdGFmcmFtZSI%2BCiAgPHRoZWFkPgogICAgPHRyIHN0eWxlPSJ0ZXh0LWFsaWduOiBjZW50ZXI7Ij4KICAgICAgPHRoPjwvdGg%2BCiAgICAgIDx0aD5EYXRlPC90aD4KICAgICAgPHRoPlRlbXA8L3RoPgogICAgICA8dGg%2BQ2xvdWRzPC90aD4KICAgICAgPHRoPlJhaW4gQ2hhbmNlPC90aD4KICAgICAgPHRoPlByZWNpcGl0YXRpb248L3RoPgogICAgICA8dGg%2BRGVzY3JpcHRpb248L3RoPgogICAgICA8dGg%2BU3RhdHVzPC90aD4KICAgIDwvdHI%2BCiAgPC90aGVhZD4KICA8dGJvZHk%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4wPC90aD4KICAgICAgPHRkPjI3LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNS44wrA8L3RkPgogICAgICA8dGQ%2BMTAwICU8L3RkPgogICAgICA8dGQ%2BNzUgJTwvdGQ%2BCiAgICAgIDx0ZD4yLjg3NSBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5PdmVyY2FzdCBjbG91ZHM8L3RkPgogICAgICA8dGQ%2BPGltZyBzcmM9Imh0dHBzOi8vd3d3LndlYXRoZXJiaXQuaW8vc3RhdGljL2ltZy9pY29ucy9jMDRkLnBuZyIgd2lkdGg9IjYwIiA%2BPC90ZD4KICAgIDwvdHI%2BCiAgICA8dHI%2BCiAgICAgIDx0aD4xPC90aD4KICAgICAgPHRkPjI4LjExLjIwMjE8L3RkPgogICAgICA8dGQ%2BNS45wrA8L3RkPgogICAgICA8dGQ%2BNDcgJTwvdGQ%2BCiAgICAgIDx0ZD4wICU8L3RkPgogICAgICA8dGQ%2BMCBtbS9ocjwvdGQ%2BCiAgICAgIDx0ZD5Ccm9rZW4gY2xvdWRzPC90ZD4KICAgICAgPHRkPjxpbWcgc3JjPSJodHRwczovL3d3dy53ZWF0aGVyYml0LmlvL3N0YXRpYy9pbWcvaWNvbnMvYzAzZC5wbmciIHdpZHRoPSI2MCIgPjwvdGQ%2BCiAgICA8L3RyPgogICAgPHRyPgogICAgICA8dGg%2BMjwvdGg%2BCiAgICAgIDx0ZD4yOS4xMS4yMDIxPC90ZD4KICAgICAgPHRkPjEuN8KwPC90ZD4KICAgICAgPHRkPjQ2ICU8L3RkPgogICAgICA8dGQ%2BMCAlPC90ZD4KICAgICAgPHRkPjAgbW0vaHI8L3RkPgogICAgICA8dGQ%2BQnJva2VuIGNsb3VkczwvdGQ%2BCiAgICAgIDx0ZD48aW1nIHNyYz0iaHR0cHM6Ly93d3cud2VhdGhlcmJpdC5pby9zdGF0aWMvaW1nL2ljb25zL2MwM2QucG5nIiB3aWR0aD0iNjAiID48L3RkPgogICAgPC90cj4KICA8L3Rib2R5Pgo8L3RhYmxlPjwvcD4KICAgICAgICAgICAgICAgICAgICA8L2JvZHk%2BCiAgICAgICAgICAgICAgICAgICAg%22%20width%3D%22540%22%20style%3D%22border%3Anone%20%21important%3B%22%20height%3D%22360%22%3E%3C/iframe%3E%60%29%5B0%5D%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20popup_48f4bbf969234582b3824530dee63ed1.setContent%28i_frame_66c1e2895fd14234b821a087e21e69ce%29%3B%0A%20%20%20%20%20%20%20%20%0A%0A%20%20%20%20%20%20%20%20marker_373dd3ad248040f586e2d178f2f293d7.bindPopup%28popup_48f4bbf969234582b3824530dee63ed1%29%0A%20%20%20%20%20%20%20%20%3B%0A%0A%20%20%20%20%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%20%20marker_373dd3ad248040f586e2d178f2f293d7.bindTooltip%28%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%60%3Cdiv%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20Day%204%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3C/div%3E%60%2C%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%22sticky%22%3A%20true%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%29%3B%0A%20%20%20%20%20%20%20%20%0A%3C/script%3E onload="this.contentDocument.open();this.contentDocument.write(    decodeURIComponent(this.getAttribute('data-html')));this.contentDocument.close();" allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe></div></div>


    [1mFly ticket info[0m
    [1m____________________________________________________________________________________________________[0m
    [34m['TLV', 'CDG', '2021-11-23', '2021-11-30'][0m
    
    Cheapest_df
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>AirPorts_1</th>
      <th>Stops_1</th>
      <th>Duration_1</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_2</th>
      <th>Stops_2</th>
      <th>Duration_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-23</td>
      <td>5:30 am – 12:10 pm</td>
      <td>TLV - KBP - CDG</td>
      <td>1 stop</td>
      <td>7h 40</td>
      <td>2021-11-30</td>
      <td>1:20 pm – 11:10 pm</td>
      <td>CDG - KBP - TLV</td>
      <td>1 stop</td>
      <td>8h 50</td>
      <td>321</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-23</td>
      <td>5:30 am – 12:10 pm</td>
      <td>TLV - KBP - CDG</td>
      <td>1 stop</td>
      <td>7h 40</td>
      <td>2021-11-30</td>
      <td>6:45 pm – 3:10 am +1</td>
      <td>CDG - FCO - TLV</td>
      <td>1 stop</td>
      <td>7h 25</td>
      <td>322</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-23</td>
      <td>7:35 am – 2:10 pm</td>
      <td>TLV - ZRH - CDG</td>
      <td>1 stop</td>
      <td>7h 35</td>
      <td>2021-11-30</td>
      <td>8:10 pm – 3:30 am +1</td>
      <td>CDG - ZRH - TLV</td>
      <td>1 stop</td>
      <td>6h 20</td>
      <td>327</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-23</td>
      <td>7:35 am – 7:15 pm</td>
      <td>TLV - ZRH - CDG</td>
      <td>1 stop</td>
      <td>12h 40</td>
      <td>2021-11-30</td>
      <td>8:10 pm – 3:30 am +1</td>
      <td>CDG - ZRH - TLV</td>
      <td>1 stop</td>
      <td>6h 20</td>
      <td>327</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-23</td>
      <td>7:35 am – 2:10 pm</td>
      <td>TLV - ZRH - CDG</td>
      <td>1 stop</td>
      <td>7h 35</td>
      <td>2021-11-30</td>
      <td>3:15 pm – 3:30 am +1</td>
      <td>CDG - ZRH - TLV</td>
      <td>1 stop</td>
      <td>11h 15</td>
      <td>327</td>
    </tr>
  </tbody>
</table>
</div>


    
    Quickest_query
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>AirPorts_1</th>
      <th>Stops_1</th>
      <th>Duration_1</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_2</th>
      <th>Stops_2</th>
      <th>Duration_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-23</td>
      <td>9:00 am – 1:00 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 0</td>
      <td>2021-11-30</td>
      <td>2:45 pm – 8:00 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 15</td>
      <td>715</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-23</td>
      <td>4:50 pm – 8:55 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 5</td>
      <td>2021-11-30</td>
      <td>2:45 pm – 8:00 pm</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 15</td>
      <td>636</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-23</td>
      <td>9:00 am – 1:00 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 0</td>
      <td>2021-11-30</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 25</td>
      <td>685</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-23</td>
      <td>4:50 pm – 8:55 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>5h 5</td>
      <td>2021-11-30</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>CDG - TLV</td>
      <td>nonstop</td>
      <td>4h 25</td>
      <td>607</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-23</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>TLV - CDG</td>
      <td>nonstop</td>
      <td>4h 40</td>
      <td>2021-11-30</td>
      <td>6:40 pm – 2:20 am +1</td>
      <td>CDG - AMS - TLV</td>
      <td>1 stop</td>
      <td>6h 40</td>
      <td>586</td>
    </tr>
  </tbody>
</table>
</div>


    
    Early_Arrival_df
    


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>Depart_Date</th>
      <th>Depart_Time</th>
      <th>Return_Date</th>
      <th>Return_Time</th>
      <th>AirPorts_1</th>
      <th>Duration_1</th>
      <th>Stops_1</th>
      <th>AirPorts_2</th>
      <th>Duration_2</th>
      <th>Stops_2</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2021-11-23</td>
      <td>3:55 pm – 7:35 pm</td>
      <td>2021-11-30</td>
      <td>12:40 pm – 2:20 am +1</td>
      <td>TLV - CDG</td>
      <td>4h 40</td>
      <td>nonstop</td>
      <td>CDG - AMS - TLV</td>
      <td>12h 40</td>
      <td>1 stop</td>
      <td>561</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021-11-23</td>
      <td>5:30 am – 12:10 pm</td>
      <td>2021-11-30</td>
      <td>12:00 pm – 10:30 pm</td>
      <td>TLV - KBP - CDG</td>
      <td>7h 40</td>
      <td>1 stop</td>
      <td>CDG - OTP - TLV</td>
      <td>9h 30</td>
      <td>1 stop</td>
      <td>402</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2021-11-23</td>
      <td>10:00 pm – 11:00 am +1</td>
      <td>2021-11-30</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>TLV - OTP - CDG</td>
      <td>14h 0</td>
      <td>1 stop</td>
      <td>CDG - TLV</td>
      <td>4h 25</td>
      <td>nonstop</td>
      <td>373</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2021-11-23</td>
      <td>11:30 pm – 11:00 am +1</td>
      <td>2021-11-30</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>TLV - OTP - CDG</td>
      <td>12h 30</td>
      <td>1 stop</td>
      <td>CDG - TLV</td>
      <td>4h 25</td>
      <td>nonstop</td>
      <td>368</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2021-11-23</td>
      <td>4:50 pm – 8:55 pm</td>
      <td>2021-11-30</td>
      <td>10:30 pm – 3:55 am +1</td>
      <td>TLV - CDG</td>
      <td>5h 5</td>
      <td>nonstop</td>
      <td>CDG - TLV</td>
      <td>4h 25</td>
      <td>nonstop</td>
      <td>607</td>
    </tr>
  </tbody>
</table>
</div>

