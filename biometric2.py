import time 
import multiprocessing
from zk import ZK, const 
import mysql.connector


# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    port="3306",
    password="",
    database="biometric"
)


cursor = db.cursor()

# constant machine port
machine_port = 4370

# define a list of IP addresses
ip_addresses = [ '192.168.3.100', '192.168.3.103']

def devices(ip_address):
    while True:
        try:
            # Create a ZK object for the device
            zk = ZK(ip_address, port=machine_port, timeout=5, password=0, force_udp=False, ommit_ping=False)
            
            # Connect to the device
            conn = zk.connect()
            if conn:
                conn.disable_device()
                print(f"Connected to device {ip_address}")
                
                for attendance in conn.live_capture():
                    if attendance is None:
                        # implement here timeout logic
                        pass
                    else:
                        user_id = attendance.user_id
                        bio_date = attendance.timestamp.strftime('%Y-%m-%d')
                        bio_time = attendance.timestamp.strftime('%H:%M:%S')
                        
                        
                        # Check if the log already exists
                        cursor.execute("SELECT COUNT(*) FROM attendance WHERE id_number = %s AND bio_date = %s AND bio_time = %s", (user_id, bio_date, bio_time))
                        count = cursor.fetchone()[0]
                        
                        if count == 0:
                            # Insert log into database
                            cursor.execute("INSERT INTO attendance (id_number, bio_date, bio_time, ip_address) VALUES (%s, %s, %s, %s)", (user_id, bio_date, bio_time, ip_address))
                            db.commit()
                            
                    conn.end_live_capture = True
                conn.enable_device()
            else:
                raise Exception(f"Failed to connect to device {ip_address}")
        except Exception as e:
            print(f"Error with device {ip_address}: {e}")
            time.sleep(0.500)   # Wait before retrying

        finally:
            try:
                conn.disconnect()
            except:
                print(f"Attempting to reconnect to device {ip_address}...")
                time.sleep(0.100)   # Wait before retrying

if __name__ == '__main__':
    # Create a process for each device
    processes = []
    for ip_addr in ip_addresses:
        process = multiprocessing.Process(target=devices, args=(ip_addr,))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()

    print("Finished handling live capture for all devices")
