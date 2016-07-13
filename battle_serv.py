from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
import battle


def form(env):
    cl = int(env.get("CONTENT_LENGTH", "0"))
    d = env['wsgi.input'].read(cl)
    d = parse_qs(d)
    battle.squads.append(int(d.get(b'quantity of squads')[0]))
    battle.units.append(int(d.get(b'quantity of units')[0]))
    battle.strategy.append(str(d.get(b'strategy')[0]))


def quantity(env):
    cl = int(env.get("CONTENT_LENGTH", "0"))
    d = env['wsgi.input'].read(cl)
    d = parse_qs(d)
    return d.get(b'quantity of armies', "1")[0]

route = {"quantity": quantity,
         "form": form}


def app(env, resp_start):
    resp_start("200 OK", [("Content-Type", "text/html")])
    path = env.get("PATH_INFO", '')[1:]
    parts = path.split("/")

    with open("form.html", "r") as f:
        if len(parts) > 0 and parts[0] == "form":
            battle.armies_quantity = int(quantity(env))
            result = [(f.read() % (1, 1, 1)).encode("UTF-8")]
        elif len(parts) > 0 and parts[0] == "repeat" and \
                battle.armies_quantity - 1 > battle.i:
            form(env)
            battle.i += 1
            result = [(f.read() % (battle.i + 1, battle.i + 1, battle.i + 1)).encode("UTF-8")]
        elif battle.armies_quantity and battle.i == battle.armies_quantity - 1:
            form(env)
            go = battle.Battlefield(quan_armies=int(battle.armies_quantity),
                                    units=battle.units, squads=battle.squads,
                                    strategy=battle.strategy)
            go.start()
            winner = go.winner
            with open("result.html", "r") as f:
                result = [(f.read() % winner).encode("UTF-8")]
        else:
            with open("index.html", "r") as f:
                result = [(f.read().encode("UTF-8"))]

    return result


if __name__ == "__main__":
    serv = make_server("", 8080, app)
    serv.serve_forever()
