import peeweedbevolve  # new; must be imported before models
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Store, Warehouse  # new line
import os
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')


@app.before_request  # new line
def before_request():
    db.connect()


@app.after_request  # new line
def after_request(response):
    db.close()
    return response


@app.cli.command()  # new
def migrate():  # new
    db.evolve(ignore_tables={'base_model'})  # new


@app.route('/')
def index():
    return render_template('index.html')


####CHALLENGE####

#1. Create a new page /store#

@app.route('/store')  # changes the url to http://localhost:5000/store
def addstore():
    store_name = request.args.get('store_name')
    return render_template('store.html', store_name=store_name)


# when using POST should request from exactly where you're getting info from i.e. from the form itself, rather than the args
@app.route('/post_store', methods=['POST'])
def create():
    store_name = request.form.get('store_name')
    store = Store(name=store_name)

    if store.save():  # save method returns either 0 or 1
        flash(f"Saved Store: {store_name}")
        return redirect(url_for('addstore'))
    else:
        flash('Name is already taken, pick another')
        return render_template('store.html', errors=store.errors)

####CHALLENGE####

# Create a form that allows users to create a warehouse & is connected to a store#

#   WAREHOUSE PAGE #


@app.route('/warehouse/new')
def warehouse_new():
    return render_template('warehouse.html', stores=Store.select())


@app.route('/warehouse', methods=['POST'])
def warehouse_create():
    warehouse_location = request.form.get('warehouse_location')
    store_id = request.form.get('store_id')
    warehouse = Warehouse(location=warehouse_location, store=store_id)

    if warehouse.save():
        flash(f"Added Warehouse: {warehouse_location}")
        return redirect(url_for('warehouse_new'))
        #redirect back to the GET app.route('warehouse/new/) to re-render the whole form again#
    else:
        flash('Store already has a warehouse')
        return render_template('warehouse.html', stores=Store.select())


####CHALLENGE####

#Index and Show Pages #

#Page listing all the stores#

@app.route('/stores')
def stores():
    return render_template('liststores.html', stores=Store.select(), warehouse=Warehouse.select())


@app.route('/store/<id>')
def store_id(id):
    return render_template('storespage.html', store=Store.get_by_id(id))

####CHALLENGE####

# implement both edit_store() and update_store() view functions to allow users to modify information about a store using a form


@app.route('/store/<id>/edit')
def edit_store(id):
    return render_template('storespage.html', store=Store.get_by_id(id))


@app.route('/store/<id>', methods=['POST'])
def update(id):
    store = Store.get_by_id(id)
    new_name = request.form.get('newname')
    store.name = new_name
    if not store.save():
        flash('Unable to update store!')
        return render_template('storespage.html', store=store)

    flash(f'Successfully updated store name to {new_name}')
    return redirect(url_for('edit_store', id=store.id))

####CHALLENGE####

#Challenge: Delete


@app.route('/stores/<id>/delete', methods=['POST'])
def delete(id):
    store = Store.get_by_id(id)
    if store.delete_instance(recursive=True):
        flash(f'{store.name} is deleted')

    return redirect(url_for('stores'))


if __name__ == '__main__':
    app.run()
