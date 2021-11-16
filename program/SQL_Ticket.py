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