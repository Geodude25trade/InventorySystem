import click
import sqlalchemy.exc
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from shutil import copyfile
from credentials import *
import json
import enum
import os
import sass

sass.compile(dirname=('static/styles/sass', 'static/styles/css'), output_style='compressed')

app = Flask(__name__)
app.secret_key = APP_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Item': Item,
            'Tag': Tag,
            'ItemConditionEnum': ItemConditionEnum
            }


@app.cli.command('initdb')
def initialize_database():
    if not os.path.exists('database.db'):
        with open('database.db', 'w') as file:
            pass
    db.create_all()


@app.cli.command('export-json')
def initialize_database():
    db_items = Item.query.all()
    json_items = [
        {"name": item.name,
         "upc": item.upc,
         "expiration": item.expiration.isoformat() if item.expiration else None,
         "price": item.price,
         "condition": item.condition.value,
         "tags": [tag.name for tag in item.tags]
         } for item in db_items
    ]
    with open("database.json", "w") as file:
        json.dump(json_items, file)


@app.cli.command('import-json')
@click.argument('filename', type=click.Path(exists=True))
def initialize_database(filename):
    if os.path.exists("database.db") and os.stat("database.db") != 0:
        copyfile("database.db", "database.db.BAK")
        db.drop_all()
    db.create_all()
    with open(filename, "r") as file:
        json_items = json.load(file)
    for item in json_items:
        tag_list = []
        for tag_name in item["tags"]:
            tag = Tag.query.filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tag_list.append(tag)
        new_item = Item(name=item["name"],
                        upc=item["upc"],
                        expiration=date.fromisoformat(item["expiration"]) if item["expiration"] else None,
                        price=item["price"],
                        condition=ItemConditionEnum(item["condition"]),
                        tags=tag_list)
        db.session.add(new_item)
    db.session.commit()


class ItemConditionEnum(enum.Enum):
    available = 0
    used = 1
    discarded = 2


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    upc = db.Column(db.String(32))
    expiration = db.Column(db.Date)
    price = db.Column(db.Float(2), default=0)
    condition = db.Column(db.Enum(ItemConditionEnum), nullable=False, server_default="available")
    tags = db.relationship('Tag', backref='items', secondary='item_tags')

    @property
    def expiration_status(self):
        if self.expiration:
            today = date.today()
            days_to_expiration = self.expiration - today
            if days_to_expiration.days <= 0:
                return "expired"
            elif days_to_expiration.days <= 7:
                return "almost-expired"
            elif days_to_expiration.days <= 18:
                return "old"
            else:
                return "fresh"
        else:
            return ""


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


item_tags = db.Table('item_tags',
                     db.Column('item_id', db.Integer(), db.ForeignKey('items.id'), primary_key=True),
                     db.Column('tag_id', db.Integer(), db.ForeignKey('tags.id'), primary_key=True)
                     )


# class NullableDateField(DateField):
#
#     def process_formdata(self, valuelist):
#         if valuelist:
#             date_str = ' '.join(valuelist).strip()
#             if date_str == '':
#                 self.data = None
#                 return
#             try:
#                 self.data = datetime.strptime(date_str, self.format).date()
#             except ValueError:
#                 self.data = None
#                 raise ValueError(self.gettext('Not a valid date value'))
#
#
# class ItemForm(FlaskForm):
#     name = StringField('Name', validators=[InputRequired(), Length(max=150)])
#     upc = StringField('UPC', validators=[InputRequired(), Length(max=32)])
#     expiration = NullableDateField('Expiration Date')
#     tags = FieldList(StringField('tag'), min_entries=1)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/data')
def data_dashboard():
    return render_template("data-view.html",
                           total_spent=f"{total_money_spent():,.2f}",
                           total_wasted=f"{total_money_wasted():,.2f}",
                           items=Item.query.filter(Item.expiration, Item.condition == ItemConditionEnum.available).order_by(Item.expiration).limit(7).all()
                           )


@app.route('/items', methods=["GET"])
def view_items():
    items = Item.query.filter(Item.condition == ItemConditionEnum.available).all()
    return render_template("view-items.html", items=items)


@app.route('/scan_add', methods=["POST", "GET"])
def scan_add():
    if request.method == "GET":
        tags = Tag.query.all()
        return render_template("scan-add.html", tags=tags)
    elif request.method == "POST":
        upc_code = request.get_json().get('upc')
        if upc_code:
            item = Item.query.filter(Item.upc == upc_code).order_by(Item.id.desc()).first()
            if item:
                return {"code": 200, "message": "", "method": "add", "name": item.name, "upc": item.upc,
                        "price": item.price, "tags": [tag.name for tag in item.tags]}
            else:
                return {"code": 200, "message": "", "method": "new"}
        else:
            return {"code": 500, "message": "No code entered", "method": "new"}


@app.route('/scan_remove', methods=["POST", "GET"])
def scan_remove():
    if request.method == "GET":
        return render_template("scan-remove.html")
    elif request.method == "POST":
        req_json = request.get_json()
        upc_code = req_json.get('upc')
        all_items = req_json.get('all_items')

        items = None

        if upc_code:
            items = Item.query.filter(Item.upc == upc_code, Item.condition == ItemConditionEnum.available).all()
        elif all_items:
            items = Item.query.filter(Item.condition == ItemConditionEnum.available).all()

        # Send whatever items where selected
        if items:
            return {"code": 200, "message": "", "items": [
                {
                    "id": item.id, "name": item.name, "upc": item.upc,
                    "expiration": item.expiration.isoformat() if item.expiration else None,
                    "tags": [tag.name for tag in item.tags],
                    "expiration_status": item.expiration_status
                } for item in items
            ]}
        else:
            if all_items:
                return {"code": 500, "message": f"No items in database", "items": []}
            elif upc_code:
                return {"code": 500, "message": f"No item with code {upc_code}", "items": []}
            else:
                return {"code": 500, "message": f"No item with code {upc_code}", "items": []}


