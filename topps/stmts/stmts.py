from MySQLdb import escape_string as e

# This makes sure the value looks like an int to start with.
ei = lambda val: e(str(int(val)))

# A decorator so we don't always have to do `print stmt; return stmt` at the end
def print_and_return(func):
    def pr_wrapper(*arg, **kwargs):
        res = func(*arg, **kwargs)
        print res
        return res
    return pr_wrapper

@print_and_return
def login(email, password):
    return "SELECT * FROM users WHERE email='{0}' AND password=MD5('{1}');".format(e(email), e(password))

@print_and_return
def get_user(user_id):
    return "SELECT * FROM users WHERE id={0} LIMIT 1;".format(ei(user_id))

@print_and_return
def get_other_users(user_id):
    return "SELECT id, full_name FROM users WHERE id != {0}".format(ei(user_id))

@print_and_return
def after_login(user_id, extra_points):
    return "UPDATE users SET points = points + {1} WHERE id = {0};".format(ei(user_id), ei(extra_points))

@print_and_return
def populate_card(player_id):
    return "SELECT * FROM player WHERE id={0} LIMIT 1;".format(ei(player_id))

@print_and_return
def get_notifications_count(user_id):
    return "SELECT COUNT(*) FROM `trade` WHERE (prop_id={0} OR accepter_id={0}) AND last_edited != {0} AND confirmed_at IS NULL;".format(ei(user_id))

@print_and_return
def get_active_trades(user_id):
    return "SELECT *, proposer.id, proposer.full_name FROM trade JOIN users AS proposer ON proposer.id=trade.prop_id \
            LEFT OUTER JOIN users AS accepter ON accepter.id=accepter_id WHERE (prop_id={0} OR accepter_id={0}) AND confirmed_at IS NULL".format(ei(user_id))

@print_and_return
def select_trade(trade_id):
    return "SELECT *, proposer.id, proposer.full_name FROM trade JOIN users AS proposer ON proposer.id=trade.prop_id \
            LEFT OUTER JOIN users AS accepter ON accepter.id=accepter_id WHERE trade_id = {0}".format(ei(trade_id))

@print_and_return
def initiate_trade(user_id_1, user_id_2=None, last_edited=None):
    #oh god.
    if user_id_2:
        if last_edited:
            return "INSERT INTO trade (prop_id, accepter_id, last_edited) VALUES ({0}, {1}, {2})".format(ei(user_id_1), ei(user_id_2), ei(last_edited))
        else:
            return "INSERT INTO trade (prop_id, accepter_id) VALUES ({0}, {1})".format(ei(user_id_1), ei(user_id_2))
    elif last_edited:
        return "INSERT INTO trade (prop_id, last_edited) VALUES ({0}, {1})".format(ei(user_id_1), ei(last_edited))
    else:
        return "INSERT INTO trade (prop_id) VALUES ({0})".format(ei(user_id_1))

@print_and_return
def propose_trade(trade_id, user_id):
    return "UPDATE trade SET accepter_id={1} WHERE trade_id={0};".format(ei(trade_id), ei(user_id))

@print_and_return
def counter_trade(last_edited, trade_id):
    return "UPDATE trade SET last_edited={0} WHERE trade_id={1};".format(ei(last_edited), ei(trade_id))

@print_and_return
def accept_trade(user_id_1, user_id_2):
    return "UPDATE trade SET accepted_at=CURRENT_TIMESTAMP WHERE prop_id={0} AND accepter_id={1}".format(ei(user_id_1), ei(user_id_2))

@print_and_return
def confirm_trade(trade_id):
    return "UPDATE trade SET confirmed_at=CURRENT_TIMESTAMP WHERE trade_id={0}".format(ei(trade_id))

@print_and_return
def cancel_trade(trade_id):
    return "DELETE FROM trade WHERE trade_id={0}".format(ei(trade_id))

@print_and_return
def select_card(card_id):
    return "SELECT * FROM card WHERE card_id = {0}".format(ei(card_id))

@print_and_return
def get_user_cards(user_id):
    return "SELECT * FROM card JOIN player JOIN team JOIN division WHERE team_name=team.name AND team.division=division.name AND card.player_id=player.id AND card.current_owner_id = {0} AND player.image_url IS NOT NULL;".format(ei(user_id))

