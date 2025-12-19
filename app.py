from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db, Item

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

BUFF_TYPES = [
    "support_style", "sword_style", "fighting_style", "gun_style",
    "devil_fruit", "suit", "title", "race", "armament_haki", "conqueror_haki",
    "blacksmith", "giant_blacksmith"
]

ACCESSORY_TYPES = ["hat", "top", "arm", "back", "waist", "bottom"]

# ===== Helper functions =====

def get_active_buffs_by_type(items):
    final = {"fruit": 1.0, "sword": 1.0, "gun": 1.0, "strength": 1.0}
    seen_types = set()
    for item in items:
        if item.category != "buff":
            continue
        if item.type in seen_types:
            continue
        seen_types.add(item.type)
        vals = item.values_dict()
        for stat in final:
            final[stat] *= vals.get(stat, 1.0)
    return final

def get_accessory_totals(items):
    totals = {
        "strength":0, "stamina":0, "defense":0,
        "sword":0, "gun":0, "haki":0, "fruit":0
    }
    for item in items:
        if item.category != "accessory":
            continue
        vals = item.values_dict()
        for stat in totals:
            totals[stat] += vals.get(stat, 0)
    return totals

# ===== Routes =====

@app.route("/kingcode99")
def index():
    edit_id = request.args.get("edit", type=int)
    item_to_edit = Item.query.get(edit_id) if edit_id else None
    items = Item.query.all()
    return render_template(
        "index.html",
        items=items,
        buff_types=BUFF_TYPES,
        accessory_types=ACCESSORY_TYPES,
        final_buffs=get_active_buffs_by_type(items),
        accessory_totals=get_accessory_totals(items),
        item_to_edit=item_to_edit,
        edit_index=edit_id
    )

@app.route("/add-buff", methods=["POST"])
def add_buff():
    index = request.form.get("index", type=int)
    is_separate = request.form.get("separate") == "1"

    if is_separate:
        values = {
            "fruit": float(request.form.get("fruit", 1.0)),
            "sword": float(request.form.get("sword", 1.0)),
            "gun": float(request.form.get("gun", 1.0)),
            "strength": float(request.form.get("strength", 1.0)),
        }
    else:
        val = float(request.form.get("all_value", 1.0))
        values = {"fruit": val, "sword": val, "gun": val, "strength": val}

    try:
        if index is not None:
            item = Item.query.get(index)
            if not item:
                return redirect(url_for("index"))

            item.name = request.form["name"]
            item.type = request.form["type"]
            item.strength = values["strength"]
            item.sword = values["sword"]
            item.gun = values["gun"]
            item.fruit = values["fruit"]

        else:
            item = Item(
                category="buff",
                name=request.form["name"],
                type=request.form["type"],
                strength=values["strength"],
                sword=values["sword"],
                gun=values["gun"],
                fruit=values["fruit"]
            )
            db.session.add(item)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("BUFF SAVE ERROR:", e)

    return redirect(url_for("index"))

@app.route("/add-accessory", methods=["POST"])
def add_accessory():
    index = request.form.get("index", type=int)
    values = {
        stat: float(request.form.get(stat, 0))
        for stat in ["strength","stamina","defense","sword","gun","haki","fruit"]
    }

    try:
        if index is not None:
            item = Item.query.get(index)
            if not item:
                return redirect(url_for("index"))

            item.name = request.form["name"]
            item.type = request.form["type"]
            for stat, val in values.items():
                setattr(item, stat, val)

        else:
            item = Item(
                category="accessory",
                name=request.form["name"],
                type=request.form["type"],
                **values
            )
            db.session.add(item)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("ACCESSORY SAVE ERROR:", e)

    return redirect(url_for("index"))

@app.route("/delete/<int:index>")
def delete(index):
    item = Item.query.get(index)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/", methods=["GET","POST"])
def build():
    items = Item.query.all()
    selected = {}
    best_stat = request.form.get("best")

    # Auto-select best
    if best_stat:
        for buff_type in BUFF_TYPES:
            candidates = [i for i in items if i.category=="buff" and i.type==buff_type]
            if candidates:
                best_item = max(candidates, key=lambda x: getattr(x, best_stat, 1.0))
                selected[buff_type] = best_item.name
        for slot in ACCESSORY_TYPES:
            candidates = [i for i in items if i.category=="accessory" and i.type==slot]
            if candidates:
                best_item = max(candidates, key=lambda x: getattr(x, best_stat, 0))
                selected[slot] = best_item.name
    else:
        for buff_type in BUFF_TYPES:
            selected[buff_type] = request.form.get(buff_type)
        for slot in ACCESSORY_TYPES:
            selected[slot] = request.form.get(slot)

    # Compute buffs and accessory totals
    buff_values = {"fruit":1.0,"sword":1.0,"gun":1.0,"strength":1.0}
    accessory_values = {"strength":0,"stamina":0,"defense":0,"sword":0,"gun":0,"haki":0,"fruit":0}

    for item in items:
        if item.category=="buff" and selected.get(item.type)==item.name:
            for stat in buff_values:
                buff_values[stat] *= getattr(item, stat, 1.0)
        if item.category=="accessory" and selected.get(item.type)==item.name:
            for stat in accessory_values:
                accessory_values[stat] += getattr(item, stat, 0)

    main_buffs = ['support_style','fighting_style','gun_style','sword_style','devil_fruit','suit']
    other_buffs = [b for b in BUFF_TYPES if b not in main_buffs]
    first_group = ['hat','top','arm']
    second_group = ['back','waist','bottom']

    return render_template(
        "build.html",
        items=items,
        selected=selected,
        buff_values=buff_values,
        accessory_values=accessory_values,
        main_buffs=main_buffs,
        other_buffs=other_buffs,
        first_group=first_group,
        second_group=second_group
    )

# ===== Run =====
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8000)
