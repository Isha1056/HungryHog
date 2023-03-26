Create Database tiffin_service;
SHOW DATABASES;
USE tiffin_service;

CREATE TABLE User_Subscribed (
Subscription_ID  varchar(255) Not Null,
Subscription_Type  varchar(255),
Subscription_plan varchar(255),
primary key (Subscription_ID)
);
INSERT INTO User_Subscribed VALUE ('1001', 'Premium', 'Monthly');
INSERT INTO User_Subscribed VALUE ('1002', 'Premium', 'Quarterly');
INSERT INTO User_Subscribed VALUE ('1003', 'Premium', 'Weekly');
INSERT INTO User_Subscribed VALUE ('1004', 'Premium', 'Daily');

select * from User_Subscribed;

CREATE TABLE USERS (
    USER_ID numeric NOT NULL,
    USER_NAME varchar(255),
    USER_PASSWORD varchar(255),
    USER_TYPE varchar(255),
	USER_EMAIL varchar(255),
    USER_ADDRESS varchar(255),
    USER_MOBILE varchar(255),
    VEG_NONVEG_PERF varchar(255),
    Subscription_ID varchar(255) Not Null,
	PRIMARY KEY (USER_ID),
    FOREIGN KEY (Subscription_ID) REFERENCES User_Subscribed(Subscription_ID)
);

INSERT INTO USERS VALUES (1011, 'Rishabh Bhatia', 'Pass@123', 'Normal' ,'xyz@gmail.com','Andheri East, Mumbai', '7777777777', 'Non-veg','1001');
INSERT INTO USERS VALUES (1012, 'Isha Gupta', 'Pass@123', 'Normal' ,'abc@gmail.com','Airoli, navi Mumbai', '7877777777', 'Non-veg','1001');

INSERT INTO USERS VALUES (1013, 'Angad Singh', 'Pass@123', 'Normal' ,'pqr@gmail.com','Airoli, navi Mumbai', '7877777779', 'Non-veg','1002');
INSERT INTO USERS VALUES (1014, 'Shreyas Joshi', 'Pass@123', 'Normal' ,'jkl@gmail.com','Thane', '7877777799', 'Veg','1003');
INSERT INTO USERS VALUES (1015, 'Sunil Lakhwani', 'Pass@123', 'Normal' ,'you@gmail.com','Andheri East, Mumbai', '7877777796', 'Non-veg','1002');
INSERT INTO USERS VALUES (1016, 'Yashvi Bhatt', 'Pass@123', 'Normal' ,'mno@gmail.com','Ghatkopar, Mumbai', '7877777770', 'Veg','1004');


SELECT * FROM USERS WHERE USER_EMAIL = 'xyz@gmail.com';

select * from USERS;

CREATE TABLE Meals (
    Meal_ID numeric NOT NULL,
    Meal_Type varchar(255),
    Meal_Timings varchar(255),
	PRIMARY KEY (Meal_ID)
);

INSERT INTO Meals VALUES (2010, 'Lunch', '1:00-3:00');
INSERT INTO Meals VALUES (2011, 'Breakfast', '8:00-11:00');
INSERT INTO Meals VALUES (2012, 'Dinner', '20:00-23:00');
select * from Meals;

CREATE TABLE Kitchen (
    Kitchen_ID numeric NOT NULL,
    Kitchen_Name varchar(255),
    Kitchen_Type varchar(255),
    Kitchen_open_time varchar(255),
    Kitchen_Close_time varchar(255),
	Kitchen_Address varchar(255),
    Kitchen_Ratings varchar(255),
    Kitchen_Number varchar(255),
    Popularity varchar(255),
    Meal_ID numeric Not Null,
	PRIMARY KEY (Kitchen_ID),
    FOREIGN KEY (Meal_ID) REFERENCES Meals(Meal_ID)
);

INSERT INTO Kitchen VALUES (3001, 'Angad Ka Dhaba', '', '8:00', '23:59', 'Andheri Railway station, Mumbai', '4.5', '2222222222', 'High', 2012);
INSERT INTO Kitchen VALUES (3002, 'Dabba Garam', '', '9:00', '23:59', 'Chakala Metro, Mumbai', '3.7', '2822222222', 'Medium', 2010);
INSERT INTO Kitchen VALUES (3003, 'Hare Rama Hare Krishna', '', '8:00', '23:59', 'Western Express Highway metro, Mumbai', '4.7', '2822222222', 'Very High', 2012);
INSERT INTO Kitchen VALUES (3004, 'Senorita FoodHall', '', '10:00', '23:59', 'Khar West, Mumbai', '4.7', '2822222222', 'Very High', 2010);
INSERT INTO Kitchen VALUES (3005, 'Louis Burger', '', '11:00', '23:59', 'Andher West, Mumbai', '4.5', '2822222222', 'Very High', 2010);
INSERT INTO Kitchen VALUES (3006, 'Bikaner Breakfast House', '', '7:00', '23:59', 'Versova, Mumbai', '4.0', '2822222288', 'High', 2011);

select * from Kitchen;

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

INSERT INTO Delivery_Partner VALUES ('DLP1010', 'Ram Kumar', '', 'KTM Bike', '33333333333', '4', '1');
INSERT INTO Delivery_Partner VALUES ('DLP1011', 'Kapil Shrama', '', 'Jupiter Scooter', '33333333338', '3.5', '2');
# 0 -  Not vaccinated, 1 = 2 Doses Vacinated, 2 - 3 Doses Vaccinated  
select * from Delivery_Partner;


