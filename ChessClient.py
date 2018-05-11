# -*- coding: utf-8 -*-
import threading

import requests
import cookielib
from bs4 import BeautifulSoup
import json
import time
import cPickle as pickle

import ChessHelper
from ChessBoard import ChessBoard
from Hall import GameRoom
from Hall import User
import random
import os

GAME_URL = 'http://192.168.7.61:11111'


class ChessClient():
    def __init__(self):
        self.session = requests.Session()
        # cook =
        self.session.cookies = cookielib.CookieJar()
        # self.session.cookies = http.cookiejar.LWPCookieJar("cookie")
        agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/5.1.2.3000 Chrome/55.0.2883.75 Safari/537.36'
        self.headers = {
            "Host": "http://192.168.7.61:11111",
            "Origin": "http://192.168.7.61:11111",
            "Referer": "http://192.168.7.61:11111",
            'User-Agent': agent
        }

        self.board = ChessBoard()
        self.last_move = {
            'role': -100,
            'move_num': -1,
            'row': -1,
            'col': -1,
        }

    def send_get(self, url):
        return self.session.get(GAME_URL + url, headers=self.headers)

    def send_post(self, url, data):
        return self.session.post(GAME_URL + url, data, headers=self.headers)

    def login_in_guest(self):
        response = self.send_get('/login?action=login_in_guest')
        soup = BeautifulSoup(response.content, "html.parser")
        username_span = soup.find('span', attrs={'id': 'username'})
        if username_span:
            return username_span.text
        else:
            return None

    def login(self, username, password):
        response = self.send_post('/login?action=login',
                                  data={'username': username, 'password': password})
        soup = BeautifulSoup(response.content, "html.parser")
        username_span = soup.find('span', attrs={'id': 'username'})
        if username_span:
            return username_span.text
        else:
            return None

    def logout(self):
        self.send_get('/login?action=logout')

    def join_room(self, roomid):
        response = self.send_post('/action?action=joinroom',
                                  data={'roomid': roomid})
        action_result = json.loads(response.content)
        return action_result

    def join_game(self):
        response = self.send_get('/action?action=joingame')
        action_result = json.loads(response.content)
        return action_result

    def put_piece(self, row, col):
        response = self.send_get(
            '/action?action=gameaction&actionid=%s&piece_i=%d&piece_j=%d' % ('put_piece', row, col))
        action_result = json.loads(response.content)
        return action_result

    def get_room_info(self):
        response = self.send_get(
            '/action?action=gameaction&actionid=%s' % 'get_room_info')
        action_result = json.loads(response.content)
        room = pickle.loads(str(action_result['info']))
        return room

    def get_game_info(self):
        response = self.send_get(
            '/action?action=gameaction&actionid=%s' % 'get_game_info')
        action_result = json.loads(response.content)
        room = pickle.loads(str(action_result['info']))
        return room

    def get_user_info(self):
        response = self.send_get(
            '/action?action=gameaction&actionid=%s' % 'get_user_info')
        action_result = json.loads(response.content)
        room = pickle.loads(str(action_result['info']))
        return room

    def wait_game_info_changed(self, interval=0.3, max_time=100):
        wait_time = 0
        assert interval > 0, "interval must be positive"
        while True:
            response = self.send_get(
                '/action?action=gameaction&actionid=%s' % ('getlastmove'))
            action_result = json.loads(response.content)
            c_last_move = action_result['info']
            if c_last_move['role'] != self.last_move['role'] or c_last_move['move_num'] != self.last_move['move_num'] or \
                    c_last_move['row'] != self.last_move['row'] or c_last_move['col'] != self.last_move['col']:
                self.last_move = c_last_move
                break
            time.sleep(interval)
            wait_time += interval
            if wait_time > max_time:
                break

        return wait_time

    def get_all_rooms(self):
        response = self.send_get(
            '/action?action=get_all_rooms')
        action_result = json.loads(response.content)
        all_rooms = action_result['info']
        return all_rooms


class GameListener():
    def __init__(self, prefix_stategy_map):
        self.client = ChessClient()
        self.client.login_in_guest()
        self.prefix_stategy_map = prefix_stategy_map

    def listen(self):
        while True:
            all_rooms = self.client.get_all_rooms()
            for room in all_rooms:
                room_name = room[0]
                room_status = room[1]
                for prefix in self.prefix_stategy_map:
                    if room_name.startswith(prefix) and room_status == GameRoom.ROOM_STATUS_ONEWAITING:
                        strg = self.prefix_stategy_map[prefix]()
                        commu = GameCommunicator(room_name, strg)
                        commu.start()
                        break
            time.sleep(4)


class GameStrategy():
    def __init__(self):
        import gobang
        self.searcher = gobang.searcher()

    def play_one_piece(self, user, gameboard):
        # user = User()
        # gameboard = ChessBoard()
        turn = user.game_role
        self.searcher.board = [[gameboard.get_piece(m, n) for n in xrange(gameboard.SIZE)] for m in
                               xrange(gameboard.SIZE)]
        # gameboard=ChessBoard()
        # gameboard.move_history
        score, row, col = self.searcher.search(turn, 2)
        print "score:", score
        return (row, col)


