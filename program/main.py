from program.Input_data import input_data
from program.Trip_Map import trip_Map
from IPython.display import display


def run_app():
    print("Departure from: TLV\n"
          "Destination: valbona\n"
          "Chose day to fly: 24.09.2021\n"
          "Chose day to return: 03.10.2021\n")
    user_info = input_data.all_ticket_options()

    return input_data.draw_on_map(user_info), user_info


results = run_app()