CREATE TABLE Delivery_Management (
    Delivery_ID varchar(255) NOT NULL,
    Delivery_Partner_ID varchar(255),
    Delivery_Timings varchar(255),
    Delivery_Type varchar(255),
    Door_Step_Delivery varchar(255),
	PRIMARY KEY (Delivery_ID),
    FOREIGN KEY (Delivery_Partner_ID) REFERENCES Delivery_Partner(Delivery_Partner_ID)
);
INSERT INTO Delivery_Management VALUES('DLM2010', 'DLP1010','1:00', '', 'Yes');
INSERT INTO Delivery_Management VALUES('DLM2011', 'DLP1011','5:00', '', 'Yes');
select * from Delivery_Management;


CREATE TABLE Payment(
    Payment_ID varchar(255) NOT NULL,
    Payment_type varchar(255),
    Payment_Amt varchar(255),
    Payment_Status varchar(255),
	PRIMARY KEY (Payment_ID)
);	
INSERT INTO Payment VALUES ('PAY4000', 'COD', '233', 'Completed');
INSERT INTO Payment VALUES ('PAY4001', 'Debit Card', '450', 'Completed');
select * from Payment;


drop table Lunch_Box_Order;

CREATE TABLE Lunch_Box_Order (
    Lunch_Box_Order_ID varchar(255) NOT NULL,
    Lunch_Box_Type varchar(255),
    Lunch_Box_Size varchar(255),
    Lunch_Box_color_pref varchar(255),
    User_ID numeric NOT NULL,
	Payment_ID varchar(255) NOT NULL,
    Delivery_ID varchar(255) NOT NULL,
    Kitchen_ID numeric NOT NULL,
	PRIMARY KEY (Kitchen_ID),
    FOREIGN KEY (User_ID) REFERENCES USERS(User_ID),
    FOREIGN KEY (Payment_ID) REFERENCES Payment(Payment_ID),
    FOREIGN KEY (Delivery_ID) REFERENCES Delivery_Management(Delivery_ID),
    FOREIGN KEY (Kitchen_ID) REFERENCES Kitchen(Kitchen_ID)
);

INSERT INTO Lunch_Box_Order VALUES ('LBO2020', '', 'Large', 'Bule', 1011, 'PAY4000', 'DLM2010', 3001);
INSERT INTO Lunch_Box_Order VALUES ('LBO2021', '', 'Large', 'Green', 1011, 'PAY4001', 'DLM2011', 3002);
select * from Lunch_Box_Order;


select Lunch_Box_Order.Lunch_Box_Order_ID, Lunch_Box_Order.Lunch_Box_Type, Lunch_Box_Order.Lunch_Box_Size, 
Lunch_Box_Order.Lunch_Box_color_pref, Payment.Payment_type, Payment.Payment_Amt, Payment.Payment_Status,
Kitchen.Kitchen_ID, Kitchen.Kitchen_Name, Delivery_Management.Delivery_Timings, Delivery_Management.Door_Step_Delivery
FROM Lunch_Box_Order
LEFT JOIN Kitchen
ON Lunch_Box_Order.Kitchen_ID = Kitchen.Kitchen_ID
LEFT JOIN Payment 
ON Lunch_Box_Order.Payment_ID = Payment.Payment_ID
LEFT JOIN Delivery_Management 
ON Lunch_Box_Order.Delivery_ID = Delivery_Management.Delivery_ID
Where Lunch_Box_Order.User_ID='1011'
;



SHOW TABLES;


CREATE TABLE SNACK (
    SNACK_ID varchar(255) NOT NULL,
    SNACK_NAME varchar(255),
    SNACK_PRICE varchar(255),
    Kitchen_ID numeric Not Null,
	Meal_ID numeric Not Null,
    SNACK_LOGO BLOB,
	PRIMARY KEY (SNACK_ID),
    FOREIGN KEY (Kitchen_ID) REFERENCES Kitchen(Kitchen_ID),
    FOREIGN KEY (Meal_ID) REFERENCES Meals(Meal_ID)
);

DELETE FROM SNACK WHERE SNACK_ID='SNK0004';

INSERT INTO SNACK VALUES ('SNK0001', 'VEG MOMOS', '45', 3001, 2012, load_file("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/snacks_vegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0002', 'Fried Chicken Momos', '60', 3002, 2010, load_file("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/snacks_frynonvegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0003', 'Veg Chawmin', '65', 3003, 2012, load_file("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/snacks_chommeen.jpg"));
INSERT INTO SNACK VALUES ('SNK0004', 'Chicken Momos', '55', 3004, 2010, load_file("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/snacks_nonvegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0005', 'Fried Veg Momos', '50', 3005, 2010, load_file("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/snacks_vegmomo.jpg"));
INSERT INTO SNACK VALUES ('SNK0006', 'Veg Sprign roll', '60', 3006, 2011, load_file("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/snacks_vegroll.jpg"));
INSERT INTO SNACK VALUES ('SNK0007', 'Golgappa', '50',3005, 2010, load_file("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/snacks_gol.jpg"));

SELECT * FROM SNACK;

select SNACK.SNACK_ID, SNACK.SNACK_NAME, SNACK.SNACK_PRICE, SNACK.Kitchen_ID, Kitchen.Kitchen_Name, SNACK.Meal_ID, 
SNACK.SNACK_LOGO, Meals.Meal_Type, Meals.Meal_Timings
FROM SNACK
LEFT JOIN Kitchen
ON SNACK.Kitchen_ID = Kitchen.Kitchen_ID
LEFT JOIN Meals
ON SNACK.Meal_ID = Meals.Meal_ID