@print_and_return
def trade_card(card_id, new_owner_id):
    return "UPDATE card SET current_owner_id={1} WHERE card_id={0}".format(ei(card_id), ei(new_owner_id))

@print_and_return
def check_trades(user_id_1, user_id_2):
    return "SELECT * FROM trade WHERE prop_id={0} AND accepter_id={1}".format(ei(user_id_1), ei(user_id_2))

@print_and_return
def insert_trade_cards(trade_id, card_id, from_id, desired):
    raw = "INSERT INTO `trade_cards` (`trade_id` ,`card_id` ,`from_id` ,`desired`) VALUES ({0}, {1}, {2}, {3})"
    return raw.format(ei(trade_id), ei(card_id), ei(from_id), e(desired))

@print_and_return
def select_trade_cards(trade_id):
    return "SELECT DISTINCT * FROM `trade_cards` JOIN card JOIN player WHERE trade_cards.card_id=card.card_id AND player.id=card.player_id AND trade_id={0}".format(ei(trade_id))

@print_and_return
def remove_trade_cards(trade_id, card_id):
    return "DELETE FROM `trade_cards` WHERE trade_id={0} AND card_id={1}".format(ei(trade_id), ei(card_id))

@print_and_return
def insert_pack(pack_name, points):
    return "INSERT INTO packs VALUES (NULL, {0}, {1});".format(e(pack_name), ei(points))

@print_and_return
def insert_pack_player(pack_id, player_id):
    return "INSERT INTO packs_players VALUES ({0}, {1})".format(ei(pack_id), ei(player_id))

@print_and_return
def get_packs():
    return "SELECT * FROM packs;"

@print_and_return
def get_pack(pack_id):
    return """SELECT *
              FROM packs
                   INNER JOIN packs_players ON packs.pack_id = packs_players.pack_id
                   INNER JOIN player ON player.id = packs_players.player_id
              WHERE packs.pack_id = {0};""".format(ei(pack_id))

@print_and_return
def purchase_pack(user_id, pack_id):
    return """INSERT INTO card
                          SELECT NULL, packs_players.player_id, {0}
                          FROM packs
                               INNER JOIN packs_players ON packs.pack_id = packs_players.pack_id
                          WHERE packs.pack_id = {1}
                          AND (SELECT users.points FROM users WHERE users.id = {0}) > packs.points;""".format(ei(user_id), ei(pack_id))

@print_and_return
def deduct_points(user_id, pack_id):
    return """UPDATE users
              SET users.points = users.points - (SELECT packs.points FROM packs WHERE packs.pack_id = {1} LIMIT 1)
              WHERE users.id = {0}
              LIMIT 1;""".format(ei(user_id), ei(pack_id))

@print_and_return
def get_user_points(user_id):
    return "SELECT points FROM users WHERE id={0};".format(ei(user_id))

@print_and_return
def get_pack_points(pack_id):
    return "SELECT points from packs WHERE pack_id={0};".format(ei(pack_id))

@print_and_return
def register_user(email, full_name, password):
    # We give them 10 points to start off with, for the lols
    return """INSERT INTO `users` (`email`, `full_name`, `password`) VALUES ("{0}", "{1}", MD5("{2}"));""".format(e(email), e(full_name), e(password))

@print_and_return
def check_registered(email):
    return """SELECT id FROM users WHERE email="{0}";""".format(e(email))

@print_and_return
def get_users():
    return """SELECT * FROM users;"""

@print_and_return
def get_card():
    return """SELECT * FROM card;"""

@print_and_return
def get_conference():
    return """SELECT * FROM conference;"""

@print_and_return
def get_division():
    return """SELECT * FROM division;"""

@print_and_return
def get_packs_players():
    return """SELECT * FROM packs_players;"""

@print_and_return
def get_player():
    return """SELECT * FROM player;"""

@print_and_return
def get_team():
    return """SELECT * FROM team;"""

@print_and_return
def get_trade():
    return """SELECT * FROM trade;"""

@print_and_return
def get_trade_cards():
     return """SELECT * FROM trade_cards;"""
