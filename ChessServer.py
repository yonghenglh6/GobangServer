import tornado.ioloop
import tornado.web
import os

from Hall import Hall

hall = Hall()


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


class ChessHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        info_ = ""
        room_info = hall.get_room_info_with_user(self.current_user)
        self.render("page/chessboard.html", username=self.current_user, roominfo=room_info, info=info_)

    @tornado.web.authenticated
    def post(self):
        action = self.get_argument("action", None)
        info_ = ""
        if action:
            if action == "joinroom":
                roomid = self.get_argument("roomid", None)
                if roomid:
                    hall.join_room(self.current_user, roomid)
                else:
                    info_ = "Not legal roomid."
            elif action == "joingame":
                hall.join_game(self.current_user)

            elif action == "gameaction":
                actionid = self.get_argument("actionid", None)
                hall.game_action(self.current_user,actionid, self)

        room_info = hall.get_room_info_with_user(self.current_user)
        chess_board = None
        import ChessHelper
        if room_info['status'] == 1:
            ChessHelper.playRandomGame(room_info['room'].board)
            chess_board = ChessHelper.printBoard2Str(room_info['room'].board)

        # print room_info
        self.render("page/chessboard.html", username=self.current_user, roominfo=room_info, info=info_,
                    chess_board=chess_board)


class LoginHandler(BaseHandler):
    def get(self):
        self.render('page/login.html')

    def post(self):
        action = self.get_argument("action", None)
        if action == "login":
            username = self.get_argument("username")
            password = self.get_argument("password")
            username = hall.login(username, password)
            if username:
                self.set_secure_cookie("username", username)
                self.redirect("/")
            else:
                self.redirect("/login?status=wrong_password_or_name")
        elif action == "login_in_guest":
            username = hall.login_in_guest()
            print username
            if username:
                self.set_secure_cookie("username", username)
                self.redirect("/")
        else:
            self.render('page/login.html')


class LogoutHandler(BaseHandler):
    def get(self):
        if self.get_argument("logout", None):
            self.clear_cookie("username")
            self.redirect("/")


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
    ], **settings)
    app.listen(11111)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
