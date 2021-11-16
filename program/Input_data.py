from geopy.geocoders import Nominatim
from folium import plugins
import datetime
from datetime import timedelta, datetime, date
import folium


class input_data:

    def cast_date(self, dt):
        """
        casting function
        :return: return date i format of date
        """
        date_str = datetime.strptime(dt, "%d.%m.%Y").strftime("%Y-%m-%d")
        return date(*map(int, date_str.split('-')))

    def all_ticket_options(self):
        """
        function receives input from the user and checks for correctness and adds to the dates 4 days
        ahead and four days later if possible and returns a list of optional days
        :return: list
        """
        departure_from = input("Departure from: ")
        destination = input("Destination: ")
        chosen_day = self.cast_date(input("Chose day to fly: "))
        return_day = self.cast_date(input("Chose day to return: "))
        # check if date insert to fly is not passed
        today_date = date.today()

        if today_date < chosen_day < return_day and (return_day - chosen_day).days < 16:
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

    def draw_on_map(self, user_info):
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
        plugins.Fullscreen(position='topright').add_to(map_with_mini)  # choosing map type
        # add measures
        measure_control = plugins.MeasureControl(position='topleft',
                                                 active_color='purple',
                                                 completed_color='purpule',
                                                 primary_length_unit='kilometers')
        map_with_mini.add_child(measure_control)

        # add tools and export=True exports the drawn shapes as a geojson file
        draw = plugins.Draw(filename='MyMap', export=True)
        draw.add_to(map_with_mini)

        # save map
        map_with_mini.save('MyMap.html')

        return map_with_mini



