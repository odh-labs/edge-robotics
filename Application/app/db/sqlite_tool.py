import sqlite3  
import datetime
import base64
from .sys_colors import bcolors

# from datetime import timedelta
class SQLite():
    def __init__(self, file='ANPR.db'):
        self.file=file
    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

class SQLiteTool():

    def __init__(self,total_cam=1):
        """initialise the sqlite connection
        
        """
        # self.conn = sqlite3.connect('ANPR_Guise.db')
        self.db = "ROBOT.db" #envconf('MDB', default='ANPR.db')
        self.col_robots = 'robots'#envconf('ROBOTS', default='robots')

        self.total_cameras = total_cam
        self.create_table_robot(self.col_robots)

    def create_table_robot(self,table_name):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """    
        self.conn = sqlite3.connect(self.db)
        try:
            delete_old_table_sql = """ DROP TABLE IF EXISTS {}; """.format(table_name)
            with SQLite(self.db) as curr:
                curr.execute(delete_old_table_sql)
            
            create_table_sql = """ CREATE TABLE IF NOT EXISTS {} (
                                        id integer,
                                        label text,
                                        alert_type text,                                        
                                        timestamp text
                                    ); """.format(table_name)
            with SQLite(self.db) as curr:
                curr.execute(create_table_sql)
        except Exception as e:
            print(e)

    def insert_robot(self,data,ordered=False):
        
        insert_query = ''' INSERT INTO {}(id, label,alert_type,timestamp)
              VALUES(?,?,?,?) '''

        data_ins = (data['id'],data['label'],data['alert_type'],data['timestamp'])

        insert_query_robot = insert_query.format(f"{self.col_robots}")

        with SQLite(self.db) as cur:
            cur.execute(insert_query_robot, data_ins)
            
        return 'values inserted'

    def get_robot_results(self,fetched_vehicle_data,all_flag,limit_data=False):

            final_list = []
            fetched_ids = []
            time_thres = 1800
                        
            for vehicle in fetched_vehicle_data:
                # print(f"Fetched Data:{vehicle}")
                # print(vehicle['timestamp'])
                
                # print((d1 - d2).total_seconds())
                
                new_dict = {}
                new_dict['id'] = vehicle['id']
                new_dict['label'] = vehicle['label'].title()                    
                #new_dict['image_path'] = vehicle['image_path']                    
                                    
                '''v_encoded_image = None
                try:
                    v_image_path = vehicle['image_path']
                    with open(v_image_path, "rb") as image_file:
                        v_encoded_image = base64.b64encode(image_file.read()).decode("utf8")
                    new_dict['vehicle_image'] = v_encoded_image
                except:
                    new_dict['vehicle_image'] = v_encoded_image'''
                new_dict['alert_type'] = vehicle['alert_type']
                new_dict['timestamp'] = vehicle['timestamp']                    
                final_list.append(new_dict)
                # else:
                #     print("Too Old")
                fetched_ids.append(vehicle['id'])
            return final_list,fetched_ids

    def fetch_robot_data(self):
        
        all_flag = True
        
        qry_condition = ""
        select_qry = """SELECT * FROM {} {} """.format(self.col_robots,qry_condition)
        # print(select_qry)
        with SQLite(self.db) as cur:
            d = cur.execute(select_qry)
            fetched_vehicle_data =d.fetchall()
            try:
                final_list,fetched_ids = self.get_robot_results(fetched_vehicle_data,all_flag)
                # remove fetched ids
            except Exception as exp:
                print(exp)
                print(f"{bcolors.FAIL}[DB] Error: Error in retreiving data from DB{bcolors.ENDC}")
                final_list = []
            try:
                # if len(fetched_ids) > 0 and not all_flag:
                #     fetched_ids = tuple(fetched_ids) if len(fetched_ids) > 1 else f'({fetched_ids[0]})'
                if not all_flag:
                    del_condition = ""#"WHERE id IN {}".format(fetched_ids)
                    remove_entries = self.delete(f"{self.col_robots}",del_condition)
            except Exception as exp:
                print(exp)
                print(f"{bcolors.FAIL}[DB] Error: Errorin deleting data from DB{bcolors.ENDC}")
                final_list = []
        # print(final_list)
        return final_list

    def connect(self,db):
        """connect to sqlite 
        """
        self.conn = sqlite3.connect(db)

    def delete(self,table_name,qry_condtition):
        """Deletes data
        """
        # remove all vehicles
        del_qry = """DELETE FROM {} {} """.format(table_name,qry_condtition)
        #print(del_qry)
        with SQLite(self.db) as cur:
            d = cur.execute(del_qry)
        return 'values deleted'

if __name__=="__main__":
    mt=SQLiteTool()