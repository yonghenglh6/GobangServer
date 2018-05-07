import sys

from ChessBoard import ChessBoard


class User(object):
    def __init__(self, uid_, hall_):
        self.uid = uid_
        self.game_room = None
        self.hall = hall_
        self.game_status = 0

    def send_message(self):
        pass

    def receive_message(self, message):
        pass

    def send_game_state(self):
        pass

    def action(self, action):
        pass

    def join_room(self, room):
        if self.game_room is not None:
            self.game_room.leave_room(self)
        if room.join_room(self) == GameRoom.ACTION_SUCCESS:
            self.game_room = room
        else:
            return -1

    def join_game(self):
        if self.game_room is None:
            return
        self.game_room.join_game(self);
        self.game_status = 1

class ActionResult(object):
    def __init__(self,result_id_=0,result_info_=""):
        self.result_id=result_id_
        self.result_info=result_info_

class GameRoom(object):
    ACTION_SUCCESS = 0
    ACTION_FAILURE = -1

    def __init__(self, room_id_):
        self.play_users = []
        self.room_id = room_id_
        self.users = []
        self.max_player_num = 2
        self.max_user_num = 10000
        self.board = ChessBoard()

    def broadcast_message_to_all(self, message):
        pass

    def send_message(self, to_user_id, message):
        pass

    def action(self, user, action_code, action_args):
        if action_code=="set_piece":
            pass

    # def join(self, user):
    #     if self.join_game(user) == GameRoom.ACTION_SUCCESS:
    #         return GameRoom.ACTION_SUCCESS
    #     return self.join_watch(user)

    def join_game(self, user):
        if user not in self.users:
            return GameRoom.ACTION_FAILURE
        if len(self.play_users) >= self.max_player_num:
            return GameRoom.ACTION_FAILURE
        self.play_users.append(user)

        return GameRoom.ACTION_SUCCESS

    def join_room(self, user):
        if len(self.users) >= self.max_user_num:
            return GameRoom.ACTION_FAILURE
        self.users.append(user)
        return GameRoom.ACTION_SUCCESS

    def leave_room(self, user):
        if user in self.play_users:
            self.play_users.remove(user)

        if user in self.users:
            self.users.remove(user)
        else:
            # not in room
            assert False, ""


class Hall(object):
    def __init__(self):
        self.uid2user = {}
        self.id2room = {}
        self.MaxUserNum = 10000
        self.user_num = 0

    def login(self, username, password):
        if self.user_num > self.MaxUserNum:
            return None
        pass

    def login_in_guest(self):
        if self.user_num > self.MaxUserNum:
            return None
        import random
        username = "guest_"
        while True:
            rand_postfix = random.randint(10000, 1000000)
            username = "guest_" + str(rand_postfix)
            if username not in self.uid2user:
                break
        user = User(username, self)
        self.uid2user[username] = user
        return username

    def get_user_with_uid(self, userid):
        if userid not in self.uid2user:
            self.uid2user[userid] = User(userid, self)
        return self.uid2user[userid]

    def join_room(self, username, roomid):
        user = self.get_user_with_uid(username)
        if roomid not in self.id2room:
            self.id2room[roomid] = GameRoom(roomid)
        if user.game_room != self.id2room[roomid]:
            user.join_room(self.id2room[roomid])

    def get_room_info_with_user(self, username):
        room_info = {'status': 0, 'roomid': -1}
        user = self.get_user_with_uid(username)
        if user.game_room:
            room_info['status'] = 1
            room_info['roomid'] = user.game_room.room_id
            room_info['room'] = user.game_room
            room_info['users_uid'] = []
            room_info['play_users_uid'] = []
            room_info['users'] = []
            room_info['play_users'] = []
            for user in user.game_room.users:
                room_info['users_uid'].append(user.uid)
                room_info['users'].append(user)
            for user in user.game_room.play_users:
                room_info['play_users_uid'].append(user.uid)
                room_info['play_users'].append(user)
        return room_info

    def join_game(self, username):
        user = self.get_user_with_uid(username)
        user.join_game()

    def game_action(self, username, actionid, arg_pack):
        user = self.get_user_with_uid(username)
        user.game_room.action(user, actionid, arg_pack)

