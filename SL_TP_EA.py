
import socket
import MetaTrader5 as mt5
import re,time,pdb,time,threading

def main():
   login=22334134
   password="5(jt0MqVowo!"
   server="Forex.com-Demo 535"
   terminalconnect(login,password,server)
   createsocket()

    
#creates the socket for communication
def createsocket():
   
      global sock
      global msd
      sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      sock.bind(("",2023))
      sock.listen()
      print("socket is listening")
      while True:
         t1=threading.Thread(target=createThread,args=(sock,))
         t1.start()
         print("listening thread: ",t1.native_id,'\n')
         time.sleep(10)
         
def createThread(sock):
   
      conn, addr=sock.accept()
      print("socket accepts the connection")
         
      conn.send("finally working".encode())
         
      msd=str(conn.recv(1024).decode('utf-8'))
      print(msd)
      

         
      #filtering the recieved message to get ATR and pair information
      _=re.split(r"\x00",msd)[0:-1]
      print(_)
      ATR=round(float(_[0]),4)
      pair=_[1]
      position=_[-1]
      t2=threading.Thread(target=trade_manager,args=(pair,ATR,position,))
      t2.start()
      print("managing thread: ",t2.native_id,'\n')
      time.sleep(10)
      
      
      
      
   

#connects to the metatrader 5 terminal
def terminalconnect(login,password,server):
   login=login
   password=password
   server=server
   account=mt5.login(login,password,server)
   initialize=mt5.initialize(login=login,password=password,server=server)
   print(initialize)
   return initialize

#get the ticket information
def get_ticket(dparsed,ATR,pair):
     order=mt5.positions_get(symbol=pair)
     a=re.search("ticket=(\d+)",str(order))
     ticket=int(str(a.group(1)))
     if len(mt5.positions_get(symbol=pair))==0:
         closesocket()
     return ticket
  
#Trade manager
def trade_manager(pair,ATR,position):
   #step 1:get the recent price and ticket #
   pairinfo=str(mt5.symbol_info(pair))
   price=re.search("bid=((\d)+\.(\d)+),",pairinfo)
   dparsed=float(price.group(1))
   price_list=[dparsed]
   ticket=get_ticket(dparsed,ATR,pair)
   count=0
                     
   #step 3:check if price has gone beyond your takeprofit level, then take profit if true
   _=mt5.positions_get(symbol=pair)
   _=re.search("price_open=(\d+\.\d+)",str(_))
   price_in=float(_.group(1))
   takeprofit=price_in+(ATR*1)
   if dparsed>takeprofit:
      exit=mt5.Close(pair,ticket=ticket)
   else:
      limits(dparsed,ATR,ticket,pair,position)
   
#checks if trade can be exitted and exits        
def trade_exit(ticket,pair):
      #loop through this step until 7:00 pm
      while time.localtime().tm_hour!=19 and time.localtime()!=0:
         if input("exit?: ")=="yes":
            _=mt5.positions_get(symbol=pair)
            _=re.search("volume=(\d?\.\d{2})",str(_))
            volume=float(_.group(1))
            #send the request to exit
            request={"action":mt5.TRADE_ACTION_DEAL,"order":ticket,"symbol":pair,"volume":float(volume),"type":mt5.ORDER_TYPE_SELL}
            exit=mt5.Close(pair)  
   
#sets the initial limit
def limits(dparsed,ATR,ticket,pair,position):
   if position=="true":
      stoploss=dparsed-(ATR*1.5)
   elif position=="false":
      stoploss=dparsed+(ATR*1.5)
   if positions_get(ticket=ticket):
      sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":0.000,
      "position":ticket}
      sl=mt5.order_send(sl_request)
      print(sl)
  
      if position=="true":
         lastPrice=dparsed
         while True:
            priceNow=mt5.symbol_info(pair).bid
            if priceNow>lastPrice:
               stoploss=priceNow-(ATR*1.5)
               sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":0.000,
         "position":ticket}
               sl=mt5.order_send(sl_request)
               lastPrice=priceNow
               print(sl)
      elif position=="false":
         lastPrice=dparsed
         while True:
            priceNow=mt5.symbol_info(pair).bid
            if priceNow<lastPrice:
               stoploss=priceNow+(ATR*1.5)
               sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":0.000,
         "position":ticket}
               sl=mt5.order_send(sl_request)
               lastPrice=priceNow
               print(sl)
               print(priceNow)

      
#closes the socket connection
def closesocket():
   global sock
   sock.close()
   return("socket is closed")

main()
