import sys

from ChessBoard import ChessBoard
import cPickle as pickle


class User(object):
    def __init__(self, uid_, hall_):
        self.uid = uid_
        self.game_room = None
        self.hall = hall_
        self.game_status = 0
        self.game_role = -1

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
            self.game_status = 0
            self.game_role = -1
        if room.join_room(self) == GameRoom.ACTION_SUCCESS:
            self.game_room = room
        else:
            return -1

    def join_game(self):
        if self.game_room is None:
            return -1
        if self.game_status == 1:
            return -1
        if self.game_room.join_game(self) == GameRoom.ACTION_SUCCESS:
            self.game_status = 1
            return 0
        else:
            return -1


class ActionResult(object):
    def __init__(self, result_id_=0, result_info_=""):
        self.result_id = result_id_
        self.result_info = result_info_


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
        self.last_status = 0;

    def broadcast_message_to_all(self, message):
        pass

    def send_message(self, to_user_id, message):
        pass

    def get_last_move(self):
        (userrole, move_num, row, col) = self.board.get_lastmove()
        if userrole < 0:
            userrole = -1 * self.get_status() - 1
        last_move = {
            'role': userrole,
            'move_num': move_num,
            'row': row,
            'col': col,
        }
        return last_move

    def get_last_info(self):
        (userrole, move_num, row, col) = self.board.get_lastmove()
        if userrole < 0:
            userrole = -1 * self.get_status() - 1
        last_move = {
            'role': userrole,
            'move_num': move_num,
            'row': row,
            'col': col,
        }
        return last_move

    def action(self, user, action_code, action_args):
        if action_code == "put_piece":
            piece_i = action_args.get_argument('piece_i', None)
            piece_j = action_args.get_argument('piece_j', None)
            if piece_i and piece_j:
                return_code = self.board.put_piece(int(piece_i), int(piece_j), user.game_role)
                if return_code >= 0:
                    return ActionResult(0, "put_piece success:" + str(return_code));
                else:
                    return ActionResult(-4, "put_piece failed, because " + str(return_code))
            else:
                return ActionResult(-3, "Not set the piece_i and piece_j")
        elif action_code == "getlastmove":
            return ActionResult(0, self.get_last_move())
        elif action_code == "get_last_info":
            return ActionResult(0, self.get_last_info())
        elif action_code == "get_room_info":
            return ActionResult(0, pickle.dumps(self))
        elif action_code == "get_game_info":
            return ActionResult(0, pickle.dumps(self.board))
        elif action_code == "get_user_info":
            return ActionResult(0, pickle.dumps(user))
        else:
            return ActionResult(-2, "Not recognized game action")

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
        user.game_role = len(self.play_users)
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

    ROOM_STATUS_FINISH = 4
    ROOM_STATUS_NOONE = 1
    ROOM_STATUS_ONEWAITING = 2
    ROOM_STATUS_PLAYING = 3
    ROOM_STATUS_WRONG = -1

    def get_status(self):
        if self.board.is_over():
            return GameRoom.ROOM_STATUS_FINISH;
        if len(self.play_users) == 0:
            return GameRoom.ROOM_STATUS_NOONE;
        if len(self.play_users) == 1:
            return GameRoom.ROOM_STATUS_ONEWAITING;
        if len(self.play_users) == 2:
            return GameRoom.ROOM_STATUS_PLAYING;
        return GameRoom.ROOM_STATUS_WRONG;

    # def get_room_info(self):
    #     room_info = {'status': 0, 'roomid': -1}
    #     room_info['status'] = self.get_status()
    #     room_info['roomid'] = self.room_id
    #     room_info['room'] = self
    #     room_info['users_uid'] = []
    #     room_info['play_users_uid'] = []
    #     room_info['users'] = []
    #     room_info['play_users'] = []
    #     for user in self.users:
    #         room_info['users_uid'].append(user.uid)
    #         room_info['users'].append(user)
    #     for user in user.game_room.play_users:
    #         room_info['play_users_uid'].append(user.uid)
    #         room_info['play_users'].append(user)


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

            room_info['status'] = user.game_room.get_status()
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

    def get_room_with_user(self, username):
        user = self.get_user_with_uid(username)
        if user.game_room:
            return user.game_room
        return None

    def join_game(self, username):
        user = self.get_user_with_uid(username)
        return user.join_game()

    def game_action(self, username, actionid, arg_pack):
        user = self.get_user_with_uid(username)
        if user.game_room:
            return user.game_room.action(user, actionid, arg_pack)
        else:
            return ActionResult(-1, "Not in any room")

    def logout(self, username):
        user = self.get_user_with_uid(username)
        if user.game_room:
            user.game_room.leave_room(user)
            self.uid2user.pop(username)
