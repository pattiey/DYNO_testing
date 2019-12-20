import sys
import matplotlib
import pandas as pd
import numpy as np
import argparse
import datetime

def load_data(dyno_file):
    df = pd.read_csv(dyno_file, sep = "\t")
    return(df)

def find_previous_pb(name, team, past_data):
    data = past_data[past_data['Name'] == name]
    data = data[data['Team'] == team]
    if data.shape[0] == 0:
        return None

    return max(data['Press + Pull'])

def find_percent_gain(pb, score):
    # print(data)
    if pb is None:
        return None
    return ((score - pb)/pb) * 100

def filter_team(data, team):
    if team is 'all':
        return data
    if "M" in team:
        data = data[data['Team'].str.contains("Men's")]
    if "W" in team:
        data = data[data['Team'].str.contains("Women's")]
    if "V" in team:
        data = data[data['Team'].str.contains("Varsity")]
    if "N" in team:
        data = data[data['Team'].str.contains("Novice")]
    return data

def main(dyno_file, current_month, team):
    df = load_data(dyno_file)
    df = filter_team(df, team)
    data_month = df['Timestamp'].apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y %H:%M:%S').month)
    df['Press + Pull'] = df['Leg Press'] + df['Arm Pull']

    current_data = df.loc[data_month == current_month].copy()
    past_data = df.loc[data_month < current_month].copy()

    current_data['Previous PB'] = current_data.apply(lambda x: find_previous_pb(x['Name'], x['Team'], past_data), axis = 1)

    current_data['Percent Gain'] = current_data.apply(lambda x: find_percent_gain(x['Previous PB'], x['Press + Pull']), axis = 1)

    current_data = current_data.sort_values(by = ['Press + Pull'], ascending = False)
    current_data = current_data.drop('Timestamp', axis = 1)
    return current_data

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-F', required = True, help = "Raw DYNO data file")
    arg_parser.add_argument('-M', default = datetime.datetime.now().month, type = int, help = "Month of interest")
    arg_parser.add_argument('-T', default = 'all', help = "Team, enter M for men's varsity and novice,\
     W for women's varisty and novice, \
     V for men's and women's varsity, \
     N for men's and women's novice,\
     MV for men's varsity, \
     WV for women's varsity, \
     MN for men's novice, \
     WV for women's novice, \
     all for all teams")

    args = arg_parser.parse_args()
    dyno_file = args.F
    current_month = args.M
    team = args.T
    data = main(dyno_file, current_month, team)
    data.to_csv(f'{team}_DYNO_results_{datetime.date(1900, current_month, 1).strftime("%B")}_{datetime.datetime.now().year}.tsv', sep = "\t", index = False)
