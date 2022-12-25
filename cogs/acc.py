import json
import logging
import boto3

import discord
import os
from datetime import timedelta
from discord.ext import commands, tasks
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import requests
from datetime import datetime
from itertools import groupby
from operator import itemgetter

session_over = 0
first_overall = ""
first_time = ""
second_time = ""
third_time = ""
second_overall = ""
third_overall = ""
track_name = ""

aws_region = 'us-east-1'
key = 'AKIAXKJBRD7GJZPZXWG3'
secret = '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'


class acc(commands.Cog):
    def __init__(self, bot):
        self.db = boto3.resource('dynamodb',
                                 region_name=aws_region,
                                 aws_access_key_id=key,
                                 aws_secret_access_key=secret)
        self.track = ""
        self.bot = bot
        self.app_state = {}
        self.ranked_drivers = []
        self.total_driving_time = {}
        self.car_list = {
            "0": "Porsche 991 GT3 R",
            "1": "Mercedes AMG GT3",
            "2": "Ferrari 488 GT3",
            "3": "Audi R8 LMS",
            "4": "Lamborghini Huracan GT3",
            "5": "McLaren 650S GT3",
            "6": "Nissan GT-R Nismo GT3",
            "7": "BMW M6 GT3",
            "8": "Bentley Continental GT3",
            "9": "Porsche 991II GT3 Cup",
            "10": "Nissan GT-R Nismo GT3",
            "11": "Bentley Continental GT3",
            "12": "AMR V12 Vantage GT3",
            "13": "Reiter Engineering R-EX",
            "14": "Emil Frey Jaguar G3",
            "15": "Lexus RC F GT3",
            "16": "Lamborghini Huracan GT3",
            "17": "Honda NSX GT3",
            "18": "Lamborghini Huracan ST",
            "19": "Audi R8 LMS evo",
            "20": "AMR V8 Vantage GT3",
            "21": "Honda NSX GT3 Evo",
            "22": "McLaren 720S GT3",
            "23": "Porsche 991II GT3 R",
            "24": "Ferrari 488 GT3 evo",
            "25": "Mercedes AMG GT3 2020",
            "26": "Ferrari 488 Challenge",
            "27": "BMW M2 CS Racing",
            "28": "Porsche 992 GT3 Cup",
            "29": "Lamborghini Huracan ST",
            "30": "BMW M4 GT3",
            "31": "Audi R8 LMS evo II",
            "32": "Audi R8 LMS evo IIb",
        }
        self.mfc_list = {
            "0": "porsche",
            "1": "mercedes",
            "2": "ferrari",
            "3": "audi",
            "4": "lambo",
            "5": "mclaren",
            "6": "nissan",
            "7": "bmw",
            "8": "bentley",
            "9": "porsche",
            "10": "nissan",
            "11": "bentley",
            "12": "aston",
            "13": "reiter",
            "14": "jaguar",
            "15": "lexus",
            "16": "lambo",
            "17": "honda",
            "18": "lambo",
            "19": "audi",
            "20": "aston",
            "21": "honda",
            "22": "mclaren",
            "23": "porsche",
            "24": "ferrari",
            "25": "mercedes",
            "26": "ferrari",
            "27": "bmw",
            "28": "porsche",
            "29": "lambo",
            "30": "bmw",
            "31": "audi",
            "32": "audi",
        }
        self.pnt_list = {
            "0": "25",
            "1": "18",
            "2": "15",
            "3": "12",
            "4": "10",
            "5": "8",
            "6": "6",
            "7": "4",
            "8": "2",
            "9": "1",
            "10": "0",
            "11": "0",
            "12": "0",
            "13": "0",
            "14": "0",
            "15": "0",
            "16": "0",
            "17": "0",
            "18": "0",
            "19": "0",
            "20": "0"
        }

    def get_top_players_by_points(self, number_of_players: int = 99):
        """
            Function retrieve data from DynamoDb, group points by player_name, and sorts by total points
            :param number_of_players: Integer value of how many TOP players to return.
                Default is 10.
            :return: Array of sorted by points players.
        """
        data = self.get_table_data('points')
        data.sort(key=itemgetter('player_name'))

        grouped_data = []
        for player, items in groupby(data, key=itemgetter("player_name")):
            grouped_data.append({
                "player_name": player,
                "points": sum(int(item['points']) for item in items)
            })
        grouped_data.sort(key=itemgetter("points"), reverse=True)
        print(f"TOP {number_of_players} players by points: {grouped_data[:number_of_players]} ")
        return grouped_data[:number_of_players]

    def put(self, table_name: str, data: dict):
        logging.debug(f"SAVE to DB:", data)
        self.db.Table(table_name).put_item(Item=data)

    def get_table_data(self, table_name: str) -> list:
        """
            @:param table_name: Name of the Table to read from
            @:return: Array of records
        """
        result = self.db.Table(table_name).scan()
        return result['Items']


    @staticmethod
    def parse_date_to_ms(str_time) -> int:
        """
            @:param str_time    string in format "mm:ss.SSS".
                                Example: "01:10:548"
            @:returns   Time in milliseconds (int).
                        Example: 70548
        """
        # print(f"DEBUG: Parsing {str_time}")
        # if not str_time.startswith("--:--"):
        duration_ms = 0
        try:
            split1 = str_time.split(":")
            if len(split1) > 2:
                # print(f"================================ {str_time} ===============================")
                hours = int(split1[0])
                minutes = int(split1[1])
            else:
                hours = 0
                minutes = int(split1[0])
            split2 = split1[-1].split(".")
            seconds = int(split2[0])
            ms = int(split2[1])

            duration_ms = hours * 3660 * 1000 + minutes * 60 * 1000 + seconds * 1000 + ms
        except ValueError:
            logging.error(f"Error in {__name__}: Can't parse {str_time} : {ValueError}")
        finally:
            return duration_ms
        # else:
        #     return 0

    @staticmethod
    def parse_ms_to_time(int_time) -> str:
        return str(timedelta(milliseconds=int_time))

    @staticmethod
    def track_convert(self, name):
        if name == "Circuit Zolder":
            return "zolder"

    def update_total_driving_time(self):
        for broadcast_car in self.app_state["BROADCASTING_EVENT"].values():
            car_id = str(broadcast_car['CarId'])
            lap_duration = broadcast_car['Msg']
            if not lap_duration == "--:--.---":
                if car_id in self.total_driving_time.keys():
                    car_stats = self.total_driving_time[car_id]
                    if lap_duration != car_stats['last_lap_duration']:
                        duration_ms = car_stats['duration_ms'] + self.parse_date_to_ms(lap_duration)
                        car_stats['duration_ms'] = duration_ms
                        car_stats['duration'] = self.parse_ms_to_time(duration_ms)
                        car_stats['last_lap_duration'] = lap_duration
                        car_stats['laps'].append(self.parse_date_to_ms(lap_duration))
                else:
                    duration_ms = self.parse_date_to_ms(lap_duration)
                    self.total_driving_time[car_id] = {
                        'duration_ms': duration_ms,
                        'duration': self.parse_ms_to_time(duration_ms),
                        'last_lap_duration': lap_duration,
                        'laps': [self.parse_date_to_ms(lap_duration)]
                    }

        # print(f"Total driving time: {self.total_driving_time}")

    def rank_by_position(self):
        """
            Function sorts cars by position, and assigns/updates top 3 to the self.ranked_drivers variable.
        :return: None
        """
        sorted_data = []
        for car_data in self.app_state["REALTIME_CAR_UPDATE"].values():
            sorted_data.append(
                {
                    "CarIndex": car_data["CarIndex"],
                    "Position": car_data["Position"]
                })
        sorted_data.sort(key=lambda x: int(x["Position"]))
        # print(f"SORTED: {sorted_data}")
        self.ranked_drivers = []
        for position_car in sorted_data[:11]:
        # for position_car in sorted_data[:20]:
            for broadcast_car in self.app_state["BROADCASTING_EVENT"].values():
                # print(f"laptime: {broadcast_car['Msg']}")
                if position_car["CarIndex"] == broadcast_car["CarId"]:
                    # self.put('test', {
                    #     "id": str(datetime.now()),
                    #     "data": broadcast_car['CarData']
                    # })

                    print(broadcast_car['CarData'])
                    drivers = broadcast_car['CarData']['Drivers'][0]
                    driver_name = drivers['FirstName'] + ' ' + drivers['LastName']
                    self.ranked_drivers.append({
                        "driver_name": driver_name,
                        "car_id": position_car["CarIndex"],
                        "position": position_car["Position"],
                        "team_name": broadcast_car["CarData"]["TeamName"],
                        "car_name": broadcast_car["CarData"]['CarModelType']
                    })
                    # print(f"FOUND MATCH for {position_car['CarIndex']} : {driver_name}")
        print(f"Top driver: {self.ranked_drivers}")
        # return sorted_data

    @commands.Cog.listener()
    async def on_ready(self):
        print("acc cog loaded")
        self.acc.start()

    @commands.Cog.listener()
    async def pr(self):
        embed = discord.Embed()
        embed.add_field(name="1", value="a", inline=False)
        embed.add_field(name="2", value="b", inline=False)
        embed.set_footer(text="oh and it kinda works with pcars2 and ams2 but not really")
        await self.bot.get_channel(1052683967427526757).send(embed=embed)

    @tasks.loop(seconds=3)
    async def acc(self):
        global session_over
        global first_overall
        global second_overall
        global third_overall
        global track_name

        x = requests.get('http://136.56.10.210:8792')
        # x = requests.get('http://47.204.162.11:8792')
        if x.status_code == 200:
            data = x.json()
            self.app_state = data
            # print(json.dumps(data, indent=2))

            self.rank_by_position()
            self.update_total_driving_time()

            if "REALTIME_UPDATE" in data.keys():
                if "SessionType" in data['REALTIME_UPDATE'].keys():
                    if data['REALTIME_UPDATE']['SessionType'] == "Race":
                        if data['REALTIME_UPDATE']['Phase'] == "PostSession":
                            if session_over == 0:
                                # await self.bot.get_channel(1050162757204455475).send("race over")

                                image = Image.open(f"./tracks/watkins.png")

                                self.clpos = 0

                                def classification(clpos):
                                    pos = Image.open(f"./assets/position.png")
                                    image.paste(pos, (80, 150 + clpos * 80))
                                    mfc = Image.open(f"./assets/{self.mfc_list[str(self.ranked_drivers[clpos]['car_name'])]}.png")
                                    # mfc = Image.open(f"./assets/porsche.png")
                                    car_name = self.mfc_list[str(self.ranked_drivers[clpos]['car_name'])]
                                    if car_name == "aston":
                                        image.paste(mfc, (680, 170 + clpos * 80), mfc)
                                    elif car_name == "bentley":
                                        image.paste(mfc, (680, 170 + clpos * 80), mfc)
                                    elif car_name == "ferrari":
                                        image.paste(mfc, (689, 155 + clpos * 80), mfc)
                                    elif car_name == "mclaren":
                                        image.paste(mfc, (678, 167 + clpos * 80), mfc)
                                    elif car_name == "audi":
                                        image.paste(mfc, (680, 167 + clpos * 80), mfc)
                                    elif car_name == "lambo":
                                        image.paste(mfc, (683, 155 + clpos * 80), mfc)
                                    elif car_name == "jaguar":
                                        image.paste(mfc, (680, 167 + clpos * 80), mfc)
                                    elif car_name == "lexus":
                                        image.paste(mfc, (680, 161 + clpos * 80), mfc)
                                    elif car_name == "honda":
                                        image.paste(mfc, (680, 159 + clpos * 80), mfc)
                                    else:
                                        image.paste(mfc, (680, 155 + clpos * 80), mfc)
                                    draw = ImageDraw.Draw(image)
                                    font = ImageFont.truetype("f1regular.ttf", 35)
                                    text = str(clpos + 1)
                                    if clpos == 0:
                                        draw.text((96, 162 + clpos * 80), text, (5, 5, 5), font=font)
                                        text = "Car Class"
                                        font = ImageFont.truetype("f1regular.ttf", 45)
                                        draw.text((680, 63), text, (245, 245, 245), font=font)
                                        text = "Time"
                                        font = ImageFont.truetype("f1regular.ttf", 45)
                                        draw.text((1385, 63), text, (245, 245, 245), font=font)
                                        text = "Points"
                                        font = ImageFont.truetype("f1regular.ttf", 45)
                                        draw.text((1685, 63), text, (245, 245, 245), font=font)
                                        text = "Driver"
                                        font = ImageFont.truetype("f1regular.ttf", 45)
                                        draw.text((150, 63), text, (245, 245, 245), font=font)
                                    elif clpos == 9:
                                        draw.text((82, 162 + clpos * 80), text, (5, 5, 5), font=font)
                                    elif clpos == 10:
                                        draw.text((85, 162 + clpos * 80), text, (5, 5, 5), font=font)
                                    else:
                                        draw.text((93.5, 162 + clpos * 80), text, (5, 5, 5), font=font)

                                    font = ImageFont.truetype("f1regular.ttf", 41)
                                    text = f"{self.ranked_drivers[clpos]['driver_name']}"
                                    draw.text((150, 157 + clpos * 80), text, (245, 245, 245), font=font)
                                    text = f"{self.car_list[str(self.ranked_drivers[clpos]['car_name'])]}"
                                    draw.text((730, 157 + clpos * 80), text, (245, 245, 245), font=font)
                                    text = f"{self.total_driving_time[str(self.ranked_drivers[clpos]['car_id'])]['duration'][:-3]}"
                                    draw.text((1385, 157 + clpos * 80), text, (245, 245, 245), anchor="lt", font=font)
                                    text = f"+{self.pnt_list[str(clpos)]}"
                                    draw.text((1805, 157 + clpos * 80), text, (245, 245, 245), anchor="rt", font=font)

                                    points_data = {
                                        "player_name": self.ranked_drivers[clpos]['driver_name'],
                                        "created_at": str(datetime.now()),
                                        "points": self.pnt_list[str(clpos)]
                                    }
                                    self.put('points', points_data)

                                for car in self.ranked_drivers:
                                    classification(self.clpos)
                                    self.clpos += 1

                                bytes = BytesIO()
                                image.save(bytes, format="PNG")
                                bytes.seek(0)
                                dfile = discord.File(bytes, filename="classification.png")
                                await self.bot.get_channel(1052683967427526757).send(file=dfile)
                                session_over = 1
            if "TRACK_DATA" in data.keys():
                if "TrackName" in data['TRACK_DATA'].keys():
                    track_name = data['TRACK_DATA']['TrackName']


def setup(bot):
    bot.add_cog(acc(bot))
