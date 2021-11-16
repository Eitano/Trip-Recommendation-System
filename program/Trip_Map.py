# import
import folium
from folium import plugins
from IPython.core.display import display, HTML
import json
import os
from termcolor import colored
from program.Foecast import forecast
from program.SQL_Ticket import sql_ticket


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
        if show_:  # show the dictionary
            print(get_best_day)
        get_best_day = get_best_day[:options]  # get amount of result from dictionary

        print(colored("\nDisplay maps as option 1 is the rank the heights\n", 'green', attrs=['bold']))  # title
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

            mayMap.save('Map_Option_{} , {}.html'.format(opt[4][0], opt[4][1]))  # save map
            result_Dict = {"Start": opt[4][0], "End": opt[4][1], "Avg_Rain": opt[2], "Avg_Clouds": opt[3]}

            # print info about the sequence of days suitable for the trip
            print(colored('\nTravel info', attrs=['bold']))
            print(colored('_' * 100, attrs=['bold']))
            print(colored
                  (
                  "Option {}\nStarts at {}\nReturn at {}\nIn average:\n - Rain chance per day is {}%\n - Coluds chance per day {}%\n"
                  .format(opt_num, result_Dict.get('Start'), result_Dict.get('End'), result_Dict.get('Avg_Rain'),
                          result_Dict.get('Avg_Clouds')),
                  attrs=['bold']))
            display(mayMap)  # show map

            # using sql query retrieve information on tickets based on querys implement at run_sky_scanner function
            print(colored('Fly ticket info', attrs=['bold']))
            print(colored('_' * 100, attrs=['bold']))
            print(colored(ls_info[:2] + [result_Dict.get('Start'), result_Dict.get('End')], 'blue'))
            sql_ticket().run_sky_scanner(ls_info[:2] + [result_Dict.get('Start'), result_Dict.get('End')])
            opt_num += 1
    except Exception as e:
        print(e)
    finally:
        return