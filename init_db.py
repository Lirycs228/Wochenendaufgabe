import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
print(os.environ.get("DB_SERVER"))

conn = mysql.connector.connect(
    host=f"{os.environ.get("DB_SERVER")}",
    port=os.environ.get("DB_PORT"),
    user=f"{os.environ.get("MYSQL_USER")}",
    password=f"{os.environ.get("MYSQL_PASSWORD")}",
    database=f"{os.environ.get("MYSQL_DATABASE")}"
)

curr = conn.cursor()

try:
    curr.execute("" \
    "CREATE TABLE properties ( " \
    "id INT AUTO_INCREMENT PRIMARY KEY, " \
    "Straße varchar(255) NOT NULL, " \
    "Hausnummer varchar(100) NOT NULL, " \
    "PLZ varchar(5) NOT NULL, " \
    "Ort varchar(255) NOT NULL, " \
    "Land varchar(255) NOT NULL, " \
    "Baujahr INT(255) NOT NULL, " \
    "Zustand ENUM('simpel', 'normal', 'gehoben') NOT NULL, " \
    "Zimmer DOUBLE(200, 1) NOT NULL, " \
    "Wohnfläche FLOAT NOT NULL, " \
    "Art ENUM('Wohnung', 'Haus', 'MFH') NOT NULL"
    ")")
except Exception as e:
    print(e)

try:
    curr.execute("" \
    "CREATE TABLE criteria ( " \
    "id INT AUTO_INCREMENT PRIMARY KEY, " \
    "Art ENUM('Wohnung', 'Haus', 'MFH'), " \
    "Ort varchar(255), " \
    "ZimmerMin DOUBLE(200, 1), " \
    "ZimmerMax DOUBLE(200, 1), " \
    "WohnflächeMin FLOAT, " \
    "WohnflächeMax FLOAT, " \
    "Zustand ENUM('simpel', 'normal', 'gehoben')" \
    ")")
except Exception as e:
    print(e)

try:
    curr.execute("" \
    "CREATE TABLE buyer ( " \
    "id INT AUTO_INCREMENT PRIMARY KEY, " \
    "Vorname varchar(255) NOT NULL, " \
    "Nachname varchar(100) NOT NULL, " \
    "Budget DOUBLE(200, 2), " \
    "SuchkriterienId INT, " \
    "FOREIGN KEY (SuchkriterienId) REFERENCES criteria(id)"
    ")")
except Exception as e:
    print(e)

try:
    curr.execute("" \
    "CREATE TABLE owner ( " \
    "id INT AUTO_INCREMENT PRIMARY KEY, " \
    "Vorname varchar(255) NOT NULL, " \
    "Nachname varchar(100) NOT NULL, " \
    "Geburtsdatum DATE NOT NULL, " \
    "Email VARCHAR(255), " \
    "Telefonnummer VARCHAR(20)"
    ")")
except Exception as e:
    print(e)

try:
    curr.execute("" \
    "CREATE TABLE realtor ( " \
    "id INT AUTO_INCREMENT PRIMARY KEY, " \
    "Vorname varchar(255) NOT NULL, " \
    "Nachname varchar(100) NOT NULL"
    ")")
except Exception as e:
    print(e)

try:
    curr.execute("" \
    "CREATE TABLE event ( " \
    "id INT AUTO_INCREMENT PRIMARY KEY, " \
    "realtorId INT NOT NULL, " \
    "buyerId INT NOT NULL, " \
    "propertiesId INT, " \
    "Inhalt VARCHAR(255) NOT NULL, " \
    "DatumUhrzeit DATETIME NOT NULL, " \
    "FOREIGN KEY (realtorId) REFERENCES realtor(id), " \
    "FOREIGN KEY (buyerId) REFERENCES buyer(id), " \
    "FOREIGN KEY (propertiesId) REFERENCES properties(id)"
    ")")
except Exception as e:
    print(e)


try:
    curr.execute("" \
    "CREATE TABLE note ( " \
    "id INT AUTO_INCREMENT PRIMARY KEY, " \
    "Typ ENUM('Gespräch', 'Telefonat', 'E-Mail') NOT NULL, " \
    "buyerId INT NOT NULL, " \
    "Inhalt VARCHAR(255), " \
    "Foreign KEY (buyerId) REFERENCES buyer(id)"
    ")")
except Exception as e:
    print(e)


curr.execute("SHOW TABLES")
print(curr.fetchall())

conn.close()