class GameStrategy_yixin():

    def __init__(self):
        self.muid = str(random.randint(0, 1000000))
        self.comm_folder = 'yixin_comm/'
        if not os.path.exists(self.comm_folder):
            os.makedirs(self.comm_folder)
        self.chess_state_file = self.comm_folder + 'game_state_' + self.muid
        self.action_file = self.comm_folder + 'action_' + self.muid

    def play_one_piece(self, user, gameboard):
        # user = User()
        # gameboard = ChessBoard()
        with open(self.chess_state_file, 'w') as chess_state_file:
            for userrole, move_num, row, col in gameboard.move_history:
                chess_state_file.write('%d,%d\n' % (row, col))
        if os.path.exists(self.action_file):
            os.remove(self.action_file)
        os.system("yixin.exe %s %s" % (self.chess_state_file, self.action_file))
        row, col = random.randint(0, 15), random.randint(0, 15)
        with open(self.action_file) as action_file:
            line = action_file.readline()
            row, col = line.strip().split(',')

        return (row, col)


class GameStrategy_random():
    def __init__(self):
        self._chess_helper_move_set = []
        for i in range(15):
            for j in range(15):
                self._chess_helper_move_set.append((i, j))
        random.shuffle(self._chess_helper_move_set)
        self.try_step = 0

    def play_one_piece(self, user, gameboard):
        move = self._chess_helper_move_set[self.try_step]
        while gameboard.get_piece(move[0], move[1]) != 0 and self.try_step < 15 * 15:
            self.try_step += 1
            move = self._chess_helper_move_set[self.try_step]
        self.try_step += 1
        return move


class GameCommunicator(threading.Thread):
    def __init__(self, roomid, stragegy):
        threading.Thread.__init__(self)
        self.room_id = roomid
        self.stragegy = stragegy;

    def run(self):
        client = ChessClient()
        client.login_in_guest()
        client.join_room(self.room_id)
        client.join_game()
        while True:
            wait_time = client.wait_game_info_changed()
            room = client.get_room_info()
            # room=GameRoom()
            user = client.get_user_info()
            # user=User()
            gameboard = client.get_game_info()
            # gameboard = ChessBoard()
            if room.get_status() == 1:
                continue
            elif room.get_status() == 2:
                if gameboard.get_current_user() == user.game_role:
                    one_piece = self.stragegy.play_one_piece(user, gameboard)
                    action_result = client.put_piece(*one_piece)
                    if action_result['id'] != 0:
                        print ChessHelper.numToAlp(one_legal_piece[0]), ChessHelper.numToAlp(one_legal_piece[1])
                        print action_result['info']
                        break
                continue
            elif room.get_status() == 3:
                if gameboard.get_current_user() == user.game_role:
                    one_legal_piece = self.stragegy.play_one_piece(user, gameboard)
                    action_result = client.put_piece(*one_legal_piece)
                    if action_result['id'] != 0:
                        print ChessHelper.numToAlp(one_legal_piece[0]), ChessHelper.numToAlp(one_legal_piece[1])
                        print action_result['info']
                        break
                continue
            elif room.get_status() == 4:
                break


def go_play():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--room_name', type=str, default='default')
    parser.add_argument('--server_url', default='http://192.168.7.61:11111')
    parser.add_argument('--ai', default='random')
    args = parser.parse_args()
    global GAME_URL
    GAME_URL = args.server_url
    if args.ai == 'random':
        strategy = GameStrategy_random()
    elif args.ai == 'normal':
        strategy = GameStrategy()
    elif args.ai == 'yixin':
        strategy = GameStrategy_yixin()
    else:
        assert False, "Not recog ai."
    client = ChessClient()
    client.login_in_guest()
    client.join_room(args.room_name)
    client.join_game()
    user = client.get_user_info()
    print "加入游戏成功，你是:" + ("黑方" if user.game_role == 1 else "白方")
    while True:
        wait_time = client.wait_game_info_changed()
        print 'wait_time:', wait_time

        room = client.get_room_info()
        # room=GameRoom()
        user = client.get_user_info()
        # user=User()
        gameboard = client.get_game_info()
        # gameboard = ChessBoard()

        print 'room.get_status():', room.get_status()
        print 'user.game_status():', user.game_status
        print 'gameboard.game_status():'
        ChessHelper.printBoard(gameboard)

        if room.get_status() == 1:
            print "等待另一个对手加入游戏:"
            continue
        elif room.get_status() == 2:
            print "选手已经满了，开始游戏："
            if gameboard.get_current_user() == user.game_role:
                print "轮到你走："
                one_legal_piece = strategy.play_one_piece(user, gameboard)
                action_result = client.put_piece(*one_legal_piece)
                if action_result['id'] != 0:
                    print "走棋失败:"
                    print action_result['info']
            else:
                print "轮到对手走...."
            continue
        elif room.get_status() == 3:
            if gameboard.get_current_user() == user.game_role:
                print "轮到你走："
                one_legal_piece = strategy.play_one_piece(user, gameboard)
                action_result = client.put_piece(*one_legal_piece)
                if action_result['id'] != 0:
                    print "走棋失败:"
                    print ChessHelper.numToAlp(one_legal_piece[0]), ChessHelper.numToAlp(one_legal_piece[1])
                    print action_result['info']

            else:
                print "轮到对手走...."
            continue
        elif room.get_status() == 4:
            print "游戏已经结束了," + ("黑方" if gameboard.get_winner() == 1 else "白方") + " 赢了"
            break


def go_listen():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_url', default='http://192.168.7.61:11111')
    args = parser.parse_args()
    global GAME_URL
    GAME_URL = args.server_url

    prefix_stategy_map = {'ai_': lambda: GameStrategy(), 'yixin_': lambda: GameStrategy_yixin(),
                          'random_': lambda: GameStrategy_random()}
    listen = GameListener(prefix_stategy_map)
    listen.listen()


if __name__ == "__main__":
    # go_play()
    go_listen()
