from flask import Flask, request
import vk_api
import random
import json
import os
from difflib import SequenceMatcher

app = Flask(__name__)

# ==========================================
# НАСТРОЙКИ
# ==========================================

TOKEN = "Твой-токен"
CONFIRMATION = "a26c27d2"

PLAYERS_FILE = "players.json"

# ==========================================
# VK
# ==========================================

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

# ==========================================
# ДАННЫЕ
# ==========================================

players = {}
games = {}

# ==========================================
# КОМАНДЫ
# ==========================================

COMMANDS = [
    "привет",
    "помощь",
    "профиль",
    "баланс",
    "игра",
    "магазин",
    "инвентарь",
    "купить удачу",
    "купить сундук",
    "купить vip",
    "открыть сундук"
]


# ==========================================
# ПОИСК ПОХОЖЕЙ КОМАНДЫ
# ==========================================

def find_similar_command(text):

    text = text.lower().strip()

    # Не проверяем фразы из нескольких слов
    if " " in text:
        return None

    best_command = None
    best_ratio = 0

    for command in COMMANDS:

        # Для многословных команд пропускаем
        if " " in command:
            continue

        ratio = SequenceMatcher(
            None,
            text,
            command
        ).ratio()

        if ratio > best_ratio:

            best_ratio = ratio

            best_command = command

    # Минимальное сходство
    if best_ratio >= 0.70:

        return best_command

    return None


# ==========================================
# ЗАГРУЗКА ИГРОКОВ
# ==========================================

