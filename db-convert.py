import sqlite3
import json

dblocation = 'C:\\Users\\chris\\AppData\\LocalLow\\Cygames\\umamusume\\master\\master.mdb'


class Card:
    id = 0
    type = 0
    group = False
    rarity = 0
    limit_break = -1
    starting_stats = []  # Speed, Stamina, Power, Guts, Int
    type_stats = 0  # starting stat based non-friend and non-group cards you bring
    type_stats_friend = 0  # like type_stats but got friend and group cards, stats evenly spread out
    stat_bonus = []  # Speed, Stamina, Power, Guts, Int, Skill Points
    race_bonus = 0
    sb = 0  # starting bond
    specialty_rate = 0
    unique_specialty = 1
    tb = 0  # training bonus
    fs_bonus = 0  # fs = friendship
    mb = 0  # motivation bonus
    unique_fs_bonus = 0
    fs_stats = []
    fs_training = 0
    fs_motivation = 0
    fs_trigger = 0
    fs_ramp = [0, 0]
    wisdom_recovery = 0
    effect_size_up = 0
    energy_up = 0
    energy_discount = 0
    fail_rate_down = 0
    hint_rate = 0
    highlander_threshold = 0
    highlander_training = 0
    crowd_bonus = 0
    fan_bonus = 0
    self_hate = [0, 0]  # bond required, training bonus if not on own stat
    fan_training = [0, 0]  # no. of fans for +1% training bonus, training bonus cap
    fail_nullify = 0  # chance of having 0% failure training
    all_bond_training = 0
    facility_training = 0
    char_name = "Unknown"


def get_value(data_tuple, lb, rarity):
    base_value = -1
    base_lb = lb
    index = lb + rarity + 5
    while index >= 2:
        base_value = int(data_tuple[index])
        if base_value == -1:
            index -= 1
            base_lb -= 1
        else:
            break

    if base_lb == lb:
        return base_value
    
    if base_value == -1:
        return 0

    max_value = -1
    max_lb = lb
    index = lb + rarity + 5
    while index <= 12:
        max_value = int(data_tuple[index])
        if max_value == -1:
            index += 1
            max_lb += 1
        else:
            break

    if max_value == -1:
        return base_value

    if base_lb == max_lb:
        return base_value

    return int(base_value + (max_value - base_value) * ((lb - base_lb) / (max_lb - base_lb)))


def add_effect_to_card(this_card, effect_int, effect_value):
    if effect_int == 1:
        this_card.fs_bonus += effect_value / 100
    elif effect_int == 2:
        this_card.mb += effect_value / 100
    elif effect_int == 3:
        this_card.stat_bonus[0] += effect_value
    elif effect_int == 4:
        this_card.stat_bonus[1] += effect_value
    elif effect_int == 5:
        this_card.stat_bonus[2] += effect_value
    elif effect_int == 6:
        this_card.stat_bonus[3] += effect_value
    elif effect_int == 7:
        this_card.stat_bonus[4] += effect_value
    elif effect_int == 8:
        this_card.tb += effect_value / 100
    elif effect_int == 9:
        this_card.starting_stats[0] += effect_value
    elif effect_int == 10:
        this_card.starting_stats[1] += effect_value
    elif effect_int == 11:
        this_card.starting_stats[2] += effect_value
    elif effect_int == 12:
        this_card.starting_stats[3] += effect_value
    elif effect_int == 13:
        this_card.starting_stats[4] += effect_value
    elif effect_int == 14:
        this_card.sb += effect_value
    elif effect_int == 15:
        this_card.race_bonus += effect_value
    elif effect_int == 16:
        this_card.fan_bonus += effect_value / 100
    elif effect_int == 18:
        this_card.hint_rate += effect_value / 100
    elif effect_int == 19:
        this_card.specialty_rate += effect_value
    elif effect_int == 25:
        this_card.energy_up += effect_value / 100
    elif effect_int == 26:
        this_card.effect_size_up += effect_value / 100
    elif effect_int == 27:
        this_card.fail_rate_down += effect_value / 100
    elif effect_int == 28:
        this_card.energy_discount += effect_value / 100
    elif effect_int == 30:
        this_card.stat_bonus[5] += effect_value
    elif effect_int == 31:
        this_card.wisdom_recovery += effect_value
    # The below unique effects are in a different column so they're hardcoded for now
    # elif effect_int == ...
    elif effect_int != 0:
        return -1  # identify new effects


cards = []

types = {
    0: 6,
    101: 0,
    102: 2,
    103: 3,
    105: 1,
    106: 4
}

bonus_dict = {
    1: 'unique_fs_bonus',  # to be used only for unique
    2: 'mb',
    3: 'stat_bonus[0]',
    4: 'stat_bonus[1]',
    5: 'stat_bonus[2]',
    6: 'stat_bonus[3]',
    7: 'stat_bonus[4]',
    30: 'stat_bonus[5]',
    8: 'tb',
    31: 'wisdom_recovery',
}

with sqlite3.connect(dblocation) as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM support_card_data')
    card_data = cursor.fetchall()

    for data in card_data:
        # 0 id | 1 chara_id | 2 rarity | 3 exchange_item_id | 4 effect_table_id | 5 unique_effect_id | 6 command_type
        # 7 command_id | 8 support_card_type | 9 skill_set_id | other stuff
        cursor.execute('SELECT * FROM support_card_effect_table WHERE id=%s' % data[0])
        effects = cursor.fetchall()

        for i in range(5):
            current_card = Card()
            current_card.id = data[0]
            current_card.type = types[int(data[7])]
            current_card.group = int(data[8]) == 3
            current_card.rarity = int(data[2])
            current_card.limit_break = i
            current_card.starting_stats = [0, 0, 0, 0, 0]
            current_card.type_stats = 0
            current_card.type_stats_friend = 0
            current_card.stat_bonus = [0, 0, 0, 0, 0, 0]
            current_card.race_bonus = 0
            current_card.sb = 0
            current_card.specialty_rate = 0
            current_card.unique_specialty = 1
            current_card.tb = 1
            current_card.fs_bonus = 1
            current_card.mb = 1
            current_card.unique_fs_bonus = 1
            current_card.fs_stats = [0, 0, 0, 0, 0, 0]
            current_card.fs_training = 0
            current_card.fs_motivation = 0
            current_card.fs_trigger = 0
            current_card.fs_ramp = [0, 0]
            current_card.wisdom_recovery = 0
            current_card.effect_size_up = 1
            current_card.energy_up = 1
            current_card.energy_discount = 0
            current_card.fail_rate_down = 0
            current_card.hint_rate = 1
            current_card.highlander_threshold = 0
            current_card.highlander_training = 0
            current_card.crowd_bonus = 0
            current_card.fan_bonus = 0
            current_card.self_hate = [0, 0]
            current_card.fan_training = [0, 0]
            current_card.fail_nullify = 0
            current_card.all_bond_training = 0
            current_card.facility_training = 0
            current_card.char_name = ""

            for effect in effects:
                # 0 id | 1 type | 2 init | 3 limit_lv_5 | ... | 12 limit_lv_50
                effect_type = int(effect[1])
                add_effect_to_card(current_card, effect_type, get_value(effect, i, int(data[2])))

            cursor.execute('SELECT * FROM support_card_unique_effect WHERE id = %s' % data[0])
            # 0 id | 1 level unlocked | 2 type_0 | 3 value_0　... | 8 type_1 | 9 value_1
            unique = cursor.fetchone()
            if unique is not None:
                for u in 0, 6:
                    type_0 = unique[2 + u]
                    if type_0 == 1:
                        current_card.unique_fs_bonus += unique[3 + u] / 100
                    elif type_0 == 19:
                        current_card.unique_specialty = 1 + unique[3 + u] / 100
                    elif type_0 == 101:
                        current_card.fs_trigger = unique[3 + u]
                        for k in 0, 2:
                            bonus_type = unique[4 + u + k]
                            bonus_value = unique[5 + u + k]
                            if bonus_type == 2:
                                current_card.fs_motivation += bonus_value / 100
                            elif bonus_type == 3:
                                current_card.fs_stats[0] += bonus_value
                            elif bonus_type == 4:
                                current_card.fs_stats[1] += bonus_value
                            elif bonus_type == 5:
                                current_card.fs_stats[2] += bonus_value
                            elif bonus_type == 6:
                                current_card.fs_stats[3] += bonus_value
                            elif bonus_type == 7:
                                current_card.fs_stats[4] += bonus_value
                            elif bonus_type == 30:
                                current_card.fs_stats[5] += bonus_value
                            elif bonus_type == 8:
                                current_card.fs_training += bonus_value / 100
                            elif bonus_type == 31:
                                current_card.wisdom_recovery += bonus_value
                    elif type_0 == 102:
                        # TODO don't hardcode (delete this fs_training, use self_hate instead)
                        current_card.self_hate = [unique[3 + u], unique[4 + u] / 100]
                        current_card.fs_training += 0.2
                    elif type_0 == 103:
                        current_card.highlander_threshold = unique[3 + u]
                        current_card.highlander_training = unique[4 + u] / 100
                    elif type_0 == 104:
                        # TODO don't hardcode (delete this tb, use fan_training instead)
                        current_card.fan_training = [unique[3 + u], unique[4 + u] / 100]
                        current_card.tb += 0.15
                    elif type_0 == 105:
                        current_card.type_stats = unique[3 + u]
                        current_card.type_stats_friend = unique[4 + u]
                    elif type_0 == 106:
                        if unique[4 + u] == 1:
                            current_card.fs_ramp = [unique[5 + u], unique[5 + u] * unique[3 + u]]
                    elif type_0 == 107:
                        # TODO find out what variables mean (for Bamboo 30094: 1, 10, 30, 15, 5), don't hardcode
                        setattr(current_card, bonus_dict[unique[3 + u]], getattr(current_card, bonus_dict[unique[3 + u]]) + 0.07)
                    elif type_0 == 108:
                        # TODO find out what variables mean (for Pearl 30095: 8, 100, 75, 5, 20), don't hardcode
                        setattr(current_card, bonus_dict[unique[3 + u]], getattr(current_card, bonus_dict[unique[3 + u]]) + 0.12)
                    elif type_0 == 109:
                        # TODO don't hardcode (delete this tb, use all_bond_training instead)
                        if unique[3 + u] == 8:
                            current_card.all_bond_training = unique[4 + u] / 100
                        current_card.tb += 0.15
                    elif type_0 == 110:
                        if unique[3 + u] == 8:
                            current_card.crowd_bonus += unique[4 + u] / 100
                    elif type_0 == 111:
                        # TODO don't hardcode (delete this tb, use facility_training instead)
                        if unique[3 + u] == 8:
                            current_card.facility_training = unique[4 + u] / 100
                        current_card.tb += 0.15
                    elif type_0 == 112:
                        current_card.fail_nullify = unique[3 + u] / 100
                    elif add_effect_to_card(current_card, type_0, unique[3 + u]) == -1:
                        print(unique)  # print new effects
            cards.append(current_card)

            cursor.execute('SELECT * FROM text_data WHERE id = 170 AND [index] = %s' % data[1])
            char_name = cursor.fetchone()
            if char_name is not None:
                current_card.char_name = char_name[3]

card_strings = []
for card in cards:
    card_strings.append(json.dumps(card.__dict__, ensure_ascii=False))

# json_string = 'const cards = [%s];\n\nexport default cards;' % ",".join(card_strings)
json_string = '[%s]' % ",".join(card_strings)  # for converting to a format MS Excel can parse

with open("./src/cards.js", "w", encoding="utf-8") as f:
    f.write(json_string)
