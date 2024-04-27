import socket
import MetaTrader5 as mt5
import re,time,pdb,time,threading,sys,os,traceback,subprocess
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
  global login
  login=22334134
  global password
  password="5(jt0MqVowo!"
  global server
  server="Forex.com-Demo 535"
  checkservice()
  #reconnectThread=threading.Thread(target=checkservice,args=())
  #reconnectThread.start()
  createsocket()                                                                                    

def openpositions():
    openTrades=mt5.positions_get()
    for  i in openTrades:
        position=i.type
        if position==1:position="false"
        elif position==0:position="true"
        dparsed=i.price_current
        ticket=i.ticket
        ATR=(i.price_open-i.sl)/1.5
        pair=i.symbol
        servicemanager.LogInfoMsg(str(i))
        tp=0.000
        stoploss=dparsed-(ATR*1.5)
        opThread=threading.Thread(target=limits,args=(dparsed,ATR,ticket,pair,position,))
        opThread.start()
        time.sleep(5)
        
def services():
    try:
        _=subprocess.run('tasklist /FI "IMAGENAME eq terminal64.exe"',check=True,text=True,shell=True,capture_output=True)
        _1=_.stdout.split()
        _2=_1.index("Console")
        try:
            _3=_1.index("Services")
            servicemanager.LogInfoMsg(str(_1[_3-1]))
            _4=_=subprocess.run('taskkill /F /pid '+str(_1[_3-1]),check=True,text=True,shell=True,capture_output=True)
            servicemanager.LogInfoMsg(str(_4))
        except:
            pass
        return _2
    except:
        counter=0
        return counter
def checkservice():
    _list=[None]*2
    
    while True:
        _list.pop(0)
        counter=_list[0]
        _list.append(services())
        servicemanager.LogInfoMsg(str(_list))
        if services():
            if _list[0]!=_list[1]:
                mt5.initialize(login=login,password=password,server=server)
                openpositions()
        else:
            if _list[0]!=_list[1]:
                terminalconnect(login,password,server)
                openpositions()
        time.sleep(10)
        services()
    
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
     time.sleep(1)
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
     if position=="true":
        lastPrice=dparsed
        while True:
           priceNow=mt5.symbol_info(pair).bid
           tp=0.000
           if priceNow>=lastPrice:
              stoploss=priceNow-(ATR*1.5)
              sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":tp,
        "position":ticket}
              sl=mt5.order_send(sl_request)
              file=open('tradingreport.txt',mode='a+')
              file.write('\n' + str(sl) + '\n')
              file.close()
              lastPrice=priceNow
              time.sleep(60)
            
              
              
     elif position=="false":
        lastPrice=dparsed
        while True:
           priceNow=mt5.symbol_info(pair).bid
           tp=priceNow-ATR
           if priceNow<=lastPrice:
              stoploss=priceNow+(ATR*1.5)
              sl_request={"action":mt5.TRADE_ACTION_SLTP,"symbol":pair,"sl":stoploss,"tp":tp,
        "position":ticket}
              sl=mt5.order_send(sl_request)
              lastPrice=priceNow
              file=open('tradingreport.txt',mode='a+')
              file.write('\n' + str(sl) + '\n')
              file.close()
              time.sleep(60)
              
             
     
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
       
        
