import mysql.connector
from flask import Flask, jsonify, request, render_template
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
 
import base64
from io import StringIO
import PIL.Image
import razorpay


client = razorpay.Client(auth=("rzp_test_JGsIexMIOVh3bW", "kpvTVMIBppTJGlKtMmnzwcVd"))

DATA = {
    "amount": 100,
    "currency": "INR",
    "receipt": "receipt#1",
    "notes": {
        "key1": "value3",
        "key2": "value2"
    }
}
print(client.order.create(data=DATA))

app = Flask(__name__)
# Creating connection object
conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "pass@123",
    database = "tiffin_service"
)

# Page routes 
# *********************************************#
@app.route('/')
def indexPage():
    if conn:
        return render_template('index.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/about')
def aboutPage():
    if conn:
        return render_template('about.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/checkout')
def checkoutPage():
    if conn:
        return render_template('checkout.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/contact')
def contactPage():
    if conn:
        return render_template('contact.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/gallery')
def galleryPage():
    if conn:
        return render_template('gallery.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/ordernow')
def ordernowPage():
    if conn:
        return render_template('ordernow.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/reservation')
def reservationPage():
    if conn:
        return render_template('reservation.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/shopping_cart')
def shopping_cartPage():
    if conn:
        return render_template('shopping-cart.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/sign_in')
def sign_inPage():
    if conn:
        return render_template('sign_in.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/snacks')
def snacksPage():
    if conn:
        return render_template('snacks.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/snacks/<string:RestaurantID>')
def snacksPageDynamic(RestaurantID):
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM SNACKS")
        myresult = mycursor.fetchall()
        print(myresult)
        l = []
        return render_template('snacks.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/admin_home')
def admin_homePage():
    if conn:
        return render_template('admin_home.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/admin_users')
def admin_usersPage():
    if conn:
        return render_template('admin_users.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/admin_kitchens')
def admin_kitchensPage():
    if conn:
        return render_template('admin_kitchens.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/admin_delivery_partners')
def admin_delivery_partnersPage():
    if conn:
        return render_template('admin_delivery_partner.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

# *********************************************#
# APIs routes
# *********************************************#
@app.route('/CheckServer')
def CheckServer():
    if conn:
        return jsonify(StatusCode = '1', Message="Connected!")
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/getUsers',methods = ['GET'])
def getUsers():
  if request.method == 'GET':
     if conn:
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM USERS")
        myresult = mycursor.fetchall()
        print(myresult)
        Users = myresult
        return jsonify(Users = Users)
     

# @app.route('/getSnacks',methods = ['GET'])
def getSnacks(image_name, image_data):
    try:
        image = Image.open(BytesIO(image_data))
        plt.savefig('./static/images/' + image_name+'.jpg')
    except Exception as e:
        print('Error: '+ str(e))

@app.route('/UsersAuthentication',methods = ['POST'])
def UsersAuthentication():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
    try:
        if conn:
            mycursor = conn.cursor()
            User_Email = req["USER_EMAIL"]
            User_Password = req["USER_PASSWORD"]
            mycursor.execute('SELECT * FROM USERS WHERE USER_EMAIL="'+User_Email+'"')
            myresult = mycursor.fetchall()
            print(myresult)
            if len(myresult) == 0:
                return jsonify(StatusCode = '0',ErrorMessage='Invalid User email')
            if (req['USER_EMAIL'] == myresult[0][4] and req['USER_PASSWORD'] == myresult[0][2]): 
                user_record = {
                    "USER_ID" : myresult[0][0],
                    "USER_NAME" : myresult[0][1],
                    "USER_PASSWORD" : myresult[0][2],
                    "USER_TYPE" : myresult[0][3],
                    "USER_EMAIL" : myresult[0][4],
                    "USER_ADDRESS" : myresult[0][5] ,
                    "USER_MOBILE" : myresult[0][6],
                    "VEG_NONVEG_PERF" : myresult[0][7],
                    "Subscription_ID" : myresult[0][8],
                }
                return jsonify(StatusCode = '1', UserRecord=user_record)
            else:
                return jsonify(StatusCode = '2',ErrorMessage='Wrong Credentials')
    except Exception as e:
        return str(e)

@app.route('/getKitchens',methods = ['GET'])
def getKitchens():
    if request.method == 'GET':
        try:
            if conn:
                mycursor = conn.cursor()
                mycursor.execute('select * from Kitchen;')
                myresult = mycursor.fetchall()
                print(myresult)
                KitchensList = []
                RecordCount = len(myresult)
                for i in range(len(myresult)):
                    KitchenRecord = {
                        "Kitchen_ID" : myresult[i][0],
                        "Kitchen_Name" : myresult[i][1],
                        "Kitchen_Type" : myresult[i][2],
                        "Kitchen_open_time" : myresult[i][3],
                        "Kitchen_Close_time": myresult[i][4],
                        "Kitchen_Address" : myresult[i][5],
                        "Kitchen_Ratings" : myresult[i][6],
                        "Kitchen_Number" : myresult[i][7],
                        "Popularity" : myresult[i][8],
                        "Meal_ID" : myresult[i][9],
                    }
                    KitchensList.append(KitchenRecord)
                
                return jsonify(StatusCode = '1', Total = RecordCount,  get_kitchens=KitchensList)
        except Exception as e:
            return str(e)

@app.route('/showMyLunchBoxOrders',methods = ['POST'])
def showMyLunchBoxOrders():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        try:
            if conn:
                mycursor = conn.cursor()
                mycursor.execute("select Lunch_Box_Order.Lunch_Box_Order_ID, Lunch_Box_Order.Lunch_Box_Type, Lunch_Box_Order.Lunch_Box_Size, Lunch_Box_Order.Lunch_Box_color_pref, Payment.Payment_type, Payment.Payment_Amt, Payment.Payment_Status, Kitchen.Kitchen_ID, Kitchen.Kitchen_Name, Delivery_Management.Delivery_Timings, Delivery_Management.Door_Step_Delivery FROM Lunch_Box_Order LEFT JOIN Kitchen ON Lunch_Box_Order.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Payment ON Lunch_Box_Order.Payment_ID = Payment.Payment_ID LEFT JOIN Delivery_Management ON Lunch_Box_Order.Delivery_ID = Delivery_Management.Delivery_ID Where Lunch_Box_Order.User_ID='"+req['USER_ID']+"'")
                myresult = mycursor.fetchall()
                print(myresult)
                LunchBoxOrdersList = []
                RecordCount = len(myresult)
                for i in range(len(myresult)):
                    LunchBoxOrdersRecord = {
                        "Lunch_Box_Order_ID" : myresult[i][0],
                        "Lunch_Box_Type" : myresult[i][1],
                        "Lunch_Box_Size": myresult[i][2],
                        "Lunch_Box_color_pref": myresult[i][3],
                        "Payment_type": myresult[i][4],
                        "Payment_Amt": myresult[i][5],
                        "Payment_Status": myresult[i][6],
                        "Kitchen_ID": myresult[i][7],
                        "Kitchen_Name": myresult[i][8],
                        "Delivery_Timings": myresult[i][9],
                        "Door_Step_Delivery" : myresult[i][10]
                    }
                    LunchBoxOrdersList.append(LunchBoxOrdersRecord)
                return jsonify(StatusCode = '1', Total = RecordCount, LunchBoxOrdersList=LunchBoxOrdersList)
        except Exception as e:
            return str(e)



if __name__ == '__main__':
  
    app.run(debug = True)