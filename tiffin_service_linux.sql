DROP DATABASE tiffin_service;
Create Database IF NOT EXISTS tiffin_service;
SHOW DATABASES;
USE tiffin_service;


DROP TABLE Lunch_Box_Order;
DROP TABLE USER_SUBSCRIBED;
DROP TABLE USERS;
DROP TABLE SNACK;
DROP TABLE ORDER_SUMMARY;
DROP TABLE Kitchen;
DROP TABLE Meals;
DROP TABLE Delivery_Management;
DROP TABLE Delivery_Partner;
DROP TABLE Payment;



CREATE TABLE USERS (
    USER_NAME varchar(255),
    USER_PASSWORD varchar(255),
	USER_EMAIL varchar(255),
    USER_STREET varchar(255),
    USER_STATE varchar(255),
    USER_CITY varchar(255),
    USER_COUNTRY varchar(255),
    USER_PINCODE varchar(255),
    USER_MOBILE varchar(255),
    USER_PRIVATE_KEY varchar(255),
    USER_LATITUDE FLOAT,
    USER_LONGITUDE FLOAT,
	PRIMARY KEY (USER_EMAIL)
);
CREATE TABLE USER_SUBSCRIBED (
	SUBSCRIPTION_ID  varchar(255) Not Null,
	SUBSCRIPTION_TYPE  varchar(255),
	SUBSCRIPTION_PLAN varchar(255),
	USER_EMAIL varchar(255) not null,
	PRIMARY KEY (Subscription_ID),
	FOREIGN KEY (USER_EMAIL) REFERENCES USERS(USER_EMAIL)
);
CREATE TABLE Meals (
    Meal_ID numeric NOT NULL,
    Meal_Type varchar(255),
    Meal_Timings varchar(255),
	PRIMARY KEY (Meal_ID)
);
CREATE TABLE Kitchen (
    Kitchen_ID varchar(255) NOT NULL,
    Kitchen_Email varchar(255) NOT NULL,
    Kitchen_Name varchar(255),
    Kitchen_Password varchar(255),
    Kitchen_Type varchar(255),
    Kitchen_Open_Time varchar(255),
    Kitchen_Close_Time varchar(255),
	Kitchen_Address varchar(255),
    Kitchen_City varchar(255),
    Kitchen_State varchar(255),
    Kitchen_Country varchar(255),
    Kitchen_Pincode varchar(255),
    Kitchen_Ratings FLOAT,
    Kitchen_Number varchar(255),
    Popularity varchar(255),
    Kitchen_Latitude FLOAT,
    Kitchen_Longitude FLOAT,
    Kitchen_Review_Count numeric Not Null,
    Kitchen_Review_Total numeric Not Null,
    Kitchen_Private_Key varchar(255),
	PRIMARY KEY (Kitchen_ID)
);
CREATE TABLE Delivery_Partner (
    Delivery_Partner_ID varchar(255) NOT NULL,
    Delivery_Partner_Name varchar(255),
    Delivery_Partner_Type varchar(255),
    Delivery_Partner_Vehical varchar(255),
    Delivery_Partner_Number varchar(255),
	Delivery_Partner_Ratings varchar(255),
    Vaccination_Status varchar(255),
	PRIMARY KEY (Delivery_Partner_ID)
);
CREATE TABLE Delivery_Management (
    Delivery_ID varchar(255) NOT NULL,
    Delivery_Partner_ID varchar(255),
    Delivery_Timings varchar(255),
    Delivery_Type varchar(255),
    Door_Step_Delivery varchar(255),
	PRIMARY KEY (Delivery_ID),
    FOREIGN KEY (Delivery_Partner_ID) REFERENCES Delivery_Partner(Delivery_Partner_ID)
);
CREATE TABLE Payment(
    Payment_ID varchar(255) NOT NULL,
    Payment_type varchar(255),
    Payment_Amt varchar(255),
    Payment_Status varchar(255),
	PRIMARY KEY (Payment_ID)
);	
CREATE TABLE Lunch_Box_Order (
    Lunch_Box_Order_ID varchar(255) NOT NULL,
    Lunch_Box_Type varchar(255),
    Lunch_Box_Size varchar(255),
    Lunch_Box_color_pref varchar(255),
    USER_EMAIL varchar(255) NOT NULL,
	Payment_ID varchar(255) NOT NULL,
    Delivery_ID varchar(255) NOT NULL,
    Kitchen_ID varchar(255) NOT NULL,
	PRIMARY KEY (Kitchen_ID),
    FOREIGN KEY (USER_EMAIL) REFERENCES USERS(USER_EMAIL),
    FOREIGN KEY (Payment_ID) REFERENCES Payment(Payment_ID),
    FOREIGN KEY (Delivery_ID) REFERENCES Delivery_Management(Delivery_ID),
    FOREIGN KEY (Kitchen_ID) REFERENCES Kitchen(Kitchen_ID)
);
CREATE TABLE SNACK (
    SNACK_ID varchar(255) NOT NULL,
    SNACK_NAME varchar(255),
    SNACK_PRICE varchar(255),
    Kitchen_ID varchar(255) Not Null,
	Meal_ID numeric Not Null,
    SNACK_LOGO BLOB,
    SNACK_REVIEW_COUNT numeric Not Null,
    SNACK_REVIEW_TOTAL numeric Not Null,
    SNACK_RATING FLOAT Not Null,
	PRIMARY KEY (SNACK_ID),
    FOREIGN KEY (Kitchen_ID) REFERENCES Kitchen(Kitchen_ID),
    FOREIGN KEY (Meal_ID) REFERENCES Meals(Meal_ID)
);
CREATE TABLE ORDER_SUMMARY (
    PRODUCT_ID varchar(255) NOT NULL,
    PRODUCT_NAME varchar(255),
    PRODUCT_PRICE varchar(255),
    PRODUCT_LOGO BLOB,
    Kitchen_ID varchar(255) Not Null,
    SCHEDULE_TIME varchar(255),
    TOTAL_AMOUNT numeric,
    QUANTITY numeric,
    Meal_ID numeric NOT NULL,
    USER_EMAIL varchar(255) NOT NULL,
    PAYMENT_ID varchar(255),
    IS_COMPLETE numeric NOT NULL,
    FOREIGN KEY (Kitchen_ID) REFERENCES Kitchen(Kitchen_ID),
    FOREIGN KEY (Meal_ID) REFERENCES Meals(Meal_ID)
);
SHOW TABLES;





INSERT INTO USERS VALUES ('Rishabh Bhatia', 'Pass@123' ,'xyz@gmail.com', 'Street1', 'Maharashtra', 'Andheri East, Mumbai', 'India','400321', '7777777777', 'abc', 122.123, 123.123);
INSERT INTO USERS VALUES ('Isha Gupta', 'Pass@123', 'abc@gmail.com', 'Street2', 'Maharashtra', 'Airoli, navi Mumbai', 'India', '123456','7877777777', 'pqr', 122.123, 123.123);
INSERT INTO USERS VALUES ('Angad Singh', 'Pass@123', 'pqr@gmail.com', 'Street3', 'Maharashtra', 'Airoli, navi Mumbai', 'India',  '654321','7877777779', 'xyz', 122.123, 123.123);
INSERT INTO USERS VALUES ('Shreyas Joshi', 'Pass@123', 'jkl@gmail.com', 'Street4', 'Maharashtra', 'Thane', 'India', '678901','7877777799', 'lmn', 122.123, 123.123);
INSERT INTO USERS VALUES ('Sunil Lakhwani', 'Pass@123', 'you@gmail.com', 'Street5', 'Maharashtra', 'Andheri East, Mumbai', 'India', '253782','7877777796', 'zxc', 122.123, 123.123);
INSERT INTO USERS VALUES ('Yashvi Bhatt', 'Pass@123', 'mno@gmail.com', 'Street6', 'Maharashtra', 'Ghatkopar, Mumbai', 'India', '234567','7877777770', 'qwe', 122.123, 123.123);
select * from USERS;


INSERT INTO USER_SUBSCRIBED VALUE ('1001', 'Premium', 'Monthly', 'xyz@gmail.com');
INSERT INTO USER_SUBSCRIBED VALUE ('1002', 'Premium', 'Quarterly', 'abc@gmail.com');
INSERT INTO USER_SUBSCRIBED VALUE ('1003', 'Premium', 'Weekly', 'pqr@gmail.com');
INSERT INTO USER_SUBSCRIBED VALUE ('1004', 'Premium', 'Daily', 'jkl@gmail.com');
select * from USER_SUBSCRIBED;


INSERT INTO Meals VALUES (2010, 'Lunch', '1:00-3:00');
INSERT INTO Meals VALUES (2011, 'Breakfast', '8:00-11:00');
INSERT INTO Meals VALUES (2012, 'Dinner', '20:00-23:00');
INSERT INTO Meals VALUES (2013, 'Mid-Night', '00:00-5:00');
INSERT INTO Meals VALUES (2014, 'Early Morning', '05:00-08:00');
INSERT INTO Meals VALUES (2015, 'All Day', '00:00-23:59');
UPDATE Meals SET Meal_Timings = '11:00-16:00' where Meal_ID='2010';
UPDATE Meals SET Meal_Timings = '08:00-11:00' where Meal_ID='2011';
select * from Meals;

INSERT INTO Delivery_Partner VALUES ('DLP1010', 'Ram Kumar', '', 'KTM Bike', '33333333333', '4', '1');
INSERT INTO Delivery_Partner VALUES ('DLP1011', 'Kapil Shrama', '', 'Jupiter Scooter', '33333333338', '3.5', '2');
select * from Delivery_Partner;

INSERT INTO Delivery_Management VALUES('DLM2010', 'DLP1010','1:00', '', 'Yes');
INSERT INTO Delivery_Management VALUES('DLM2011', 'DLP1011','5:00', '', 'Yes');
select * from Delivery_Management;

INSERT INTO Payment VALUES ('PAY4000', 'COD', '233', 'Completed');
INSERT INTO Payment VALUES ('PAY4001', 'Debit Card', '450', 'Completed');
select * from Payment;


INSERT INTO Kitchen VALUES ('akd','akd@gmail.com', 'Angad Ka Dhaba', 'pass@123', '', '8:00', '23:59', 'Andheri Railway station, Mumbai', 'Mumbai', 'Maharashtra', 'India', '400053', 0, '2222222222', 'High', 19.150206863545474, 72.82677495588325, 0, 0, 'abc123456');
INSERT INTO Kitchen VALUES ('dg', 'dg@gmail.com', 'Dabba Garam', 'pass@123', '', '9:00', '23:59', 'Chakala Metro, Mumbai', 'Mumbai', 'Maharashtra', 'India', '400053', 0, '2822222222', 'Medium', 19.16145883073272, 72.99882270411405, 0, 0, 'abc123456');
INSERT INTO Kitchen VALUES ('hrhk', 'hrhk@gmail.com', 'Hare Rama Hare Krishna', 'pass@123', '', '8:00', '23:59', 'Western Express Highway metro, Mumbai', 'Mumbai', 'Maharashtra', 'India', '400053', 0, '2822222222', 'Very High', 19.1613777552713, 72.99081899238811, 0, 0, 'abc123456');
INSERT INTO Kitchen VALUES ('sf', 'sf@gmail.com', 'Senorita FoodHall',  'pass@123', '', '10:00', '23:59', 'Khar West, Mumbai', 'Mumbai', 'Maharashtra', 'India', '400053', 0, '2822222222', 'Very High', 19.161641250375165, 72.99167729927562, 0, 0, 'abc123456');
INSERT INTO Kitchen VALUES ('d2418ac039143802ed84c460fdaae214007e7dd5ce2fceda633ec8843e24e0f77aaa1fc7e9c13908ae070b56dd2a6e9ac397a6ac64a1529f2b2b4585856b1f69', 'lb@gmail.com', 'Louis Burger', 'pass@123', '', '11:00', '23:59', 'Andher West, Mumbai', 'Mumbai', 'Maharashtra', 'India', '400053', 0, '2822222222', 'Very High', 19.163080331589306, 72.99189187599751, 0, 0, 'abc123456');
INSERT INTO Kitchen VALUES ('bbk', 'bbk@gmail.com', 'Bikaner Breakfast House', 'pass@123', '', '7:00', '23:59', 'Rohini, Delhi', 'Delhi', 'Delhi', 'India', '110039', 0, '2822222288', 'High', 28.663662204748466, 77.10031119068194, 0, 0, 'abc123456');
select * from Kitchen;



INSERT INTO Lunch_Box_Order VALUES ('LBO2020', '', 'Large', 'Bule', 'xyz@gmail.com', 'PAY4000', 'DLM2010', 'd2418ac039143802ed84c460fdaae214007e7dd5ce2fceda633ec8843e24e0f77aaa1fc7e9c13908ae070b56dd2a6e9ac397a6ac64a1529f2b2b4585856b1f69');
INSERT INTO Lunch_Box_Order VALUES ('LBO2021', '', 'Large', 'Green', 'abc@gmail.com', 'PAY4001', 'DLM2011', 'bbk');
select * from Lunch_Box_Order;
/*
INSERT INTO SNACK VALUES ('SNK0001', 'Veg Momos', '45', 3001, 2012, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_vegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0002', 'Fried Chicken Momos', '60', 3002, 2010, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_frynonvegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0003', 'Veg Chowmein', '65', 3003, 2012, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"));
INSERT INTO SNACK VALUES ('SNK0004', 'Chicken Momos', '55', 3004, 2010, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_nonvegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0005', 'Fried Veg Momos', '50', 3005, 2010, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_vegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0006', 'Veg Spring Rolls', '60', 3006, 2011, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_vegroll.jpg"));
INSERT INTO SNACK VALUES ('SNK0007', 'Golgappa', '50',3005, 2010, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_gol.jpg"));
INSERT INTO SNACK VALUES ('SNK0008', 'Noodles', '100',3005, 2015, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"));
INSERT INTO SNACK VALUES ('SNK0009', 'Kimchi', '140',3005, 2015, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"));
INSERT INTO SNACK VALUES ('SNK00010', 'Boba Tea', '100',3005, 2015, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"));
INSERT INTO SNACK VALUES ('SNK00011', 'Pizza', '400',3005, 2015, load_file("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"));
SELECT * FROM SNACK;
select SNACK.SNACK_ID, SNACK.SNACK_NAME, SNACK.SNACK_PRICE, SNACK.Kitchen_ID, Kitchen.Kitchen_Name, SNACK.Meal_ID, 
SNACK.SNACK_LOGO, Meals.Meal_Type, Meals.Meal_Timings
FROM SNACK
LEFT JOIN Kitchen
ON SNACK.Kitchen_ID = Kitchen.Kitchen_ID
LEFT JOIN Meals
ON SNACK.Meal_ID = Meals.Meal_ID;
*/

select * from USERS;
select * from ORDER_SUMMARY;


