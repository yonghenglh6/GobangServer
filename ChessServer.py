import tornado.ioloop
import tornado.web
import os

from ChessClient import GameStrategy, GameCommunicator
from Hall import Hall
from Hall import GameRoom
from Hall import User

hall = Hall()


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


class ChessHandler(BaseHandler):

    def get_post(self):
        info_ = ""
        user = hall.get_user_with_uid(self.current_user)
        room_info = hall.get_room_info_with_user(self.current_user)
        chess_board = None
        last_move = None
        room_status = 0
        import ChessHelper
        if room_info['status'] > 0:
            # ChessHelper.playRandomGame(room_info['room'].board)\
            room = room_info['room']
            chess_board = room.board
            last_move = room.get_last_move()
            # chess_board = ChessHelper.printBoard2Str(room_info['room'].board)

        # print room_info
        self.render("page/chessboard.html", username=self.current_user, roominfo=room_info, info=info_,
                    chess_board=chess_board, user=user, last_move=last_move)

    @tornado.web.authenticated
    def get(self):
        self.get_post()

    @tornado.web.authenticated
    def post(self):
        self.get_post()


class ActionHandler(BaseHandler):

    def get_post(self):
        action = self.get_argument("action", None)
        action_result = {"id": -1, "info": "Failure"}

        if action:
            if action == "joinroom":
                roomid = self.get_argument("roomid", None)
                if roomid:
                    hall.join_room(self.current_user, roomid)
                    action_result["id"] = 0
                    action_result["info"] = "Join room success."
                else:
                    action_result["id"] = -1
                    action_result["info"] = "Not legal room id."

            elif action == "joingame":
                if hall.join_game(self.current_user) == 0:
                    action_result["id"] = 0
                    action_result["info"] = "Join game success."
                    # room = hall.get_user_with_uid(self.current_user).game_room
                    # if str(room.room_id).startswith('ai_') and room.get_status() == GameRoom.ROOM_STATUS_WAITJOIN:
                    #     strg = GameStrategy()
                    #     commu = GameCommunicator(room.room_id, strg)
                    #     commu.start()

                else:
                    action_result["id"] = -1
                    action_result["info"] = "Join game failed, join a room first or have joined game or game is full."

            elif action == "gameaction":
                actionid = self.get_argument("actionid", None)
                game_action_result = hall.game_action(self.current_user, actionid, self)
                if game_action_result.result_id == 0:
                    action_result["id"] = 0
                    action_result["info"] = game_action_result.result_info
                else:
                    action_result["id"] = -1
                    action_result["info"] = "Game action failed:" + str(
                        game_action_result.result_id) + "," + game_action_result.result_info
            elif action == "getboardinfo":
                room = hall.get_room_with_user(self.current_user)
                # room=GameRoom()
                if room:
                    action_result["id"] = 0
                    action_result["info"] = room.board.dumps()
                else:
                    action_result["id"] = -1
                    action_result["info"] = "Not in room, please join one."
            elif action == "get_all_rooms":
                action_result["id"] = 0
                action_result["info"]=[[room_name,hall.id2room[room_name].get_status()] for room_name in hall.id2room]
            else:
                action_result["id"] = -1
                action_result["info"] = "Not recognition action" + action
        else:
            action_result["info"] = "Not action arg set"

        # self.write(tornado.escape.json_encode(action_result))
        self.finish(action_result)

    @tornado.web.authenticated
    def get(self):
        self.get_post()

    @tornado.web.authenticated
    def post(self):
        self.get_post()


class LoginHandler(BaseHandler):

    def get_post(self):

        action = self.get_argument("action", None)

        if action == "login":
            if self.current_user is not None:
                self.clear_cookie("username")
                hall.logout(self.current_user)

            username = self.get_argument("username")
            password = self.get_argument("password")
            username = hall.login(username, password)
            if username:
                self.set_secure_cookie("username", username)
                self.redirect("/")
            else:
                self.redirect("/login?status=wrong_password_or_name")
        elif action == "login_in_guest":
            if self.current_user is not None:
                self.clear_cookie("username")
                hall.logout(self.current_user)

            username = hall.login_in_guest()
            print username
            if username:
                self.set_secure_cookie("username", username)
                self.redirect("/")
        elif action == "logout":
            if self.current_user is not None:
                self.clear_cookie("username")
                hall.logout(self.current_user)
            self.redirect("/login")
        else:
            self.render('page/login.html')

    def get(self):
        self.get_post()

    def post(self):
        self.get_post()



def main():
    settings = {
        # "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        # "xsrf_cookies": True,
        "login_url": "/login",
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }
    app = tornado.web.Application([
        (r"/", ChessHandler),
        (r"/login", LoginHandler),
        (r"/action", ActionHandler),
    ], **settings)
    app.listen(11111)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
