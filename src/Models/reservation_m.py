from .base_m import ObservableModel
from datetime import datetime, timedelta
from database import dbfunc
from tkinter import messagebox
import datetime as dt




class ReservationManager(ObservableModel):

    #creates the reservation with inserted data
    def createReservation(self,restaurantID,customerName,customerNumber,partySize,date,time,employeeID,tableNum):
        self.tableID = self.getTableID(tableNum, restaurantID)
        if self.tableID != None:
            if(self.checkAvailability(date,time,self.tableID,restaurantID,partySize)):
                conn = dbfunc.getConnection() 
                if conn != None:    #Checking if connection is None                    
                    if conn.is_connected(): #Checking if connection is established  
                        dbcursor = conn.cursor()    #Creating cursor object                                                 
                        dbcursor.execute("INSERT INTO reservation (restaurant_id, reservation_customer_name, reservation_customer_phone, \
                                        table_id, reservation_party_size, reservation_author, reservation_creation_time, reservation_date,\
                                            reservation_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (restaurantID, customerName, customerNumber, self.tableID,
                                                                                                        partySize, employeeID,datetime.now(), datetime.strptime(date, '%Y-%m-%d'), datetime.strptime(time, "%H:%M:%S"))) 
                        conn.commit()
                        dbcursor.close()
                        conn.close() 
                        messagebox.showinfo("Sucsess", "Reservation created sucsessfully")
            else:
                messagebox.showerror("Error", "Table not available at that time.")
                
            
    def updateReservation(self, column_index, newValue, reservationID): #updates the data from the reservations table
        #finding out what data type needs to be updated
            
        conn = dbfunc.getConnection() 
        if conn != None:    #Checking if connection is None                    
            if conn.is_connected(): #Checking if connection is established  
                dbcursor = conn.cursor()    #Creating cursor object  
                #updates data
                #finding out what data type needs to be updated
                if column_index == 1:
                    dbcursor.execute('UPDATE reservation SET reservation_customer_name = %s WHERE reservation_id = %s;', (newValue,reservationID)) 
                    messagebox.showinfo("Sucsess", "Name has been updated")
                    
                elif column_index == 2:
                    dbcursor.execute('UPDATE reservation SET reservation_customer_phone = %s WHERE reservation_id = %s;', (newValue,reservationID))
                    messagebox.showinfo("Sucsess", "Number has been updated")
                    
                elif  column_index == 4:  
                    dbcursor.execute("SELECT restaurant_id, reservation_date, reservation_time, reservation_party_size FROM reservation WHERE restaurant_id = "+str(reservationID)+";")
                    reservation = dbcursor.fetchone() 
                    tableID = self.getTableID(newValue,reservation[0]) 
                    if tableID != None:
                        if (self.checkAvailability(reservation[1], reservation[2],tableID,reservation[0],reservation[3])):
                            dbcursor.execute('UPDATE reservation SET table_id = %s WHERE reservation_id = %s;', (tableID,reservationID))
                            messagebox.showinfo("Sucsess", "Table has been updated")
                        else:
                            messagebox.showerror("Error", "Table not available at that time.")
                            
                elif column_index == 5:
                    dbcursor.execute("SELECT restaurant_id, table_id, reservation_time, reservation_party_size FROM reservation WHERE restaurant_id = "+str(reservationID)+";")
                    reservation = dbcursor.fetchone()  
                    if (self.checkAvailability(newValue, reservation[2],reservation[1],reservation[0],reservation[3])):
                        dbcursor.execute('UPDATE reservation SET reservation_date = %s WHERE reservation_id = %s;', (datetime.strptime(newValue, '%Y-%m-%d'),reservationID))
                        messagebox.showinfo("Sucsess", "Date has been updated")
                    else:
                        messagebox.showerror("Error", "Table not available at that time.")
                        
                elif column_index == 6:
                    dbcursor.execute("SELECT restaurant_id, table_id, reservation_date, reservation_party_size FROM reservation WHERE restaurant_id = "+str(reservationID)+";")
                    reservation = dbcursor.fetchone()  
                    if (self.checkAvailability(reservation[2], newValue,reservation[1],reservation[0],reservation[3])):
                        dbcursor.execute('UPDATE reservation SET reservation_time = %s WHERE reservation_id = %s;', (datetime.strptime(newValue, "%H:%M:%S"),reservationID)) 
                        messagebox.showinfo("Sucsess", "Time has been updated")
                    else:
                        messagebox.showerror("Error", "Table not available at that time.")                                              
                
                conn.commit()
                dbcursor.close()
                conn.close() 
    
    def cancelReservation(self, reservationID):
        #cancels a specific reservation by its ID number
        conn = dbfunc.getConnection() 
        if conn != None:    #Checking if connection is None                    
            if conn.is_connected(): #Checking if connection is established  
                dbcursor = conn.cursor()
                dbcursor.execute('DELETE FROM reservation WHERE reservation_id = '+str(reservationID)+';')
                conn.commit()
                dbcursor.close()
                conn.close() 
            
            
    def getReservations(self, restaurantID = None): #gets the reservations made and formats them for the reservations table
        conn = dbfunc.getConnection() 
        if conn != None:    #Checking if connection is None                    
            if conn.is_connected(): #Checking if connection is established  
                dbcursor = conn.cursor()    #Creating cursor object 
                if restaurantID == None:                                            
                    dbcursor.execute("SELECT reservation_id, reservation_customer_name, reservation_customer_phone, restaurant_id, table_id, reservation_date, reservation_time FROM reservation;")    
                else:
                    dbcursor.execute("SELECT reservation_id, reservation_customer_name, reservation_customer_phone, restaurant_id, table_id, reservation_date, reservation_time FROM reservation WHERE restaurant_id = "+str(restaurantID)+";")          
                self.tempreservationlist = dbcursor.fetchall()
                self.reservationlist = []
                for reservation in self.tempreservationlist:
                    self.tempReservation = list(reservation)
                    self.tempReservation[4] = self.getTableNum(self.tempReservation[4])
                    self.reservationlist.append(self.tempReservation)
                dbcursor.close()
                conn.close() 
        return(self.reservationlist)
    
    def getRestaurantNames(self):
        self.restaurantNames = []
        conn = dbfunc.getConnection() 
        if conn != None:    #Checking if connection is None                    
            if conn.is_connected(): #Checking if connection is established  
                dbcursor = conn.cursor()    #Creating cursor object                                                 
                dbcursor.execute("SELECT restaurant_id, restaurant_name FROM restaurant;")                                           
                self.restaurantList = dbcursor.fetchall()
                for restaurant in self.restaurantList:
                    self.tempRestaurantName = str(restaurant[1]) + "("+ str(restaurant[0]) +")"
                    self.restaurantNames.append(self.tempRestaurantName)
                dbcursor.close()
                conn.close() 
        return(self.restaurantNames)
            
            
        
    def checkAvailability(self,reservationDate,reservationTime,tableid,restaurantID, partySize):
        # Calculate the start and end times
        if isinstance(reservationTime, dt.timedelta) != True:
            reservationTime = datetime.strptime(reservationTime, "%H:%M:%S")
        if isinstance(reservationDate, dt.date) != True:
            reservationDate = datetime.strptime(reservationDate, '%Y-%m-%d')
            
            
        self.beforeReservationTime = reservationTime - timedelta(hours=1)
        self.afterReservationTime = reservationTime  + timedelta(hours=1)

        conn = dbfunc.getConnection() 
        if conn != None:    #Checking if connection is None                    
            if conn.is_connected(): #Checking if connection is established  
                dbcursor = conn.cursor()    #Creating cursor object                                                 
                dbcursor.execute("SELECT * FROM reservation WHERE restaurant_id = %s AND table_id = %s AND reservation_date = %s \
                AND reservation_time BETWEEN (%s) AND (%s);", (restaurantID,tableid,reservationDate,self.beforeReservationTime,self.afterReservationTime))
                dbcursor.fetchall()
                if(dbcursor.rowcount > 0): # this means there is reservations takeing those time slots and so the table is not avalible
                    dbcursor.close()
                    conn.close() 
                    messagebox.showerror("Error", "Table already reserved.")   
                    return False
                else:
                    dbcursor.close()
                    dbcursor = conn.cursor()
                    dbcursor.execute("SELECT * FROM tables WHERE table_id = "+str(tableid)+" ;")
                    self.capacity = dbcursor.fetchone()
                    if (int(self.capacity[2]) < int(partySize)):
                        dbcursor.close()
                        conn.close()
                        messagebox.showerror("Error", f"This table has a capacity of {self.capacity[2]}.")   
                        return False
                    else:
                        dbcursor.close()
                        conn.close() 
                        return True
                    
    def getTableID(self, tablenum, restaurantID):
        conn = dbfunc.getConnection() 
        if conn != None:    #Checking if connection is None                    
            if conn.is_connected(): #Checking if connection is established  
                dbcursor = conn.cursor()    #Creating cursor object                                                 
                dbcursor.execute("SELECT * FROM tables WHERE restaurant_id = %s AND table_number = %s ;", (restaurantID,tablenum))
                tableID = dbcursor.fetchone()
                if(dbcursor.rowcount > 0): # finding if table exsits
                    dbcursor.close()
                    conn.close() 
                    return tableID[0]
                else:
                    messagebox.showerror("Error", "Table does not exsit")
                    return None   
                
    def getTableNum(self, tableID):
        conn = dbfunc.getConnection() 
        if conn != None:    #Checking if connection is None                    
            if conn.is_connected(): #Checking if connection is established  
                dbcursor = conn.cursor()    #Creating cursor object                                                 
                dbcursor.execute("SELECT * FROM tables WHERE table_id = "+str(tableID)+" ;")
                tableNum = dbcursor.fetchone()
                if(dbcursor.rowcount > 0): # finding if table exsits
                    dbcursor.close()
                    conn.close() 
                    return(tableNum[1])
                else:
                    messagebox.showerror("Error", "Table does not exsit")
                    return None     
    
            
  
                
        