def load_players():

    global players

    if not os.path.exists(PLAYERS_FILE):

        players = {}

        return

    try:

        with open(
            PLAYERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            players = json.load(file)

    except (json.JSONDecodeError, OSError):

        players = {}

    changed = False

    for user_id, player in players.items():

        if "level" not in player:
            player["level"] = 1
            changed = True

        if "xp" not in player:
            player["xp"] = 0
            changed = True

        if "coins" not in player:
            player["coins"] = 100
            changed = True

        if "wins" not in player:
            player["wins"] = 0
            changed = True

        if "games" not in player:
            player["games"] = 0
            changed = True

        if "inventory" not in player:

            player["inventory"] = {
                "luck": 0,
                "chest": 0,
                "vip": 0
            }

            changed = True

        else:

            if "luck" not in player["inventory"]:

                player["inventory"]["luck"] = 0

                changed = True

            if "chest" not in player["inventory"]:

                player["inventory"]["chest"] = 0

                changed = True

            if "vip" not in player["inventory"]:

                player["inventory"]["vip"] = 0

                changed = True

    if changed:

        save_players()


# ==========================================
# СОХРАНЕНИЕ
# ==========================================

def save_players():

    with open(
        PLAYERS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            players,
            file,
            ensure_ascii=False,
            indent=4
        )


# ==========================================
# СОЗДАНИЕ ИГРОКА
# ==========================================

def create_player(user_id):

    user_id = str(user_id)

    if user_id not in players:

        players[user_id] = {

            "level": 1,
            "xp": 0,
            "coins": 100,
            "wins": 0,
            "games": 0,

            "inventory": {

                "luck": 0,
                "chest": 0,
                "vip": 0
            }
        }

        save_players()

        return

    player = players[user_id]

    changed = False

    if "level" not in player:

        player["level"] = 1

        changed = True

    if "xp" not in player:

        player["xp"] = 0

        changed = True

    if "coins" not in player:

        player["coins"] = 100

        changed = True

    if "wins" not in player:

        player["wins"] = 0

        changed = True

    if "games" not in player:

        player["games"] = 0

        changed = True

    if "inventory" not in player:

        player["inventory"] = {

            "luck": 0,
            "chest": 0,
            "vip": 0
        }

        changed = True

    else:

        if "luck" not in player["inventory"]:

            player["inventory"]["luck"] = 0

            changed = True

        if "chest" not in player["inventory"]:

            player["inventory"]["chest"] = 0

            changed = True

        if "vip" not in player["inventory"]:

            player["inventory"]["vip"] = 0

            changed = True

    if changed:

        save_players()


# ==========================================
# УРОВНИ
# ==========================================

def check_level_up(user_id):

    user_id = str(user_id)

    player = players[user_id]

    level_up = False

    required_xp = player["level"] * 100

    while player["xp"] >= required_xp:

        player["xp"] -= required_xp

        player["level"] += 1

        level_up = True

        required_xp = player["level"] * 100

    return level_up


# ==========================================
# ЗАГРУЗКА
# ==========================================

load_players()


# ==========================================
# ГЛАВНАЯ
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return "Тусовщик работает!", 200


# ==========================================
# CALLBACK
# ==========================================

@app.route("/", methods=["POST"])
def callback():

    data = request.get_json(silent=True)

    print("VK прислал:", data)

    # ======================================
    # CONFIRMATION
    # ======================================

    if data and data.get("type") == "confirmation":

        return CONFIRMATION, 200, {
            "Content-Type": "text/plain; charset=utf-8"
        }

    # ======================================
    # НОВОЕ СООБЩЕНИЕ
    # ======================================

    if data and data.get("type") == "message_new":

        message = data["object"]["message"]

        text = message.get(
            "text",
            ""
        ).lower().strip()

        peer_id = message["peer_id"]

        user_id = str(
            message["from_id"]
        )

        print(
            "Сообщение:",
            repr(text)
        )

        create_player(user_id)

        player = players[user_id]

        # ==================================
        # ПРИВЕТ
        # ==================================

        if text == "привет":

            vk.messages.send(

                peer_id=peer_id,

                message=(
                    "👋 Привет!\n\n"
                    "Я Тусовщик 🤖\n"
                    "Игры, монеты, уровни и магазин!\n\n"
                    "Напиши «помощь»."
                ),

                random_id=0
            )

        # ==================================
        # ПОМОЩЬ
        # ==================================

        elif text == "помощь":

            vk.messages.send(

                peer_id=peer_id,

                message=(
                    "🎮 ТУСОВЩИК\n\n"

                    "👤 профиль — профиль игрока\n"
                    "💰 баланс — монеты\n"
                    "🎲 игра — сыграть\n\n"

                    "🛒 магазин — магазин\n"
                    "🎒 инвентарь — предметы\n"
                    "🛍 купить сундук\n"
                    "🍀 купить удачу\n"
                    "💎 купить vip\n"
                    "🎁 открыть сундук\n\n"

                    "❓ помощь — список команд"
                ),

                random_id=0
            )

        # ==================================
        # ПРОФИЛЬ
        # ==================================

        elif text == "профиль":

            level = player["level"]

            xp = player["xp"]

            required_xp = level * 100

            remaining_xp = (
                required_xp - xp
            )

            vk.messages.send(

                peer_id=peer_id,

                message=(
                    "👤 ПРОФИЛЬ\n\n"

                    f"⭐ Уровень: {level}\n"
                    f"✨ XP: {xp} / {required_xp}\n"

                    f"📈 До следующего уровня: "
                    f"{remaining_xp} XP\n\n"

                    f"💰 Монеты: "
                    f"{player['coins']}\n\n"

                    f"🎮 Игр сыграно: "
                    f"{player['games']}\n"

                    f"🏆 Побед: "
                    f"{player['wins']}"
                ),

                random_id=0
            )

        # ==================================
        # БАЛАНС
        # ==================================

        elif text == "баланс":

            vk.messages.send(

                peer_id=peer_id,

                message=(
                    "💰 Твой баланс: "
                    f"{player['coins']} монет."
                ),

                random_id=0
            )

        # ==================================
        # МАГАЗИН
        # ==================================

        elif text == "магазин":

            vk.messages.send(

                peer_id=peer_id,

                message=(
                    "🛒 МАГАЗИН\n\n"

                    "🍀 Удача — 100 💰\n"
                    "Удваивает награду "
                    "за следующую победу.\n\n"

                    "🎁 Сундук — 250 💰\n"
                    "Даёт случайную награду.\n\n"

                    "💎 VIP — 500 💰\n"
                    "Предмет коллекции.\n\n"

                    "Чтобы купить:\n"
                    "🍀 купить удачу\n"
                    "🎁 купить сундук\n"
                    "💎 купить vip"
                ),

                random_id=0
            )

        # ==================================
        # ИНВЕНТАРЬ
        # ==================================

        elif text == "инвентарь":

            inventory = player["inventory"]

            vk.messages.send(

                peer_id=peer_id,

                message=(
                    "🎒 ТВОЙ ИНВЕНТАРЬ\n\n"

                    f"🍀 Бустер удачи: "
                    f"{inventory['luck']}\n"

                    f"🎁 Сундук: "
                    f"{inventory['chest']}\n"

                    f"💎 VIP: "
                    f"{inventory['vip']}"
                ),

                random_id=0
            )

        # ==================================
        # КУПИТЬ УДАЧУ
        # ==================================

        elif text == "купить удачу":

            price = 100

            if player["coins"] < price:

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "❌ Недостаточно монет.\n\n"
                        f"💰 Нужно: {price}\n"
                        f"💰 У тебя: "
                        f"{player['coins']}"
                    ),

                    random_id=0
                )

            else:

                player["coins"] -= price

                player["inventory"]["luck"] += 1

                save_players()

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "🍀 Бустер удачи куплен!\n\n"

                        "Он будет использован "
                        "в следующей выигранной игре.\n\n"

                        f"💰 Осталось: "
                        f"{player['coins']} монет"
                    ),

                    random_id=0
                )

        # ==================================
        # КУПИТЬ СУНДУК
        # ==================================

        elif text == "купить сундук":

            price = 250

            if player["coins"] < price:

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "❌ Недостаточно монет.\n\n"
                        f"💰 Нужно: {price}\n"
                        f"💰 У тебя: "
                        f"{player['coins']}"
                    ),

                    random_id=0
                )

            else:

                player["coins"] -= price

                player["inventory"]["chest"] += 1

                save_players()

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "🎁 Сундук куплен!\n\n"

                        "Напиши «открыть сундук».\n\n"

                        f"💰 Осталось: "
                        f"{player['coins']} монет"
                    ),

                    random_id=0
                )

        # ==================================
        # КУПИТЬ VIP
        # ==================================

        elif text == "купить vip":

            price = 500

            if player["coins"] < price:

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "❌ Недостаточно монет.\n\n"
                        f"💰 Нужно: {price}\n"
                        f"💰 У тебя: "
                        f"{player['coins']}"
                    ),

                    random_id=0
                )

            else:

                player["coins"] -= price

                player["inventory"]["vip"] += 1

                save_players()

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "💎 VIP получен!\n\n"

                        "Предмет добавлен "
                        "в инвентарь.\n\n"

                        f"💰 Осталось: "
                        f"{player['coins']} монет"
                    ),

                    random_id=0
                )

        # ==================================
        # ОТКРЫТЬ СУНДУК
        # ==================================

        elif text == "открыть сундук":

            if player["inventory"]["chest"] <= 0:

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "🎁 У тебя нет сундуков.\n\n"
                        "Напиши «магазин»."
                    ),

                    random_id=0
                )

            else:

                player["inventory"]["chest"] -= 1

                reward_type = random.choice([
                    "coins",
                    "coins",
                    "xp"
                ])

                if reward_type == "coins":

                    reward = random.choice([
                        100,
                        150,
                        200,
                        300,
                        500
                    ])

                    player["coins"] += reward

                    save_players()

                    vk.messages.send(

                        peer_id=peer_id,

                        message=(
                            "🎁 СУНДУК ОТКРЫТ!\n\n"

                            f"💰 +{reward} монет!\n\n"

                            f"💰 Баланс: "
                            f"{player['coins']}"
                        ),

                        random_id=0
                    )

                else:

                    reward = random.choice([
                        20,
                        30,
                        50,
                        75
                    ])

                    player["xp"] += reward

                    level_up = check_level_up(
                        user_id
                    )

                    save_players()

                    if level_up:

                        result = (
                            "🎁 СУНДУК ОТКРЫТ!\n\n"
                            f"✨ +{reward} XP!\n\n"
                            "🆙 НОВЫЙ УРОВЕНЬ!\n"
                            f"⭐ Уровень: "
                            f"{player['level']}"
                        )

                    else:

                        result = (
                            "🎁 СУНДУК ОТКРЫТ!\n\n"
                            f"✨ +{reward} XP!"
                        )

                    vk.messages.send(

                        peer_id=peer_id,

                        message=result,

                        random_id=0
                    )

        # ==================================
        # ИГРА
        # ==================================

        elif text == "игра":

            if user_id in games:

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "🎲 Ты уже играешь!\n\n"
                        "Напиши число от 1 до 5."
                    ),

                    random_id=0
                )

            else:

                number = random.randint(
                    1,
                    5
                )

                games[user_id] = number

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "🎲 Я загадал число "
                        "от 1 до 5!\n\n"
                        "Напиши свою догадку."
                    ),

                    random_id=0
                )

                print(
                    "Игра начата!",
                    "Игрок:",
                    user_id,
                    "Число:",
                    number
                )

        # ==================================
        # ОТВЕТ В ИГРЕ
        # ==================================

        elif text in [
            "1",
            "2",
            "3",
            "4",
            "5"
        ]:

            if user_id not in games:

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "🎲 Сейчас нет активной игры.\n\n"
                        "Напиши «игра»."
                    ),

                    random_id=0
                )

            else:

                guess = int(text)

                number = games[user_id]

                player["games"] += 1

                # ==========================
                # ПОБЕДА
                # ==========================

                if guess == number:

                    player["wins"] += 1

                    base_coins = 20
                    base_xp = 10

                    luck_used = False

                    if player["inventory"]["luck"] > 0:

                        player["inventory"]["luck"] -= 1

                        coins_reward = base_coins * 2
                        xp_reward = base_xp * 2

                        luck_used = True

                    else:

                        coins_reward = base_coins
                        xp_reward = base_xp

                    player["coins"] += coins_reward

                    player["xp"] += xp_reward

                    level_up = check_level_up(
                        user_id
                    )

                    save_players()

                    required_xp = (
                        player["level"] * 100
                    )

                    if level_up:

                        result = (

                            "🎉 ПОБЕДА!\n\n"

                            f"🎯 Я загадал: "
                            f"{number}\n\n"

                            f"💰 +{coins_reward} монет\n"
                            f"✨ +{xp_reward} XP\n"
                        )

                        if luck_used:

                            result += (
                                "\n🍀 Бустер удачи "
                                "сработал! Награда x2.\n"
                            )

                        result += (
                            "\n🆙 НОВЫЙ УРОВЕНЬ!\n"
                            f"⭐ Уровень: "
                            f"{player['level']}\n"
                            f"📈 XP: "
                            f"{player['xp']} / "
                            f"{required_xp}"
                        )

                    else:

                        result = (

                            "🎉 УГАДАЛ!\n\n"

                            f"🎯 Я загадал: "
                            f"{number}\n\n"

                            f"💰 +{coins_reward} монет\n"
                            f"✨ +{xp_reward} XP\n"
                        )

                        if luck_used:

                            result += (
                                "\n🍀 Бустер удачи "
                                "сработал! Награда x2.\n"
                            )

                        result += (
                            f"\n⭐ Уровень: "
                            f"{player['level']}\n"
                            f"📈 XP: "
                            f"{player['xp']} / "
                            f"{required_xp}"
                        )

                # ==========================
                # ПРОИГРЫШ
                # ==========================

                else:

                    save_players()

                    result = (

                        "❌ НЕ УГАДАЛ!\n\n"

                        f"🎯 Я загадал: "
                        f"{number}\n\n"

                        "🎲 Попробуешь ещё раз?\n"
                        "Напиши «игра»."
                    )

                del games[user_id]

                vk.messages.send(

                    peer_id=peer_id,

                    message=result,

                    random_id=0
                )

                print(
                    "Результат игры отправлен!"
                )

        # ==================================
        # УМНАЯ ПРОВЕРКА ОПЕЧАТОК
        # ==================================

        elif text != "":

            similar_command = find_similar_command(text)

            if similar_command:

                vk.messages.send(

                    peer_id=peer_id,

                    message=(
                        "🤔 Возможно, ты имел в виду:\n\n"
                        f"👉 {similar_command}\n\n"
                        "Если да — напиши её правильно."
                    ),

                    random_id=0
                )

            # Если сообщение не похоже
            # ни на одну команду — молчим

    return "ok", 200


# ==========================================
# ЗАПУСК
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )