from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FieldList
from datetime import datetime
from wtforms.validators import InputRequired, Length
from credentials import *


class NullableDateField(DateField):

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist).strip()
            if date_str == '':
                self.data = None
                return
            try:
                self.data = datetime.strptime(date_str, self.format).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))


class ItemForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=150)])
    upc = StringField('UPC', validators=[InputRequired(), Length(max=16)])
    expiration_date = NullableDateField('Expiration Date')
    categories = FieldList(StringField('category'), min_entries=1)


app = Flask(__name__)
app.secret_key = APP_SECRET


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/add', methods=["POST", "GET"])
def add_item():
    form = ItemForm()
    if request.method == "GET":
        return render_template("add_item.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            print(form.data)
            flash(f"Successfully added {form.name.data} to the system")
            return redirect(url_for('add_item'))


if __name__ == '__main__':
    app.run()
