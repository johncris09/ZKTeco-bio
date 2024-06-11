import mysql.connector
from zk import ZK, const

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    port="3306",
    password="",
    database="dbname"
)

cursor = db.cursor()



# Initialize ZKTeco device connection
zk = ZK('192.168.3.106', port=4370, timeout=5)
try:
    # connect to device
    conn = zk.connect()
    # disable device, this method ensures no activity on the device while the process is run
    conn.disable_device()
    
    # get the ip address of the device
    ip_address =  conn.get_network_params()['ip']
    
    # Get attendances (will return list of Attendance object)
    attendances = conn.get_attendance()
    
    
    # live capture! (timeout at 10s)
    for attendance in conn.live_capture():
        if attendance is None:
            # implement here timeout logic
            pass
        else:
            user_id = attendance.user_id
            date = attendance.timestamp.strftime('%Y-%m-%d')
            time = attendance.timestamp.strftime('%H:%M:%S')
            
            # Insert log into database
            cursor.execute("INSERT INTO attendance (id_number, bio_date, bio_time, ip_address) VALUES (%s, %s, %s, %s)", (user_id, date, time, ip_address))
            db.commit()
            
            print("Log of User ID: " +  user_id  +" is inserted successfully."  )
    
except Exception as e:
    print ("Process terminate : {}".format(e))
finally:
    if conn:
        conn.disconnect()