@app.route('/add', methods=["POST"])
def add_item():
    params = request.get_json()
    print(params)
    tag_objects = set()
    for tag in params["tags"]:
        if tag != "":
            tag_object = Tag.query.filter(Tag.name == tag).first()
            if not tag_object:
                tag_object = Tag(name=tag)
                db.session.add(tag_object)
            tag_objects.add(tag_object)
    expiration = params["expiration"]
    new_item = Item(name=params["name"],
                    upc=params["upc"],
                    price=params["price"],
                    expiration=date.fromisoformat(expiration) if expiration and expiration != "" else None,
                    tags=list(tag_objects))
    db.session.add(new_item)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as err:
        return {"code": 500, "message": err}
    else:
        return {"code": 200, "message": f"Successfully added {params['name']}"}


@app.route('/remove', methods=["POST"])
def remove_item():
    item_ids = request.get_json().get('item_ids')
    print(item_ids)
    if item_ids:
        for item_id, condition in item_ids.items():
            item = Item.query.filter(Item.id == int(item_id)).first()
            if condition == "use":
                item.condition = ItemConditionEnum.used
            elif condition == "discard":
                item.condition = ItemConditionEnum.discarded
            elif condition == "remove":
                db.session.delete(item)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as err:
            return {"code": 500, "message": err}
        else:
            return {"code": 200, "message": f"Successfully removed items"}
    return {"code": 500, "message": "Incorrect parameter key(s)"}


@app.route('/data', methods=["POST"])
def send_data():
    data_object = request.get_json().get("data_object")
    if data_object:
        data = None
        if data_object in DATA_METHODS:
            data = DATA_METHODS[data_object]()
        return {"code": 200, "message": "", "data": data}
    return {"code": 500, "message": "Incorrect parameter key(s)"}


def tag_count_pie_chart_data():
    all_tags = Tag.query.all()
    data = []
    for tag in all_tags:
        data.append({"name": tag.name, "value": len(tag.items)})
    return sorted(data, key=lambda x: x["value"], reverse=True)


def condition_cost_pie_chart_data():
    available_items = Item.query.filter(Item.condition == ItemConditionEnum.available).all()
    used_items = Item.query.filter(Item.condition == ItemConditionEnum.used).all()
    discarded_items = Item.query.filter(Item.condition == ItemConditionEnum.discarded).all()
    return [{"name": "Available Items", "value": sum([item.price for item in available_items])},
            {"name": "Used Items", "value": sum([item.price for item in used_items])},
            {"name": "Discarded Items", "value": sum([item.price for item in discarded_items])}]


def tag_cost_pie_char_data():
    all_tags = Tag.query.all()
    data = []
    for tag in all_tags:
        value = sum([item.price for item in tag.items])
        if value > 0:
            data.append({"name": tag.name,
                         "value": value})
    return sorted(data, key=lambda x: x["value"], reverse=True)


def tag_average_cost_pie_char_data():
    all_tags = Tag.query.all()
    data = []
    for tag in all_tags:
        value = sum([item.price for item in tag.items if item.price]) / len(tag.items)
        if value > 0:
            data.append({"name": tag.name,
                         "value": value})
    return sorted(data, key=lambda x: x["value"], reverse=True)


def tag_condition_discarded_cost_pie_char_data():
    all_tags = Tag.query.all()
    data = []
    for tag in all_tags:
        value = sum([item.price for item in tag.items if item.condition == ItemConditionEnum.discarded])
        if value > 0:
            data.append({"name": tag.name,
                         "value": value})
    return sorted(data, key=lambda x: x["value"], reverse=True)


def tag_condition_used_cost_pie_char_data():
    all_tags = Tag.query.all()
    data = []
    for tag in all_tags:
        value = sum([item.price for item in tag.items if item.condition == ItemConditionEnum.used])
        if value > 0:
            data.append({"name": tag.name,
                         "value": value})
    return sorted(data, key=lambda x: x["value"], reverse=True)


def tag_condition_available_cost_pie_char_data():
    all_tags = Tag.query.all()
    data = []
    for tag in all_tags:
        value = sum([item.price for item in tag.items if item.condition == ItemConditionEnum.available])
        if value > 0:
            data.append({"name": tag.name,
                         "value": value})
    return sorted(data, key=lambda x: x["value"], reverse=True)


DATA_METHODS = {
    "tag_pie": tag_count_pie_chart_data,
    "condition_pie": condition_cost_pie_chart_data,
    "tag_cost_pie": tag_cost_pie_char_data,
    "tag_average_cost_pie": tag_average_cost_pie_char_data,
    "tag_condition_discarded_cost_pie": tag_condition_discarded_cost_pie_char_data,
    "tag_condition_used_cost_pie": tag_condition_used_cost_pie_char_data,
    "tag_condition_available_cost_pie": tag_condition_available_cost_pie_char_data
}


def total_money_spent():
    all_items = Item.query.all()
    value = sum([item.price for item in all_items])
    return value


def total_money_wasted():
    all_items = Item.query.all()
    value = sum([item.price for item in all_items if item.condition == ItemConditionEnum.discarded])
    return value


if __name__ == '__main__':
    app.run()
