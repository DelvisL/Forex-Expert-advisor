import socket
import MetaTrader5 as mt5
import re,time,pdb,time,threading,sys,os,traceback
import win32service,servicemanager,win32serviceutil,win32evtlog



class TradingService(win32serviceutil.ServiceFramework):
    _svc_name_="SL_TP_EA"
    _svc_display_name_="ForexTradingService"
    _exe_name_ = "ForextradingService"
    _svc_description_ = ("This service controls tradinng for limits for MetaTrader accounts")


    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        
        

    def SvcStop(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            self.is_alive=False
        except:
            servicemanager.LogErrorMsg(traceback.format_exc())
        

    def SvcDoRun(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.is_alive=True
            self.main()
        except:
            servicemanager.LogErrorMsg(traceback.format_exc())
        

    def main(self):        
        while self.is_alive==True:
            try:
                main2()
            except:
                servicemanager.LogErrorMsg(traceback.format_exc())
        

if __name__=='__main__':
    if len(sys.argv)==1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TradingService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(TradingService)

        

#starts the process of calling necessary functions
def main2():
  login=MT5 username
  password=MT5 password
  server=MT5 server
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
        file=open("tradingreport.txt",mode='a+')
        file.write("listening thread:" + str(t1.native_id) + '\n')
        file.close()
        time.sleep(10)
        
        
        
#Creates seperate socket for sending and recieiving msg's 
def createThread(sock):
    try:
     conn, addr=sock.accept()
     print("socket accepts the connection")
     conn.send("finally working".encode())
     msd=str(conn.recv(1024).decode('utf-8'))
     servicemanager.LogInfoMsg(str(msd))
    
     #filtering the recieved message to get ATR and pair information
     _=re.split(r"\x00",msd)[0:-1]
     print(_)
     ATR=round(float(_[0]),4)
     pair=_[1]
     position=_[-1]
     servicemanager.LogInfoMsg(str(ATR)+pair+position)
     t2=threading.Thread(target=trade_manager,args=(pair,ATR,position,))
     t2.start()
     file=open("tradingreport.txt",mode='a+')
     file.write("listening thread:" + str(t2.native_id) + '\n')
     file.close()
     time.sleep(10)
    except:
        servicemanager.LogErrorMsg(traceback.format_exc())
                     

#connects to the metatrader 5 terminal
def terminalconnect(login,password,server):
  try:
      login=login
      password=password
      server=server
      account=mt5.login(login,password,server)
      initialize=mt5.initialize(login=login,password=password,server=server)
      servicemanager.LogInfoMsg(str(initialize))
      return initialize
  except:
        servicemanager.LogErrorMsg(traceback.format_exc())

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
                    
  #step 2:check if price has gone beyond your takeprofit level, then take profit if true
  _=mt5.positions_get(symbol=pair)
  _=re.search("price_open=(\d+\.\d+)",str(_))
  price_in=float(_.group(1))
  takeprofit=price_in+(ATR*1)
  if dparsed>takeprofit:
     exit=mt5.Close(pair,ticket=ticket)
  else:
     limits(dparsed,ATR,ticket,pair,position)
    
#sets the initial limit
def limits(dparsed,ATR,ticket,pair,position):
     file=open("tradingreport.txt",mode='a+')
     if position=="true":
        lastPrice=dparsed
        while True:
           priceNow=mt5.symbol_info(pair).bid
           if priceNow>=lastPrice:
              stoploss=priceNow-(ATR*1.5)
              sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":0.000,
        "position":ticket}
              sl=mt5.order_send(sl_request)
              file.write(str(sl))
              file.close()
              lastPrice=priceNow
              
              
     elif position=="false":
        lastPrice=dparsed
        while True:
           priceNow=mt5.symbol_info(pair).bid
           if priceNow<=lastPrice:
              stoploss=priceNow+(ATR*1.5)
              sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":0.000,
        "position":ticket}
              sl=mt5.order_send(sl_request)
              lastPrice=priceNow
              file.write(str(sl))
              file.close()
              
             
     
#closes the socket connection
def closesocket():
   scHandle=servicemanager.OpenSCManager(None,None,0xF003F)
   serviceHandle=servicemanager.OpenService(scHandle,"SL_TP_EA",
                                            0xF01FF)
   if win32service.CloseServiceHandler(serviceHandle):
      global sock
      sock.close()
      file.close()
      return("socket is closed")
       
        
